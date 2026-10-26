# Severity policy (adapted from the reference method)

Modified for security-audit. See [NOTICE](../NOTICE) for licensing and
upstream attribution.

Calibrate only after scope, reachability, and counterevidence are established.
Then apply this matrix mechanically — do not re-argue severity afterwards.
The matrix below matches upstream openai/codex-security
(`attack-path-analysis/references/severity-policy.md`); `scripts/scan-gate.py`
recomputes it for every finding.

## Bars

- `critical` demands: clear exploit path + major impact obvious enough that no
  long speculative argument is needed. Non-exhaustive qualifiers: credible RCE,
  XSS with proven session/token/account impact, 0-click account takeover,
  trivial auth bypass/IDOR, severe secret leak with realistic access, trivial
  memory-corruption exploits, SQLi with proven path + impact, sandbox/VM escape,
  SSTI-to-RCE with proof, arbitrary file write with realistic persistence path,
  integrity destruction at scale with proof.
- `high` demands: realistic in-scope attacker path + major impact, no long
  speculative chain. Qualifiers: SSRF **with proof** of reachable
  internal/metadata/side-effecting targets (an intended webhook feature is not
  suppression evidence, but neither is it impact proof); exploitable memory
  corruption; file read reaching secrets; CSRF on credential/billing/security
  actions with realistic victim behavior; valid hardcoded credentials; crypto
  forgery with practical proof; supply-chain compromise with real impact;
  XXE with controlled document + vulnerable engine; stored active content via
  upload **with proof** of both upload and access reachability.
- Strength toward `critical`: unauthenticated/broad reach, 0-click,
  cross-tenant impact, identity/control-plane credential compromise,
  persistence or mass exploitation, proven code execution or secret access.
- Never `high`/`critical` on: correctness bugs alone; unclear attacker value;
  internal-only defects without reachability; already-privileged attackers
  (unless the escalation delta is the finding); "chainable with assumptions";
  self-XSS without a victim; injection claims without demonstrated control or
  sink; transient/single-user/self-targeting DoS; open redirect, version
  banners, stack traces, or missing headers outside a real chain; theoretical
  memory corruption; headers/TLS hygiene without an exploit path.

## Suppression (hard, before rating)

- Self-only impact → `ignore`. Unachievable/unrealistic preconditions → `ignore`.
- Privileged/operator/developer/physical-only preconditions → `ignore`, unless
  the escalation delta itself is the issue.
- Real bug but not a security problem in context → `ignore` (or `low`).

## Likelihood by network scope

`remote` → usually high; `local_network` → usually medium; `localhost` →
usually low (unless a lower-privileged local attacker realistically reaches
it); `none` → no exposure lift. Internal exposure reduces likelihood or
confidence; it does not force `ignore` when a real control regression exists.

## Matrix (impact × likelihood)

- high × high → `critical` only if the bars above hold, else `high`
- high × medium → `medium`; high × low → `low`; high × unknown → `medium`
- medium × high → `medium`; medium × {medium, low} → `low`; medium × unknown → `low`
- low × anything non-ignore → `low`
- ignore × any → `ignore`; any × ignore → `ignore`
- unknown × high → `medium`; unknown × {medium, low, unknown} → `low`

Priority: critical→P0, high→P1, medium→P2, low→P3. No priority for `ignore`.

## Worked calibrations (recomputed under this matrix)

- Pillow BMP amplification (validated PoC, LAN, shared-service RAM exhaustion):
  impact medium (availability, bounds-safe) × likelihood medium
  (local_network) → **Low (P3)**. Proof of internet exposure would raise
  likelihood to high → Medium.
- Team-server SSRF (primitive confirmed, no listener inventory): impact medium
  (unproven internal targets — per the bars, no `high` without that proof) ×
  likelihood medium → **Low (P3)**. Residual: an inventory of the server host's
  listeners showing a reachable internal or side-effecting target would raise
  impact to high → Medium.
- Stored XSS via publish (allowlist + escape-first rendering, unfuzzed):
  impact medium (script exec unproven at session-theft level) × likelihood
  unknown → **Low (P3)**. Proven script execution in a victim session would
  raise impact to high → Medium even with unknown likelihood.
- Attribution forgery: impact low → **Low (P3)**.
- Prompt-injection tool execution (blocked + canary-verified): self-only
  residual at most → mitigated watch, no finding.
