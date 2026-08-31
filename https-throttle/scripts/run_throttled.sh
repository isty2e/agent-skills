#!/usr/bin/env bash

set -euo pipefail
umask 077

if ! SCRIPT_PATH="$(readlink -f -- "${BASH_SOURCE[0]}")"; then
    echo "[https-throttle] could not resolve the wrapper path" >&2
    exit 2
fi
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)"
PYTHON_BIN="${HTTPS_THROTTLE_PYTHON:-python3}"
RUNTIME_PARENT="${HTTPS_THROTTLE_RUNTIME_DIR:-${XDG_RUNTIME_DIR:-${TMPDIR:-/tmp}}}"
LIMIT_MIB_PER_SEC=""
PROXY_PID=""
CHILD_PID=""
RUNTIME_DIR=""

usage() {
    cat >&2 <<'EOF'
usage: run_throttled.sh --limit-mib-per-sec N [--runtime-parent DIR] -- COMMAND [ARG ...]

Run a proxy-aware HTTPS command through one authenticated localhost proxy whose
aggregate receive rate is limited to N MiB/s. Requires Linux, Bash, and Python 3.11+.
EOF
}

terminate_pid() {
    local pid="$1"
    local attempt
    if ! kill -0 "$pid" 2>/dev/null; then
        return
    fi
    kill -TERM "$pid" 2>/dev/null || true
    for attempt in {1..20}; do
        if ! kill -0 "$pid" 2>/dev/null; then
            break
        fi
        sleep 0.1
    done
    if kill -0 "$pid" 2>/dev/null; then
        kill -KILL "$pid" 2>/dev/null || true
    fi
    wait "$pid" 2>/dev/null || true
}

cleanup() {
    local exit_code=$?
    trap - EXIT INT TERM HUP
    set +e
    if [[ -n "$CHILD_PID" ]]; then
        terminate_pid "$CHILD_PID"
    fi
    if [[ -n "$PROXY_PID" ]]; then
        terminate_pid "$PROXY_PID"
    fi
    if [[ -n "$RUNTIME_DIR" ]]; then
        rm -rf -- "$RUNTIME_DIR"
    fi
    exit "$exit_code"
}

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
trap 'exit 129' HUP

while (( $# > 0 )); do
    case "$1" in
        --limit-mib-per-sec)
            if (( $# < 2 )); then
                usage
                exit 2
            fi
            LIMIT_MIB_PER_SEC="$2"
            shift 2
            ;;
        --runtime-parent)
            if (( $# < 2 )); then
                usage
                exit 2
            fi
            RUNTIME_PARENT="$2"
            shift 2
            ;;
        --)
            shift
            break
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            usage
            exit 2
            ;;
    esac
done

if [[ ! "$LIMIT_MIB_PER_SEC" =~ ^[1-9][0-9]*$ ]] || (( $# == 0 )); then
    usage
    exit 2
fi
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "[https-throttle] Python interpreter not found: $PYTHON_BIN" >&2
    exit 2
fi
if ! "$PYTHON_BIN" -I -c 'import sys; raise SystemExit(sys.version_info < (3, 11))'; then
    echo "[https-throttle] Python 3.11 or newer is required" >&2
    exit 2
fi

mkdir -p -- "$RUNTIME_PARENT"
RUNTIME_PARENT="$(cd -- "$RUNTIME_PARENT" && pwd -P)"
RUNTIME_DIR="$(mktemp -d -- "$RUNTIME_PARENT/https-throttle.XXXXXX")"
chmod 700 "$RUNTIME_DIR"
READY_FILE="$RUNTIME_DIR/ready"

"$PYTHON_BIN" -I -u "$SCRIPT_DIR/bandwidth_proxy.py" \
    --limit-mib-per-sec "$LIMIT_MIB_PER_SEC" \
    --ready-file "$READY_FILE" &
PROXY_PID=$!

for _ in {1..100}; do
    if [[ -s "$READY_FILE" ]]; then
        break
    fi
    if ! kill -0 "$PROXY_PID" 2>/dev/null; then
        wait "$PROXY_PID" || true
        echo "[https-throttle] proxy exited before readiness" >&2
        exit 2
    fi
    sleep 0.05
done
if [[ ! -s "$READY_FILE" ]]; then
    echo "[https-throttle] proxy readiness timed out" >&2
    exit 2
fi

PROXY_URL="$(<"$READY_FILE")"
(
    export HTTPS_PROXY="$PROXY_URL"
    export https_proxy="$PROXY_URL"
    export HTTPS_THROTTLE_PROXY_URL="$PROXY_URL"
    unset ALL_PROXY all_proxy NO_PROXY no_proxy
    exec "$@"
) &
CHILD_PID=$!

set +e
wait "$CHILD_PID"
child_exit_code=$?
set -e
CHILD_PID=""
exit "$child_exit_code"
