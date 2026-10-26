# Finding detail fields (adapted)

Modified for security-audit. See [NOTICE](../NOTICE) for licensing and
upstream attribution.

Every reportable finding carries one shared `codeEvidence` catalog; prose
sections reference it by id instead of pasting code. Roles, in dataflow order:

`user_input` → `entrypoint` → `propagation`* → `root_control` → `sink` →
`outcome`, plus `expected_control` (a nearby correct check, supporting context,
never a stack step).

## Writing rules

- Keep code out of prose. Snippets live in `codeEvidence[].code`; explanations
  say what the snippet proves and where the value goes next.
- Each explanation is connective: name the attacker-controlled value at this
  step, the callee/state receiving it, and why the lines preserve or violate
  the invariant. No location-only filler ("tied to the broken control at X").
- `rootCause.summary` is a walkthrough (input → calls → missing control →
  dangerous op → later consumer), not a verdict.
- `validation` states method, summary, `assertions` (each falsifiable), and
  `limitations`. Unknowns go here, not into severity.
- `attackPath` is concise: realistic boundary, minimum trigger sequence,
  concrete outcome. Full narrative stays out.
- `remediation` is one invariant string; `remediationTests` and
  `preventiveControls` are arrays with one test/control per entry.
- Populate only evidence-backed fields. Omit unknowns instead of placeholders.

## Evidence item

`id` (stable), `label`, `path`, `startLine` (+`endLine`), `language`, `role`,
`code` (smallest useful snippet), `explanation`. `rootCause.evidenceRefs`,
`validation.evidenceRefs`, and `attackPath.dataflow.evidenceRefs` must all
resolve against this catalog — `scripts/scan-gate.py check` enforces it.
