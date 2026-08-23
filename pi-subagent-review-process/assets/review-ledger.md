# Review process ledger

## Target authority

- Repository:
- Working directory:
- Review kind:
- Base:
- Head:
- Initial worktree state:
- User constraints:
- Forbidden actions:

## Runtime preflight

- [ ] `subagent({ action: "list" })` completed
- [ ] Selected reviewer agent is executable and not disabled
- [ ] Effective model and thinking are observable and match the session requirement
- [ ] Parent-captured `review-material.json`, changed-file list, stat, and patch match the exact base/head
- [ ] Every lane prompt contains readable material paths and forbids requesting or running `git diff`
- [ ] Shared `reviewSkills` includes `code-review-vector`; every lane has explicit vector-specific `routedSkills`
- [ ] `materialDir` is unique to this wave and is not shared with an earlier or concurrent wave
- [ ] Review packet generated from `scripts/review-wave.mjs`
- [ ] Generated workflow is exactly one `return await runs.all(lanes)` fanout
- Top-level run id:
- Mission id:
- Async directory:
- Status path:

## Coverage ledger

| lane key | decision owned | routed skills | source seam | reviewer | model/thinking | status | child run id | output collected | candidate disposition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | prepared | | no | |

## Parent evidence and candidate ledger

| candidate id | source lane/direct | scope class | approval relevant | mechanism | impact | current status | independent adjudication | root-cause owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| | | in-scope/out-of-scope | yes/no | | | open | | |

Allowed candidate states: `open`, `confirmed`, `rejected`, `duplicate`, `pre-existing`, `needs-decision`. `approval relevant` must be `no` for every out-of-scope or pre-existing finding.

## Terminal receipt phase

- [ ] Top-level workflow state is `completed`, not failed, stopped, detached, or merely fleet-empty
- [ ] Top-level status has no wrapper error and contains the directly awaited lane receipts in `workflow.value`
- [ ] Every expected lane has exactly one terminal status step
- [ ] Every lane has a child run id and a structured final output with in-scope, out-of-scope, and residual-risk sections
- [ ] `scripts/review-gate.mjs` passed after its settling interval
- [ ] Machine-gate receipt copied below

```json
{}
```

A failed wrapper—including `unawaited runs.run`—blocks final delivery even when child files exist. Resolve or replace the orchestration; do not salvage it into an approval.

## Quiescence and parent closure phase

- [ ] No tracked child or wrapper remains active
- [ ] `subagent_supervisor({ action: "pending" })` is empty
- [ ] `intercom({ action: "pending" })` is empty
- [ ] Delayed completion/control notices have been consumed
- [ ] No new notice arrived after this closure pass; if one arrives, reset this section
- [ ] Exact base/head and worktree state were reconfirmed
- [ ] Required current-head CI/check evidence was reconfirmed
- [ ] Local validation followed the session's no-rerun/authorization policy
- [ ] Every candidate was independently adjudicated, deduplicated, and assigned a scope class
- [ ] Out-of-scope findings are retained for reporting but excluded from disposition logic
- [ ] Every prior finding was retained only if it still reproduces
- [ ] Residual risks and excluded evidence are recorded

## Final disposition

State: `blocked | request-changes | approve | no-disposition`

- In-scope findings affecting disposition:
- Out-of-scope findings reported separately with no disposition effect:
- Rejected candidates:
- Verification evidence:
- Residual risks:
- Exactly one final report delivered: [ ]

Do not label a post-final child message as a “late review.” Its arrival proves the closure phase was premature; retract the disposition and reopen the ledger.
