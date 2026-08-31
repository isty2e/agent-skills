---
name: https-throttle
description: >-
  Limit aggregate receive bandwidth for proxy-aware HTTPS commands with a rootless authenticated localhost proxy. Use
  for large curl, wget, pip, Git, Python HTTP-client, package-manager, or model downloads when user-level bandwidth
  control is needed and machine-wide QoS is unavailable.
---

# HTTPS Throttle

Run a command through a temporary localhost CONNECT proxy that paces aggregate received bytes across concurrent HTTPS
connections. It targets Linux, requires Bash and Python 3.11+, uses only the Python standard library, and installs
nothing.

## When To Use

Use this skill only when the client honors `HTTPS_PROXY` or an explicit HTTP proxy, the traffic is HTTPS over TCP, a
user-level aggregate cap is sufficient, and machine-wide control is unavailable or inappropriate.

It does not control NFS, SSH/SCP, rsync, UDP, QUIC/HTTP/3, uploads, other users, or proxy-bypassing clients. It is not
kernel QoS and does not bound instantaneous filesystem writeback.

## Run A Throttled Command

Resolve paths relative to this skill directory:

```bash
scripts/run_throttled.sh --limit-mib-per-sec 10 -- \
  curl -fLO https://example.com/large-file
```

Limits use MiB/s (1 MiB = 1,048,576 bytes). The wrapper starts a randomly authenticated `127.0.0.1` proxy, scopes proxy
environment variables to the child, clears `NO_PROXY` and `ALL_PROXY` variants, preserves the child exit status, and
removes credentials and its runtime directory on exit.

Use `--runtime-parent DIR` when the default temporary filesystem is unsuitable. The default lookup is
`HTTPS_THROTTLE_RUNTIME_DIR`, `XDG_RUNTIME_DIR`, `TMPDIR`, then `/tmp`. Set `HTTPS_THROTTLE_PYTHON` to select another
Python 3.11+ interpreter.

## Client-Specific Configuration

`curl`, `wget`, `pip`, `requests`, `urllib`, and `httpx` normally honor the injected proxy environment. Options such as
`--no-proxy` or `trust_env=False` bypass the limit.

Git may require its authenticated proxy to be explicit:

```bash
scripts/run_throttled.sh --limit-mib-per-sec 10 -- \
  bash -c 'git -c http.proxy="$HTTPS_THROTTLE_PROXY_URL" \
    -c http.proxyAuthMethod=basic clone -- "$1"' bash \
  https://github.com/owner/repository.git
```

For Hugging Face, disable Xet and keep worker concurrency bounded:

```bash
scripts/run_throttled.sh --limit-mib-per-sec 10 -- \
  env HF_HUB_DISABLE_XET=1 hf download MODEL_ID --max-workers 1
```

Child authentication remains the caller's responsibility. Never print child credentials or
`HTTPS_THROTTLE_PROXY_URL`.

## Observe And Verify

The proxy writes redacted interval, average, total-byte, and active-connection measurements to stderr every five
seconds. They measure upstream-to-client relayed bytes. Small transfers may show a one-chunk startup burst; the contract
is aggregate transfer pacing, not a zero-burst instantaneous ceiling.

Run the network-free tests after implementation changes:

```bash
python3 -m unittest discover -s tests -v
```

They cover aggregate pacing across concurrent authenticated tunnels, readiness-file permissions, exit propagation,
signal handling, and runtime cleanup.

## Security And Enforcement Boundaries

- The proxy accepts authenticated CONNECT requests only on `127.0.0.1`; each run stores random Basic credentials in a
  mode-600 readiness file under a mode-700 runtime directory.
- Logs exclude the authenticated proxy URL. TLS remains end-to-end; the proxy does not decrypt content or inspect
  application credentials.
- Only downloads through one proxy process share its receive cap. Uploads are relayed without throttling.
- Uncooperative clients can bypass this user-level control. Use `tc`, cgroup/eBPF policy, or another administrator-owned
  mechanism for interface-, machine-, container-, or process-level enforcement.
