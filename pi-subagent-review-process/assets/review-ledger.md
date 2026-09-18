# Review process ledger

## Target authority

- Repository:
- Working directory:
- Review kind:
- Base:
- Head:
- Review files:
- Initial worktree state:
- User constraints:
- Forbidden actions:
- Required current-head checks:

## Runtime preflight

- [ ] `subagent({ action: "list" })` completed
- [ ] Selected reviewers are executable and enabled
- [ ] Effective model and thinking match the session requirement
- [ ] Packet starts from `assets/review-wave.example.json` with an unused absolute `materialDir`
- [ ] Shared `reviewSkills` and lane-specific `routedSkills` cover the intended decisions
- [ ] `scripts/review-wave.mjs` generated the immutable material and launch request
- Review packet:
- Generated request:
- Material directory:
- Wrapper run id:
- Mission id:
- Async directory:
- Status path:

## Coverage ledger

| lane key | decision owned | routed skills | source seam | reviewer | model/thinking | status   | wrapper/child run ids | output collected | candidate disposition |
| -------- | -------------- | ------------- | ----------- | -------- | -------------- | -------- | --------------------- | ---------------- | --------------------- |
|          |                |               |             |          |                | prepared |                       | no               |                       |

## Parent evidence and candidates

| candidate id | source lane/direct | scope class           | approval relevant | mechanism | impact | current status | independent adjudication | root-cause owner |
| ------------ | ------------------ | --------------------- | ----------------- | --------- | ------ | -------------- | ------------------------ | ---------------- |
|              |                    | in-scope/out-of-scope | yes/no            |           |        | open           |                          |                  |

Allowed states: `open`, `confirmed`, `rejected`, `duplicate`, `pre-existing`, `needs-decision`. Every out-of-scope or pre-existing finding has approval relevance `no`.

## Machine gate

- [ ] Each round's gate report retained after its settling interval
- [ ] Original lane coverage accounted for across ready receipts and explicit parent review
- [ ] Wrapper failures, evidence gaps, and affected side effects resolved
- [ ] Gate reports copied below

```json
{}
```

A subset pass covers only that round. Retain original lane keys and run IDs; resolve gaps without rerunning unaffected lanes. Parent adjudication and closure remain required.

## Parent closure

- [ ] No tracked child or wrapper remains active
- [ ] Supervisor and intercom pending queues are empty; completion/control notices are drained
- [ ] No later notice arrived after this pass; otherwise reset closure
- [ ] Applicable target identity was reconfirmed: exact base/head for Git and captured snapshots for review files
- [ ] Local validation followed the session's rerun and authorization policy
- [ ] Every candidate was independently adjudicated, deduplicated, and scope-classified
- [ ] Out-of-scope findings remain reportable but disposition-neutral
- [ ] Every retained prior finding still reproduces
- [ ] Residual risks and excluded evidence are recorded

## Final disposition

State: `blocked | request-changes | approve | no-disposition`

- In-scope findings affecting disposition:
- Out-of-scope findings reported separately:
- Rejected candidates:
- Verification evidence:
- Residual risks:
- Exactly one final report delivered: [ ]

A post-final child message means closure was premature. Retract the disposition and reopen this ledger.
