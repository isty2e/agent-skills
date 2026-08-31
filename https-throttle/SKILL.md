---
name: https-throttle
description: >-
  Limit aggregate receive bandwidth for proxy-aware HTTPS commands with a rootless authenticated localhost proxy. Use
  for large curl, wget, pip, Git, Python HTTP-client, package-manager, or model downloads when user-level bandwidth
  control is needed and machine-wide QoS is unavailable.
---

# HTTPS Throttle

Run a command through a temporary localhost HTTPS CONNECT proxy that paces aggregate received bytes across concurrent
connections. The implementation targets Linux, requires Bash and Python 3.11 or newer, uses only the Python standard
library, and installs nothing.

## When To Use

Use this skill when all of the following are true:

- the download client honors `HTTPS_PROXY` or can be given an explicit HTTP proxy;
- the traffic uses HTTPS over TCP;
- a user-level aggregate cap is sufficient;
- root privileges or machine-wide traffic control are unavailable or inappropriate.

Do not use it to claim limits for NFS, SSH, SCP, rsync, UDP, QUIC, HTTP/3, uploads, other users, or clients that ignore
proxy configuration. It is not kernel QoS and does not bound instantaneous filesystem writeback.

## Run A Throttled Command

Resolve paths relative to this skill directory, then run:

```bash
scripts/run_throttled.sh --limit-mib-per-sec 10 -- \
  curl -fLO https://example.com/large-file
```

The limit uses MiB/s, where one MiB is 1,048,576 bytes. The wrapper:

1. verifies Python 3.11+;
2. creates an owner-only runtime directory;
3. starts an authenticated proxy on a random `127.0.0.1` port;
4. exports `HTTPS_PROXY`, `https_proxy`, and `HTTPS_THROTTLE_PROXY_URL` only to the child command;
5. unsets `NO_PROXY` and `ALL_PROXY` variants so listed destinations and SOCKS settings do not bypass the proxy;
6. preserves the child exit status and removes the proxy credentials and runtime directory on exit.

Set a runtime parent explicitly when the system temporary filesystem is unsuitable:

```bash
scripts/run_throttled.sh \
  --limit-mib-per-sec 10 \
  --runtime-parent "$HOME/.cache/https-throttle" \
  -- wget https://example.com/large-file
```

`HTTPS_THROTTLE_RUNTIME_DIR` supplies the default runtime parent. Otherwise the wrapper uses `XDG_RUNTIME_DIR`, then
`TMPDIR`, then `/tmp`. `HTTPS_THROTTLE_PYTHON` selects a non-default Python 3.11+ interpreter.

## Client Recipes

Most standard clients use `HTTPS_PROXY` automatically:

```bash
# pip
scripts/run_throttled.sh --limit-mib-per-sec 8 -- \
  python3 -m pip download --dest wheels some-package

# Python requests, urllib, and httpx use proxy environment variables by default.
scripts/run_throttled.sh --limit-mib-per-sec 4 -- \
  python3 download_with_requests.py
```

A client configured with `trust_env=False`, `--no-proxy`, or an equivalent option bypasses this skill. Verify the
client's proxy behavior rather than assuming the process name is sufficient.

Git installations may require explicit Basic proxy authentication configuration:

```bash
scripts/run_throttled.sh --limit-mib-per-sec 10 -- \
  bash -c 'git -c http.proxy="$HTTPS_THROTTLE_PROXY_URL" \
    -c http.proxyAuthMethod=basic clone -- "$1"' bash \
  https://github.com/owner/repository.git
```

For Hugging Face, disable transports that may bypass ordinary proxy behavior and keep worker concurrency bounded:

```bash
scripts/run_throttled.sh --limit-mib-per-sec 10 -- \
  env HF_HUB_DISABLE_XET=1 hf download MODEL_ID --max-workers 1
```

Authentication tokens remain the child command's responsibility. Never print child credentials or the proxy URL.

## Observe And Verify

The proxy writes redacted measurements to stderr every five seconds:

```text
[https-throttle] sample interval=9.98 MiB/s average=9.47 MiB/s total=512.00 MiB active=2
```

`interval` and `average` measure bytes relayed from upstream servers to clients. Small transfers may show a one-chunk
startup burst; the contract is aggregate pacing over the transfer, not a zero-burst instantaneous ceiling.

Run the network-free local tests before modifying the implementation:

```bash
python3 -m unittest discover -s tests -v
```

The tests create two concurrent authenticated CONNECT tunnels to a loopback origin, check their combined rate, verify
mode-600 readiness credentials, preserve a child command's nonzero exit status, and confirm runtime cleanup.

## Security And Operational Boundaries

- The proxy listens only on `127.0.0.1` and accepts only authenticated CONNECT requests.
- Each run generates random Basic proxy credentials and stores them only in a mode-600 readiness file under a mode-700
  runtime directory.
- Logs contain the loopback port and transfer statistics, never the authenticated proxy URL.
- TLS remains end-to-end between the child client and destination; the proxy does not decrypt content or inspect
  application credentials.
- The proxy limits only the receive direction. Uploads are relayed without throttling.
- Multiple clients share one cap only when they use the same proxy process. Separate wrapper invocations have separate
  caps.
- A process that ignores or overrides the proxy can bypass the limit. Use `tc`, cgroup/eBPF policy, or another
  administrator-controlled mechanism when enforcement must cover an interface, machine, container, or uncooperative
  process.
