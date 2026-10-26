# Scan state files

Modified for security-audit. See [NOTICE](../NOTICE) for licensing and
upstream attribution.

Each file in `<scan-dir>` has one schema; the schema is the shape, this page is
the meaning. `scripts/scan-gate.py check` validates every file and the rules
that span them. `examples/scan/` is a complete scan that passes the gate.

The JSON Schema `$id` values retain the `local-security-scan/` namespace as
stable identifiers. The installed skill is named `security-audit`; renaming
it does not change the scan-state formats.

| File | Schema | Written by |
|---|---|---|
| `inventory.json` | `schemas/inventory.schema.json` | `scan-gate.py inventory` only |
| `coverage.json` | `schemas/coverage.schema.json` | parent (`references/receipts.md`) |
| `candidates.json` | `schemas/candidates.schema.json` | parent (`references/receipts.md`) |
| `findings.json` | `schemas/findings.schema.json` | parent (this page) |
| `scan-state.json` | `schemas/scan-state.schema.json` | parent (`references/convergence.md`) |

Inventory and coverage both require `snapshot_digest`; its source identity,
attestation, and legacy-state rules are defined in `references/scope.md`.

## findings.json

`target`, `passes` (equals the number of passes in `scan-state.json`),
`findings` (reportable), `non_findings` (rejected). Every id in either list is a
candidate in `candidates.json`, and every reportable or rejected candidate
appears in exactly one of them.

### finding

Identity and triage: `id` (`sink-short-rule`), `title`, `cwe` (`CWE-<n>`),
`severity` + `severity_rationale` (with counterexample), `confidence` + what
would raise it, `attacker` (capabilities present and absent), `status`
(`hypothesis`/`validated`).

Evidence catalog: `codeEvidence[]` — `id`, `label`, `path`, `startLine`
(+`endLine`, `language`), `role` (one of `user_input`, `entrypoint`,
`propagation`, `root_control`, `sink`, `outcome`, `expected_control`), `code`,
`explanation`. Writing rules: `references/finding-details.md`.

Reasoning blocks (reference catalog ids, never paste code):
- `rootCause`: `summary` (walkthrough) + `evidenceRefs` ordered input→outcome.
- `validation`: `method`, `summary`, `evidenceRefs`, `assertions[]`,
  `limitations[]`.
- `attackPath`: `summary` (minimum trigger sequence), `dataflow` (source,
  sink, outcome + `evidenceRefs`), `reachability` (attacker, entrypoint,
  outcome), `impact` and `likelihood` (level + why), `vector`, `authScope`,
  `crossBoundary`, `blindspots[]`, `policyDecision` (always `report` here).
- Context kept flat for grepability: `entry`, `sink`, `dataflow` (one-line),
  `control`, `impact`, `prerequisites`, `counterevidence`.

`severity` must equal the matrix result for `attackPath.impact.level` ×
`attackPath.likelihood.level` (`references/severity-policy.md`) and the
candidate's `attack_path.severity`; a matrix result of `ignore` belongs in
`non_findings`.

Fix: `remediation` (one invariant string), `remediationTests[]`,
`preventiveControls[]` (one test/control per entry).

### rejected (non-finding)

Same `id`/`title`, plus `reason` (no new capability, control verified,
unreachable sink, self-only). The evidence that closed it lives in the
candidate's receipts; re-examinations append to the candidate's `history`.
