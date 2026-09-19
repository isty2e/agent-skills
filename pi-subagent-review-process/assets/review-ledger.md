# Review Ledger

## Target

- Repository / absolute cwd:
- Review kind:
- Git base/head and/or review files:
- Initial worktree state:
- User constraints / forbidden actions:
- Required current-head checks:

## Preflight

- [ ] Reviewer capabilities checked: executable, enabled, available runner, required effective model/thinking
- [ ] Example-based packet uses an unused absolute `materialDir`
- [ ] Shared `reviewSkills` and lane `routedSkills` cover assigned decisions
- [ ] Generator produced captured material and launch request
- Packet / request / material paths:
- Wrapper / mission IDs; async / status paths (per round):

## Coverage

| lane key / decision | routed skills / source seam | reviewer / model / thinking | status | wrapper / child IDs | output / disposition |
| --- | --- | --- | --- | --- | --- |
| | | | prepared | | not collected |

## Parent Findings

| candidate / source lane or direct | scope / approval relevance | mechanism / impact | status | adjudication / root-cause owner |
| --- | --- | --- | --- | --- |
| | in-scope or out-of-scope / yes or no | | open | |

States: `open`, `confirmed`, `rejected`, `duplicate`, `pre-existing`, `needs-decision`. Out-of-scope/pre-existing findings
always have approval relevance `no`.

## Gate And Recovery

- Round gate-report paths:
- [ ] Reports retained after settling; original lane keys and run IDs preserved
- [ ] Original coverage accounted for across ready receipts and authorized parent review
- [ ] Wrapper failures, evidence gaps, and affected side effects resolved under governing recovery requirements

A subset pass covers only its round. Recover gaps without rerunning unaffected lanes or replacing required independent
review without authorization. Gate success never authorizes final disposition.

## Closure

- [ ] No tracked child/wrapper remains active
- [ ] Supervisor/intercom queues and completion/control notices drained; later notices reset closure
- [ ] Exact Git base/head and/or captured file snapshots reconfirmed, along with worktree state
- [ ] Local checks follow session rerun/authorization policy
- [ ] Candidates independently adjudicated, deduplicated, and scoped; out-of-scope findings disposition-neutral
- [ ] Retained prior findings still reproduce; residual risks and excluded evidence recorded

## Disposition

State: `blocked | request-changes | approve | no-disposition`

- In-scope findings affecting disposition:
- Out-of-scope findings reported separately:
- Rejected candidates:
- Verification evidence / residual risks:
- [ ] Exactly one final report delivered

A post-final child notice reopens this ledger: retract disposition and recheck affected evidence and closure.
