# Receipts: file and candidate coverage

Modified for security-audit. See [NOTICE](../NOTICE) for licensing and
upstream attribution.

A surface is covered only when a receipt proves it, never because it appeared
in `rg` output or a search hit. `scripts/scan-gate.py check` verifies that
receipts are complete and consistent; it cannot verify that the reading
happened, so a receipt is an attestation — write only what was done.

## File receipts

`coverage.json` (`schemas/coverage.schema.json`) → `reviewed_files[]`, exactly
one per file in `inventory.json`. Its top-level `snapshot_digest` binds these
receipts to the reviewed inventory (`references/scope.md`); it is an
attestation, not a value to update automatically when inventory changes:

```json
{"path": "src/server.py", "disposition": "reviewed", "read_full": true,
 "items": ["authz", "path", "render"], "note": "all routes; no SSRF guard at :651"}
```

- `reviewed` requires `read_full: true` and the checklist `items` actually
  applied (ids from `references/checklist.md`). A partial read is `deferred`
  with what remains in `note`.
- `excluded` requires a `reason` — `generated`, `vendored`, `binary`,
  `test-only`, `documentation`, or `static-asset` — and a `note` saying how
  that was established. "Screened", "no sink found", or a search miss is not a
  reason: such a file is `reviewed` or still `deferred`. Exclusion never
  implies safety, and the report counts exclusions by reason.
- A deleted file is reviewed from the diff's baseline (`references/diff-mode.md`);
  record what control its removal stopped enforcing.
- A symlink is reviewed as a link (its target string and who resolves it); do
  not follow it out of the target.
- Files read only to explain an in-scope path (diff mode) go in
  `supporting_files[]` with why they were needed, not in `reviewed_files`.

## Candidate receipts

Each candidate carries three receipts in `candidates.json`
(`schemas/candidates.schema.json`):

```json
{
  "id": "ssrf-pdf-link-fetch",
  "title": "PDF link fetch reaches internal hosts",
  "locations": {"entrypoint": "server.py:230", "root_control": "server.py:230",
                "sink": "server.py:231", "concrete_implementation": "webpage.py:45"},
  "discovery": {"method": "forward trace", "evidence": "...", "survives": true},
  "validation": {"disposition": "reportable", "method": "interface", "confidence": "medium",
                 "confidence_rationale": "...", "evidence": "...",
                 "counterevidence_or_proof_gap": "...", "survives": "yes"},
  "attack_path": {"decision": "reportable", "severity": "medium",
                  "severity_rationale": "...", "change_conditions": "...", "proof_gap": "..."}
}
```

- `validation.disposition`: `reportable`, `suppressed`, `not_applicable`, or
  `deferred`; `method` is a `references/validation-methods.md` id.
  `reportable` needs `survives: yes`; `suppressed` and `not_applicable` need
  `survives: no` and an `attack_path.decision` of `ignore`.
- `attack_path.decision`: `reportable` (with `severity`), `ignore`, or
  `deferred`.
- Reportable in both receipts → `findings.json` `findings`; suppressed,
  not applicable, or ignored → `non_findings`. A candidate deferred in either
  receipt stays out of both and must be named by a `coverage.unresolvable`
  record (`candidate` field) carrying the exact missing proof.
- Keep independently reachable instances separate: one candidate per
  `family:file:line`. Do not collapse siblings because they share a helper.
- A re-examination that changes a receipt moves the old receipt into the
  candidate's `history[]` (pass, phase, receipt, reason); never delete it.

## No implicit coverage

- A candidate in a report but not in `candidates.json` is uncovered.
- A file in the inventory without a receipt is uncovered.
- "No findings" with uncovered surfaces is not a clean result; it is an
  incomplete scan and must be reported as such.
