"""Run a localhost CONNECT proxy with an aggregate receive-rate limit."""

import argparse
import asyncio
import base64
import contextlib
import hmac
import os
import secrets
import signal
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

_MIB = 1024 * 1024
_MAX_HEADER_BYTES = 64 * 1024
_RELAY_CHUNK_BYTES = 64 * 1024


@dataclass(frozen=True)
class _ProxyOptions:
    limit_bytes_per_second: int
    report_interval_seconds: float
    ready_file: Path


class _BandwidthLimiter:
    def __init__(self, bytes_per_second: int) -> None:
        self._bytes_per_second = bytes_per_second
        self._next_send_at = 0.0
        self._lock = asyncio.Lock()

    async def wait(self, byte_count: int) -> None:
        async with self._lock:
            loop = asyncio.get_running_loop()
            now = loop.time()
            send_at = max(now, self._next_send_at)
            self._next_send_at = send_at + byte_count / self._bytes_per_second

        delay = send_at - now
        if delay > 0:
            await asyncio.sleep(delay)


class _TransferMeter:
    def __init__(self, report_interval_seconds: float) -> None:
        loop = asyncio.get_running_loop()
        self._report_interval_seconds = report_interval_seconds
        self._started_at = loop.time()
        self._last_report_at = self._started_at
        self._last_report_bytes = 0
        self._total_bytes = 0
        self._active_connections = 0

    def connection_opened(self) -> None:
        self._active_connections += 1

    def connection_closed(self) -> None:
        self._active_connections -= 1

    def record(self, byte_count: int) -> None:
        self._total_bytes += byte_count

    def report(self, *, final: bool = False) -> None:
        now = asyncio.get_running_loop().time()
        interval_seconds = max(now - self._last_report_at, 1e-9)
        elapsed_seconds = max(now - self._started_at, 1e-9)
        interval_bytes = self._total_bytes - self._last_report_bytes
        interval_rate = interval_bytes / interval_seconds / _MIB
        average_rate = self._total_bytes / elapsed_seconds / _MIB
        label = "final" if final else "sample"
        print(
            f"[https-throttle] {label} interval={interval_rate:.2f} MiB/s "
            f"average={average_rate:.2f} MiB/s "
            f"total={self._total_bytes / _MIB:.2f} MiB "
            f"active={self._active_connections}",
            file=sys.stderr,
            flush=True,
        )
        self._last_report_at = now
        self._last_report_bytes = self._total_bytes

    async def report_periodically(self) -> None:
        while True:
            await asyncio.sleep(self._report_interval_seconds)
            self.report()


def _parse_connect_target(target: str) -> tuple[str, int]:
    if target.startswith("["):
        closing_bracket = target.find("]")
        if (
            closing_bracket < 0
            or target[closing_bracket + 1 : closing_bracket + 2] != ":"
        ):
            raise ValueError("invalid IPv6 CONNECT target")
        host = target[1:closing_bracket]
        port_text = target[closing_bracket + 2 :]
    else:
        host, separator, port_text = target.rpartition(":")
        if not separator:
            raise ValueError("CONNECT target must include a port")

    if not host or not port_text.isdecimal():
        raise ValueError("invalid CONNECT target")
    port = int(port_text)
    if not 1 <= port <= 65535:
        raise ValueError("CONNECT port is out of range")
    return host, port


async def _read_connect_target(
    reader: asyncio.StreamReader,
    expected_proxy_authorization: str,
) -> tuple[str, int]:
    try:
        request = await asyncio.wait_for(
            reader.readuntil(b"\r\n\r\n"),
            timeout=10,
        )
    except (
        asyncio.IncompleteReadError,
        asyncio.LimitOverrunError,
        TimeoutError,
    ) as error:
        raise ValueError("invalid proxy request") from error

    if len(request) > _MAX_HEADER_BYTES:
        raise ValueError("proxy request headers are too large")
    header_lines = request.split(b"\r\n")
    request_line = header_lines[0].decode("ascii", errors="replace")
    fields = request_line.split()
    if len(fields) != 3:
        raise ValueError("invalid proxy request line")
    method, target, _ = fields
    if method != "CONNECT":
        raise PermissionError("only CONNECT requests are supported")

    proxy_authorization = ""
    for header_line in header_lines[1:]:
        name, separator, value = header_line.partition(b":")
        if separator and name.strip().lower() == b"proxy-authorization":
            proxy_authorization = value.strip().decode("ascii", errors="replace")
            break
    if not hmac.compare_digest(proxy_authorization, expected_proxy_authorization):
        raise PermissionError("proxy authentication failed")
    return _parse_connect_target(target)


async def _send_proxy_response(
    writer: asyncio.StreamWriter,
    status: str,
) -> None:
    headers = ""
    if status.startswith("407 "):
        headers = 'Proxy-Authenticate: Basic realm="https-throttle"\r\n'
    if not status.startswith("200 "):
        headers += "Connection: close\r\n"
    writer.write(f"HTTP/1.1 {status}\r\n{headers}\r\n".encode())
    await writer.drain()


async def _copy_stream(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    *,
    limiter: _BandwidthLimiter | None = None,
    meter: _TransferMeter | None = None,
) -> None:
    while data := await reader.read(_RELAY_CHUNK_BYTES):
        if limiter is not None:
            await limiter.wait(len(data))
        writer.write(data)
        await writer.drain()
        if meter is not None:
            meter.record(len(data))


