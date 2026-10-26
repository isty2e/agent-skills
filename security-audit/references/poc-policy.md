# Proof-of-concept policy

Modified for security-audit. See [NOTICE](../NOTICE) for licensing and
upstream attribution.

PoCs turn a hypothesis into a validated finding or kill it. They also cause
real effects, so they run under these rules — no exceptions. The same rules
cover any execution of target code: builds, tests, imports, debuggers.

## Allowed

- Our own processes in a private scratch directory outside the target:
  `scratch=$(mktemp -d "${XDG_RUNTIME_DIR:-$HOME}/scan-XXXXXX")` (mode 0700).
  Not a fixed name under a shared `/tmp`: other users can read or pre-create
  it. Remove it afterwards.
- Execution only in a disposable copy of the target inside scratch, never in
  the target itself. The copy must not share writable hard links with the
  original. Python runs with `-B` (or `PYTHONDONTWRITEBYTECODE=1`) even in the
  copy; imports otherwise write `__pycache__`.
- Target execution requires an independently configured, verified sandbox:
  - A filesystem/mount allowlist exposes only the disposable copy and approved
    runtime/dependency paths. Runtime mounts are read-only; writable storage
    is limited to private disposable workspace. Do not expose the original
    checkout, host home, agent configuration, credential files or host sockets.
    Never bind an entire home directory just to make an interpreter work.
  - Network access is denied. Environment and inherited descriptors do not
    expose credentials, agents, or connected service sockets.
  - The whole process tree is bounded: a wall-clock limit with forced-kill
    escalation and descendant cleanup, plus total memory and process limits
    sized to what the host can spare. A per-process address-space cap alone
    does not bound a forking workload's total memory.
- Before target execution, verify the actual sandbox configuration with a
  harmless host-side canary outside its allowlist (never create it in the
  target): the sandbox cannot read or overwrite it, but can write an internal
  disposable canary. Verify network denial and the process-tree limits too.
  Preserve the configuration and preflight results as evidence. Recheck after
  any change to mounts, runtime, credentials, networking, or resource policy.
- `env -i`, changing `HOME`, a scratch copy, `python -B`, or `unshare -rn`
  alone is **not** filesystem isolation. A sandbox tool's presence is not
  proof of safe configuration. This skill does not provision a sandbox or
  grant permission to loosen one. If any required control cannot be verified,
  do not execute target code: use static trace and record the exact limitation.
- Use small inputs first and only approved dependencies available in that
  sandbox. Never modify the target or weaken isolation to make a PoC work.

## Forbidden

- Shared infrastructure and other owners' hosts, processes, and files.
  No PoCs against the team server, no stored payloads teammates would execute,
  no probing of neighboring services.
- Using discovered credentials, contacting services to "validate" them, or
  transmitting target code through external tools/services. OSV queries send
  package names and versions only, never source or credentials. The agent's
  model-provider boundary is addressed separately in `SKILL.md`.
- Persistent effects: no new accounts, keys, files outside scratch, or
  configuration changes as a side effect. Clean up and verify.

## Evidence pattern (BMP amplification)

1. Establish the candidate, pinned decoder version and intended observation;
   prepare the crafted input in private scratch.
2. Verify the sandbox and its canaries under the controls above before running
   the target's exact decode pattern (`Image.open(...).convert("RGB")`).
3. Record what actually happened: exit/crash, peak RSS, observed boundary and
   unresolved consequences. A resource limit killing the process is not proof
   of an exploitable crash outside that limit.
4. Retain input, commands, versions, sandbox/preflight evidence, resource limits
   and useful results; remove disposable artifacts and verify cleanup.

A PoC that cannot run under these guards does not run; the candidate stays open
with the exact unrun test recorded.
