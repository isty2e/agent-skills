# Validation (triage) procedure

Modified for security-audit. See [NOTICE](../NOTICE) for licensing and
upstream attribution.

Every candidate passes these steps in order. Stop at the first decisive answer
and record it. A candidate with no decisive answer stays open — it never
defaults to either side.

1. **Reproduce the claim from source.** Re-open the cited lines. If the code
   does not say what the candidate claims, reject with the exact lines.
2. **Hunt counterevidence first.** Before confirming, actively search for what
   defeats it: allowlists, type gates, escaping order, argv lists, loopback
   binds, magic checks, unreachable sinks, self-only impact. Check siblings.
3. **Establish the byte path.** Entry → every transformation → sink, each with
   a location. A hand-waved hop ("the framework handles it") is a proof gap:
   record it as an open question, not a fact.
4. **Name the gain.** The exact new capability (read file X, run code as Y,
   exhaust resource Z). "Compromise" without an object is not established.
5. **Check prerequisites.** Network position, versions, config, user action.
   Unverifiable prerequisites lower confidence; invented ones reject the candidate.
6. **Calibrate** per `references/severity-policy.md`, with rationale and a
   counterexample. Downgrades are mechanical.
7. **Disposition** (the `validation` receipt, `references/receipts.md`):
   `reportable` (validated/hypothesis + residual), `suppressed` or
   `not_applicable` (evidence + reason, kept for re-examination), or
   `deferred` (proof gap + what would close it).

## Proof-gap handling

- Missing deployment evidence (firewall, neighboring services): lowers
  confidence, never kills a source-backed path and never raises severity.
- Untestable sink (another owner's host, shared infra): mark `deferred` and add
  a `coverage.unresolvable` record naming the candidate, the exact test that
  would close it, and why it was not run.
- Re-examination on convergence passes asks only: "was the counterevidence
  really dispositive?" New evidence required to reopen; same reasoning is not
  a new pass.
