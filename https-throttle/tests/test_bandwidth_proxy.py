import base64
import os
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

_SKILL_ROOT = Path(__file__).resolve().parents[1]
_PROXY_SCRIPT = _SKILL_ROOT / "scripts" / "bandwidth_proxy.py"
_WRAPPER_SCRIPT = _SKILL_ROOT / "scripts" / "run_throttled.sh"
_MIB = 1024 * 1024


class _QuietFileHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass


class BandwidthProxyTest(unittest.TestCase):
    def test_limits_aggregate_rate_across_authenticated_connect_tunnels(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            payload = directory / "payload.bin"
            payload.write_bytes(b"x" * (2 * _MIB))
            handler = partial(_QuietFileHandler, directory=directory)
            origin = ThreadingHTTPServer(("127.0.0.1", 0), handler)
            origin_thread = threading.Thread(target=origin.serve_forever, daemon=True)
            origin_thread.start()

            ready_file = directory / "proxy-ready"
            proxy = subprocess.Popen(
                [
                    sys.executable,
                    "-I",
                    str(_PROXY_SCRIPT),
                    "--limit-mib-per-sec",
                    "2",
                    "--report-interval-seconds",
                    "0.5",
                    "--ready-file",
                    str(ready_file),
                ],
                stderr=subprocess.PIPE,
                text=True,
            )
            try:
                proxy_url = self._wait_for_proxy(ready_file, proxy)
                self.assertEqual(stat.S_IMODE(ready_file.stat().st_mode), 0o600)
                self._assert_requires_authentication(proxy_url, origin.server_port)
                started_at = time.monotonic()
                with ThreadPoolExecutor(max_workers=2) as executor:
                    responses = list(
                        executor.map(
                            lambda _: self._download_via_proxy(
                                proxy_url,
                                origin.server_port,
                            ),
                            range(2),
                        )
                    )
                elapsed_seconds = time.monotonic() - started_at

                for response in responses:
                    _, _, response_body = response.partition(b"\r\n\r\n")
                    self.assertEqual(len(response_body), 2 * _MIB)
                measured_mib_per_second = 4 / elapsed_seconds
                self.assertGreater(measured_mib_per_second, 1.5)
                self.assertLess(measured_mib_per_second, 2.3)
            finally:
                origin.shutdown()
                origin.server_close()
                proxy.terminate()
                _, proxy_stderr = proxy.communicate(timeout=5)

            self.assertEqual(proxy.returncode, 0, proxy_stderr)
            self.assertIn("[https-throttle] final", proxy_stderr)
            if proxy_url in proxy_stderr:
                raise AssertionError("proxy log exposed the authenticated URL")

    def test_proxy_refuses_to_overwrite_an_existing_ready_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            ready_file = Path(temporary_directory) / "proxy-ready"
            ready_file.write_text("sentinel\n")
            completed = subprocess.run(
                [
                    sys.executable,
                    "-I",
                    str(_PROXY_SCRIPT),
                    "--limit-mib-per-sec",
                    "2",
                    "--ready-file",
                    str(ready_file),
                ],
                text=True,
                capture_output=True,
                check=False,
                timeout=5,
            )

            self.assertNotEqual(completed.returncode, 0)
            self.assertEqual(ready_file.read_text(), "sentinel\n")

    def test_proxy_refuses_to_follow_an_existing_ready_file_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            target = directory / "target"
            target.write_text("sentinel\n")
            ready_file = directory / "proxy-ready"
            ready_file.symlink_to(target)
            completed = subprocess.run(
                [
                    sys.executable,
                    "-I",
                    str(_PROXY_SCRIPT),
                    "--limit-mib-per-sec",
                    "2",
                    "--ready-file",
                    str(ready_file),
                ],
                text=True,
                capture_output=True,
                check=False,
                timeout=5,
            )

            self.assertNotEqual(completed.returncode, 0)
            self.assertTrue(ready_file.is_symlink())
            self.assertEqual(target.read_text(), "sentinel\n")

    def test_proxy_sets_ready_permissions_without_path_chmod(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            ready_file = Path(temporary_directory) / "proxy-ready"
            probe = """
import os
import runpy
import sys
from pathlib import Path

namespace = runpy.run_path(sys.argv[1], run_name="https_throttle_probe")

def reject_path_chmod(*args: object, **kwargs: object) -> None:
    raise AssertionError("ready-file permissions must use the open descriptor")

os.chmod = reject_path_chmod
Path.chmod = reject_path_chmod
namespace["_write_ready_file"](Path(sys.argv[2]), "redacted")
"""
            completed = subprocess.run(
                [
                    sys.executable,
                    "-I",
                    "-c",
                    probe,
                    str(_PROXY_SCRIPT),
                    str(ready_file),
                ],
                text=True,
                capture_output=True,
                check=False,
                timeout=5,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(stat.S_IMODE(ready_file.stat().st_mode), 0o600)
            self.assertEqual(ready_file.read_text(), "redacted\n")

    def test_wrapper_resolves_proxy_when_invoked_through_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            bin_directory = directory / "bin"
            bin_directory.mkdir()
            wrapper_link = bin_directory / "https-throttle"
            wrapper_link.symlink_to(_WRAPPER_SCRIPT)
            runtime_directory = directory / "runtime target"
            runtime_directory.mkdir()
            runtime_link = directory / "runtime-link"
            runtime_link.symlink_to(runtime_directory, target_is_directory=True)
            environment = os.environ.copy()
            environment["HTTPS_THROTTLE_PYTHON"] = sys.executable
            completed = subprocess.run(
                [
                    "bash",
                    str(wrapper_link),
                    "--limit-mib-per-sec",
                    "2",
                    "--runtime-parent",
                    str(runtime_link),
                    "--",
                    sys.executable,
                    "-I",
                    "-c",
                    "pass",
                ],
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(list(runtime_directory.iterdir()), [])
            self.assertIn("[https-throttle] final", completed.stderr)

    def test_wrapper_preserves_child_exit_and_removes_runtime_credentials(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            runtime_parent = Path(temporary_directory)
            child_code = """
import os
from urllib.parse import urlsplit

upper = os.environ["HTTPS_PROXY"]
lower = os.environ["https_proxy"]
explicit = os.environ["HTTPS_THROTTLE_PROXY_URL"]
assert upper == lower == explicit
parsed = urlsplit(upper)
assert parsed.hostname == "127.0.0.1"
assert parsed.username == "bandwidth"
assert parsed.password
assert "NO_PROXY" not in os.environ
assert "no_proxy" not in os.environ
assert "ALL_PROXY" not in os.environ
assert "all_proxy" not in os.environ
raise SystemExit(23)
"""
            environment = os.environ.copy()
            environment["HTTPS_THROTTLE_PYTHON"] = sys.executable
            completed = subprocess.run(
                [
                    "bash",
                    str(_WRAPPER_SCRIPT),
                    "--limit-mib-per-sec",
                    "2",
                    "--runtime-parent",
                    str(runtime_parent),
                    "--",
                    sys.executable,
                    "-I",
                    "-c",
                    child_code,
                ],
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 23, completed.stderr)
            self.assertEqual(list(runtime_parent.iterdir()), [])
            self.assertIn("[https-throttle] final", completed.stderr)
            self.assertNotIn("bandwidth:", completed.stderr)

    def test_wrapper_terminates_child_and_cleans_runtime_on_signal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            runtime_parent = directory / "runtime"
            runtime_parent.mkdir()
            child_ready = directory / "child-ready"
            environment = os.environ.copy()
            environment["HTTPS_THROTTLE_PYTHON"] = sys.executable
            child_code = """
import signal
import sys
import time
from pathlib import Path

signal.signal(signal.SIGTERM, signal.SIG_IGN)
Path(sys.argv[1]).write_text("ready")
time.sleep(30)
"""
            wrapper = subprocess.Popen(
                [
                    "bash",
                    str(_WRAPPER_SCRIPT),
                    "--limit-mib-per-sec",
                    "2",
                    "--runtime-parent",
                    str(runtime_parent),
                    "--",
                    sys.executable,
                    "-I",
                    "-c",
                    child_code,
                    str(child_ready),
                ],
                env=environment,
                stderr=subprocess.PIPE,
                text=True,
            )
            self._wait_for_path(child_ready, wrapper)
            wrapper.terminate()
            _, wrapper_stderr = wrapper.communicate(timeout=5)

            self.assertEqual(wrapper.returncode, 143, wrapper_stderr)
            self.assertEqual(list(runtime_parent.iterdir()), [])
            self.assertIn("[https-throttle] final", wrapper_stderr)

    @classmethod
    def _assert_requires_authentication(cls, proxy_url: str, origin_port: int) -> None:
        parsed_proxy_url = urlsplit(proxy_url)
        if parsed_proxy_url.hostname is None or parsed_proxy_url.port is None:
            raise AssertionError("invalid authenticated proxy URL")
        with socket.create_connection(
            (parsed_proxy_url.hostname, parsed_proxy_url.port)
        ) as client:
            client.sendall(f"CONNECT 127.0.0.1:{origin_port} HTTP/1.1\r\n\r\n".encode())
            response = cls._receive_headers(client)
        if b"407 Proxy Authentication Required" not in response:
            raise AssertionError(response)
        if b'Proxy-Authenticate: Basic realm="https-throttle"' not in response:
            raise AssertionError(response)

    @classmethod
    def _download_via_proxy(cls, proxy_url: str, origin_port: int) -> bytes:
        parsed_proxy_url = urlsplit(proxy_url)
        if parsed_proxy_url.hostname is None or parsed_proxy_url.port is None:
            raise AssertionError("invalid authenticated proxy URL")
        credentials = base64.b64encode(
            f"{parsed_proxy_url.username}:{parsed_proxy_url.password}".encode()
        ).decode()
        with socket.create_connection(
            (parsed_proxy_url.hostname, parsed_proxy_url.port)
        ) as client:
            client.sendall(
                (
                    f"CONNECT 127.0.0.1:{origin_port} HTTP/1.1\r\n"
                    f"Proxy-Authorization: Basic {credentials}\r\n\r\n"
                ).encode()
            )
            connect_response = cls._receive_headers(client)
            if b"200 Connection Established" not in connect_response:
                raise AssertionError(connect_response)
            client.sendall(b"GET /payload.bin HTTP/1.0\r\nHost: localhost\r\n\r\n")
            return cls._receive_all(client)

    @staticmethod
    def _wait_for_proxy(ready_file: Path, proxy: subprocess.Popen[str]) -> str:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if ready_file.exists():
                return ready_file.read_text().strip()
            if proxy.poll() is not None:
                _, proxy_stderr = proxy.communicate()
                raise AssertionError(f"proxy exited before readiness: {proxy_stderr}")
            time.sleep(0.05)
        raise AssertionError("proxy readiness timed out")

    @staticmethod
    def _wait_for_path(path: Path, process: subprocess.Popen[str]) -> None:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if path.exists():
                return
            if process.poll() is not None:
                _, process_stderr = process.communicate()
                raise AssertionError(
                    f"process exited before readiness: {process_stderr}"
                )
            time.sleep(0.05)
        raise AssertionError(f"readiness timed out: {path}")

    @staticmethod
    def _receive_headers(client: socket.socket) -> bytes:
        response = bytearray()
        while b"\r\n\r\n" not in response:
            response.extend(client.recv(4096))
        return bytes(response)

    @staticmethod
    def _receive_all(client: socket.socket) -> bytes:
        response = bytearray()
        while chunk := client.recv(64 * 1024):
            response.extend(chunk)
        return bytes(response)


if __name__ == "__main__":
    unittest.main()