async def _relay_bidirectionally(
    client_reader: asyncio.StreamReader,
    client_writer: asyncio.StreamWriter,
    upstream_reader: asyncio.StreamReader,
    upstream_writer: asyncio.StreamWriter,
    limiter: _BandwidthLimiter,
    meter: _TransferMeter,
) -> None:
    upload_task = asyncio.create_task(_copy_stream(client_reader, upstream_writer))
    download_task = asyncio.create_task(
        _copy_stream(
            upstream_reader,
            client_writer,
            limiter=limiter,
            meter=meter,
        )
    )
    tasks = {upload_task, download_task}
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    for task in pending:
        task.cancel()
    await asyncio.gather(*pending, return_exceptions=True)
    for task in done:
        task.result()


async def _close_writer(writer: asyncio.StreamWriter) -> None:
    writer.close()
    with contextlib.suppress(ConnectionError, OSError):
        await writer.wait_closed()


async def _handle_client(
    client_reader: asyncio.StreamReader,
    client_writer: asyncio.StreamWriter,
    limiter: _BandwidthLimiter,
    meter: _TransferMeter,
    expected_proxy_authorization: str,
) -> None:
    upstream_writer: asyncio.StreamWriter | None = None
    meter.connection_opened()
    try:
        try:
            host, port = await _read_connect_target(
                client_reader,
                expected_proxy_authorization,
            )
        except PermissionError:
            await _send_proxy_response(
                client_writer,
                "407 Proxy Authentication Required",
            )
            return
        except ValueError:
            await _send_proxy_response(client_writer, "400 Bad Request")
            return

        try:
            upstream_reader, upstream_writer = await asyncio.open_connection(host, port)
        except OSError:
            await _send_proxy_response(client_writer, "502 Bad Gateway")
            return

        await _send_proxy_response(client_writer, "200 Connection Established")
        await _relay_bidirectionally(
            client_reader,
            client_writer,
            upstream_reader,
            upstream_writer,
            limiter,
            meter,
        )
    except (ConnectionError, OSError):
        pass
    finally:
        meter.connection_closed()
        if upstream_writer is not None:
            await _close_writer(upstream_writer)
        await _close_writer(client_writer)


def _write_ready_file(path: Path, proxy_url: str) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(path, flags, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        os.fchmod(handle.fileno(), 0o600)
        handle.write(f"{proxy_url}\n")


async def _serve(options: _ProxyOptions) -> None:
    limiter = _BandwidthLimiter(options.limit_bytes_per_second)
    meter = _TransferMeter(options.report_interval_seconds)
    connection_tasks: set[asyncio.Task[None]] = set()
    proxy_username = "bandwidth"
    proxy_password = secrets.token_urlsafe(24)
    encoded_credentials = base64.b64encode(
        f"{proxy_username}:{proxy_password}".encode()
    ).decode()
    expected_proxy_authorization = f"Basic {encoded_credentials}"

    def start_connection(
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        task = asyncio.create_task(
            _handle_client(
                reader,
                writer,
                limiter,
                meter,
                expected_proxy_authorization,
            )
        )
        connection_tasks.add(task)
        task.add_done_callback(connection_tasks.discard)

    server = await asyncio.start_server(
        start_connection,
        host="127.0.0.1",
        port=0,
        limit=_MAX_HEADER_BYTES,
    )
    socket = server.sockets[0]
    port = socket.getsockname()[1]
    proxy_url = f"http://{proxy_username}:{proxy_password}@127.0.0.1:{port}"
    try:
        _write_ready_file(options.ready_file, proxy_url)
    except OSError:
        server.close()
        await server.wait_closed()
        raise
    print(
        f"[https-throttle] listening=http://127.0.0.1:{port} "
        f"limit={options.limit_bytes_per_second / _MIB:.2f} MiB/s",
        file=sys.stderr,
        flush=True,
    )

    shutdown = asyncio.Event()
    loop = asyncio.get_running_loop()
    for shutdown_signal in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(shutdown_signal, shutdown.set)

    reporter = asyncio.create_task(meter.report_periodically())
    try:
        await shutdown.wait()
    finally:
        server.close()
        await server.wait_closed()
        for task in connection_tasks:
            task.cancel()
        await asyncio.gather(*connection_tasks, return_exceptions=True)
        reporter.cancel()
        await asyncio.gather(reporter, return_exceptions=True)
        meter.report(final=True)


def _parse_args(argv: Sequence[str] | None = None) -> _ProxyOptions:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit-mib-per-sec", type=int, required=True)
    parser.add_argument("--report-interval-seconds", type=float, default=5.0)
    parser.add_argument("--ready-file", type=Path, required=True)
    namespace = parser.parse_args(argv)
    if namespace.limit_mib_per_sec <= 0:
        parser.error("--limit-mib-per-sec must be positive")
    if namespace.report_interval_seconds <= 0:
        parser.error("--report-interval-seconds must be positive")
    if not namespace.ready_file.parent.is_dir():
        parser.error("--ready-file parent directory must exist")
    return _ProxyOptions(
        limit_bytes_per_second=namespace.limit_mib_per_sec * _MIB,
        report_interval_seconds=namespace.report_interval_seconds,
        ready_file=namespace.ready_file,
    )


def main(argv: Sequence[str] | None = None) -> None:
    """Run the bandwidth-limited proxy until interrupted.

    Parameters
    ----------
    argv
        Command-line arguments excluding the executable name. The process command
        line is used when omitted.

    Returns
    -------
    None
    """
    asyncio.run(_serve(_parse_args(argv)))


if __name__ == "__main__":
    main()
