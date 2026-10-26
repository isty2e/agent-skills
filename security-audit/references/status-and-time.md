# Scan status semantics

Modified for security-audit. See [NOTICE](../NOTICE) for licensing and
upstream attribution.

Record the scan's terminal state in `scan-state.json` → `status`. The status
decides what conclusions the report may draw.

| Status | Meaning |
|---|---|
| `completed` | The requested scope finished and quiescence held. Findings and absence-of-findings are reportable. |
| `failed` | Stopped after an unrecoverable blocker. Retained findings are valid; absence of findings is inconclusive. |
| `canceled` | Explicitly canceled. Retained findings are valid; absence is inconclusive. |
| `interrupted` | Stopped before completion (context loss, time, crash). Retained findings are valid; absence is inconclusive. |

Rules:

- Only `completed` supports "no vulnerabilities found" or an equivalent
  assurance statement.
- For any stopped state, report retained findings, pending candidates, and the
  exact unfinished work; never synthesize a clean result.
- A stopped scan is resumable from `scan-state.json`; resuming does not discard
  earlier receipts.
- Do not mark `completed` while `scan-gate.py check` fails.
- If source review never started, say so explicitly; an empty finding set is
  not a no-findings result.
- Do not edit or delete receipts to make a stopped scan look complete.

## Investigation time

If a time allowance is set (minutes, from the user or the scan request; record
it as `time_allowance_minutes`), treat it as advisory: pursue the most valuable
open check while time remains; at the deadline stop opening new
investigations, preserve unfinished work as gaps, and finish reporting from
established evidence. Never pad or busy-wait. The
allowance is shared across passes and resumes; it is not reset.
