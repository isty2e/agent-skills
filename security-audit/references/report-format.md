# Report format

Modified for security-audit. See [NOTICE](../NOTICE) for licensing and
upstream attribution.

The report is derived from the state files (`findings.json`,
`candidates.json`, `coverage.json`, `inventory.json`, `scan-state.json`) and
`threatmodel.md`. Author the canonical JSON first and write the report from
it, never from a separate narrative: every id, severity, confidence, count,
and status in the report must match the JSON. After any JSON change, rewrite
the affected report sections. No script renders it.

## Structure

```
# Security Review: <target>

## Scope
<in-scope paths and `--exclude` prefixes, inventory mode, source and snapshot digest,
artifacts reviewed, runtime/test status, validation mode, limitations; whether
the threat model was generated or supplied; reviewed vs excluded file counts
with exclusions by reason; scan status>

### Scan Summary        (when findings exist)
| Field | Value |        findings count, severity mix, confidence mix, limitations

## Threat Model
<the four-section model: overview + resources, boundaries + assumptions,
stories, severity calibration>

## Findings

### Findings Summary
| Finding | Severity | Confidence | Detailed write-up |

### Confidence Scale
| Label | Meaning |

### [n] <title>
| Field | Value |
| Severity | ... | Confidence | ... | Confidence rationale | ... |
| Category | ... | CWE | ... | Affected lines | path:line-range |

#### Summary
#### Root Cause
#### Validation
#### Dataflow
#### Reachability
#### Severity
#### Remediation

## Reviewed Surfaces      (repository-wide or any scan with a ledger)
| Surface | Risk Area | Outcome | Notes |

## Open Questions And Follow Up   (every coverage.unresolvable record)
```

## Rules

- Order findings critical → high → medium → low; renumber so table, headings,
  and anchors agree.
- `Affected lines` includes the root broken control or sink, not only the
  wrapper that reaches it. Keep every independently reachable sibling instance.
- One finding per broken control + remediation; do not merge distinct failures
  that merely share a CWE, and do not add secondary CWEs that only make
  exploitation worse.
- `Severity` folds likelihood and impact into one level with a concrete
  rationale, one sentence on what evidence would raise or lower it. No
  circular phrasing.
- `Root Cause` walks input → transformations → missing control → sink; code
  lives in `codeEvidence`, referenced by id.
- `Reviewed Surfaces` outcomes: `Reported`, `No issue found`, `Rejected`,
  `Not applicable`, `Needs follow-up` — each with the specific evidence.
- No findings: a short `No findings` section explaining why nothing survived
  discovery and validation, still followed by `Reviewed Surfaces`.
- Open questions are exactly the `coverage.unresolvable` records (with their
  status and any deferred candidate), as copyable, specific follow-ups (file,
  component, boundary), not generic prompts.
- Never claim runtime reproduction, coverage, or completeness the receipts do
  not establish.
