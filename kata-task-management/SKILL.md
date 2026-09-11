---
name: kata-task-management
description: Use Kata for substantive multi-step work, planning, epic/task hierarchy, follow-ups, blockers, and verified closure. Load before substantive work, workspace setup, issue reorganization, failed-mutation recovery, or closing/reopening work; brief scoping and simple questions/lookups need no registration.
license: MIT
---

# Kata Task Management

Use [Kata](https://www.katatracker.com/) as the shared task ledger, not alongside competing persistent TODOs or status
plans. Link design/verification artifacts from owning issues; preserve their designated authority without duplicating
it. Honor repository policy and approval boundaries: this skill grants no permission to replace mandated trackers,
install software/hooks, change bindings, or publish.

## Start And Plan

- On first session use, run `kata quickstart` and confirm workspace/project and daemon. Revisit only when environment,
  version, or command semantics change; explicit selectors or inherited configuration may target beyond the Git root.
- Missing CLI or workspace setup: load and apply [Initialization](references/initialization.md); reuse valid bindings.
- Before substantive multi-step work, find and update the owning issue; create only if none fits, retaining a creation
  idempotency key for retries. Brief scoping, simple questions, and short lookups need no issue. Keep work in its owning
  project even from another repository; no practice/tutorial/scratch issues unless requested. Check and claim shared-queue
  ownership before execution; claims do not authorize scope changes.
- Keep objective, scope, completion criteria, and actionable plan current in the body. Comments hold progress/history;
  reflect accepted scope/criteria changes in the body, linking authoritative details rather than copying them.
- At creation, inspect existing epics/tasks and assign an appropriate `parent`. Epics group one objective across
  independently assignable or verifiable tasks, not standalone-task ceremony. Revisit hierarchy as scope/related work
  grows, including unparented tasks; reparent rather than duplicate. Do not make issues for every command or routine check.
- `parent` means scope membership, not order. `blocks`: this issue finishes before the target; `blocked_by`: target
  finishes first; `related`: context without order. Siblings need not be serial. Before blocking links, check the affected
  blocking graph for cycles; afterward verify relationships/readiness. Parent-cycle rejection or a ready queue is not
  proof of blocking-graph acyclicity.

## Execute And Recover

- Prefer `--agent`; use `--json` for scripted structured data. Get syntax from installed `kata quickstart`, `kata --help`,
  and command `--help`, not memory. Check unfamiliar flags, evidence types, and output shapes against that version.
- Pass titles/bodies literally: prefer documented file/stdin inputs for multiline text, otherwise literal-safe quoting
  or argument arrays. Never put backticks or `$()` in expanding shell strings or assume literal `\n` becomes a newline.
  Re-read meaningful body edits.
- After mutation errors, inspect actual state and retry only missing steps: the mutation may succeed but its comment
  fail. Reuse creation keys. Read the current parent before removal, which may assert that exact relationship; after
  relationship edits, re-read affected issues rather than trusting ready queues or partial responses.
- Diagnose with current help and observed state; do not invent sleeps, serialize unrelated work, or weaken daemon checks
  to hide errors. `kata delete` and `kata purge` require explicit action-and-target approval.

## Verify And Close

- Check current completion criteria, distinguishing implementation, verification, and publication where scoped.
  Parent closure requires verified required children and the parent's own criteria.
- Close verified work with a substantive reason and task-appropriate evidence in installed-help-supported forms.
  A commit, passing test, evidence flag, or accepted close command alone does not prove completion. Re-read the intended
  issue's state after closing.
- Required work remains: keep open, label `needs-review`, and state what remains. Never close to clear a queue or end a
  session. Reopen for unmet original criteria; new deliverables/requirements become separate linked work, not expanded
  completed scope. Duplicate, superseded, or declined dispositions do not mean the original implementation completed.
