---
name: kata-task-management
description: Use Kata for substantive multi-step work, planning, epic/task hierarchy, follow-ups, blockers, and verified closure. Load before substantive work, workspace setup, issue reorganization, failed-mutation recovery, or closing/reopening work; brief scoping and simple questions/lookups need no registration.
license: MIT
---

# Kata Task Management

Use [Kata](https://www.katatracker.com/) as the shared task ledger, not alongside competing persistent TODOs or status
plans. Link design, verification, documentation, and data artifacts from owning issues; preserve their designated
authority, repeating at most headline numbers. Honor repository policy and approval boundaries: this skill grants no
permission to replace mandated trackers, install software/hooks, change bindings, or publish.

## Start And Plan

- Before the first mutation in a session, confirm the resolved workspace/project and daemon. Read `kata quickstart`
  during initialization, before using a Kata feature this skill does not cover (such as teammate attribution, attention
  requests, or event streams), or when installed behavior contradicts this skill.
- Missing CLI or workspace setup: load and apply [Initialization](references/initialization.md); reuse valid bindings.
- Before substantive multi-step work, find and update the owning issue; create only if none fits, with an idempotency
  key. Keep work in its owning project even from another repository; no practice/tutorial/scratch issues unless
  requested. Check and claim shared-queue ownership before execution; claims do not authorize scope changes.
- Keep objective, scope, completion criteria, and actionable plan current in the body. Comments hold progress/history;
  reflect accepted scope/criteria changes in the body.
- At creation, search open and closed issues for the same objective and parent the new issue under its open epic. If
  none is open but the new issue continues earlier work, create an epic, parent the new issue and any unparented
  predecessor, and link a closed predecessor epic as `related`. Never leave open work under a closed epic; when
  reopening a child, also reopen its closed epic. Epics group one objective across independently assignable or
  verifiable tasks, not standalone-task ceremony; reparent rather than duplicate. Do not make issues for every command
  or routine check.
- `parent` means scope membership, not order; siblings need not be serial. Before blocking links, check the affected
  blocking graph for cycles. Parent-cycle rejection or a ready queue is not proof of blocking-graph acyclicity.

## Write For A Cold Reader

- Write for a teammate or later agent reading `kata show` without this session. Use plain terms; define session-local
  labels (requirement ids such as R1, audit rule codes, skill abbreviations) at first use, or avoid them.
- Before closing, post a final comment with the outcome or disposition. Lead each progress comment with its result or
  current blocker, then as applicable: changes; headline numbers, including regressions and null results; what
  remains, was declined, or is deferred; residual risks; evidence location (commit, document section, receipt path).
  Add detail only when it supports a decision or reopen condition.
- Keep procedure traces (review-vector coverage, per-candidate audit dispositions, command logs) in task notes or
  receipt files, not issue text.

## Execute And Recover

- Prefer `--agent`; use `--json` for scripted structured data. Get syntax from installed `kata --help` and command
  `--help`, not memory. Check unfamiliar flags, evidence types, and output shapes against that version.
- Pass titles/bodies literally: prefer documented file/stdin inputs for multiline text, otherwise literal-safe quoting
  or argument arrays. Never put backticks or `$()` in expanding shell strings or assume literal `\n` becomes a newline.
  Re-read meaningful body edits.
- After mutation errors, inspect actual state and retry only missing steps: the mutation may succeed but its comment
  fail. Reuse creation keys. After relationship edits, re-read affected issues rather than trusting ready queues or
  partial responses.
- Diagnose from observed state; do not invent sleeps, serialize unrelated work, or weaken daemon checks to hide errors.
  `kata delete` and `kata purge` require explicit action-and-target approval.

## Verify And Close

- Check current completion criteria, distinguishing implementation, verification, and publication where scoped.
  Close a parent only after every child is closed or moved out of its scope, required children are verified, and the
  parent's own criteria are met.
- Close verified work with a substantive reason and task-appropriate evidence in installed-help-supported forms.
  A commit, passing test, evidence flag, or accepted close command alone does not prove completion. Re-read the intended
  issue's state after closing.
- Required work remains: keep open, label `needs-review`, and state what remains. Never close to clear a queue or end a
  session. Reopen for unmet original criteria. New deliverables and actionable follow-ups become separate issues. Defer
  dated work with a future schedule (a deadline does not defer it); park undated work by setting metadata `someday` to
  true, and unset it to resume. Duplicate, superseded, or declined dispositions do not mean the original implementation
  completed.
