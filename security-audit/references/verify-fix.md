# Verify a fix

Modified for security-audit. See [NOTICE](../NOTICE) for licensing and
upstream attribution.

Invoked only when asked to verify that a fix closes a specific finding. Do not
modify the repository.

## Inputs

The original finding (from `findings.json` or supplied), the target checkout,
and the mode: `standard` (may run the reproducer and tests, read-only) or
`static` (source reading only). Default `standard`.

## Method

1. Restate the original vulnerability: attacker-controlled source, broken
   control, sink, boundary crossed, preconditions, and the legitimate behavior
   that must keep working.
2. Confirm the affected component still exists in the checkout. Follow moved or
   refactored code; a missing file, renamed function, or deleted line is not
   proof of remediation.
3. Trace the original path through the current implementation. Check the
   nearest control, equivalent paths (siblings, alternate encodings, aliases),
   and plausible bypasses the fix might have left open.
4. In `standard` mode, run the original reproducer, a focused regression check,
   and one legitimate-behavior check, without modifying the repository. Under
   the PoC guards (`references/poc-policy.md`).
5. In `static` mode, cite the source evidence for each gate and state that
   runtime checks were not performed; do not count them as passed.

## Result contract

One result per finding, in the requested order:

```json
{"results": [{"id": "...", "status": "fixed|still_vulnerable|inconclusive",
              "evidence": "specific source, exploit, test, or proof-gap evidence"}]}
```

- `fixed`: evidence proves the boundary is closed and legitimate behavior
  remains intact.
- `still_vulnerable`: evidence proves the original path remains reachable.
- `inconclusive`: repository mismatch, missing original context, unavailable
  required checks, or any other material proof gap.

Never infer a stronger verdict by weakening the read-only boundary,
substituting a different vulnerability, or hiding missing evidence. Closed
tickets, unrelated green tests, and the absence of a new scan finding are not
proof.
