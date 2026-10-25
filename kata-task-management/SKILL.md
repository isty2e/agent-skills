---
name: kata-task-management
description: >-
  Use for work needing resumption, coordination, dependency management, or follow-up; requests connected to tracked
  work; and direct Kata operations, including workspace setup, issue or hierarchy changes, closure, reopening, and
  failed-mutation recovery.
license: MIT
---

# Kata Task Management

Use [Kata](https://www.katatracker.com/) as the shared task ledger for tracked work, without competing persistent TODOs
or status plans. Honor repository policy and approval boundaries; this skill grants no permission to replace mandated
trackers, install software/hooks, change bindings, or publish.

## When To Track

- If the request or current context provides concrete signs of an existing Kata owner (an issue reference, a known
  continuation, or a link from the relevant branch/PR), reuse that owner or make a scoped lookup before treating the
  work as untracked. A project binding alone does not require this search.
- Without an identified owner, decide whether work needs resumption, coordination, dependency management, or follow-up
  before further issue search or setup. Bounded, self-contained work needs no new issue. Size, step count, and duration
  alone do not decide this; expected resumption or handoff does.
- If a tracking need emerges, register it then. Before pausing or handing off, ensure known remaining commitments,
  blockers, and partially applied changes that need management have an owning record. No per-turn checklist or report
  is required; discarded possibilities and unaccepted suggestions are not follow-up commitments.
- Continuing tracked work still requires keeping its owner current, even when the current action is small. A useful
  summary may be added to an existing issue, including a closed one, without reopening it merely to record an event.

## Own And Organize Work

- For work needing an owning issue, reuse one already identified or search open and closed issues for the same
  objective; create only if none fits, with an idempotency key. Keep work in its owning project even from another
  repository. No practice, tutorial, or scratch issues unless requested. Check and claim shared-queue ownership before
  execution; claims do not authorize scope changes.
- An issue owns a coherent outcome and completion conditions. Design, implementation, review, and verification are
  normally phases, not separate deliverables. When scope grows, split outcomes needing independent completion,
  deferral, assignment, or prioritization rather than continually extending the body. Administrative decomposition
  within authorized scope does not authorize additional work.
- Use an epic when independently managed outcomes under one objective need coordination; reuse an applicable open
  epic or create one if none fits. Continuation alone requires neither a new epic nor retrospective reparenting.
  Reparent rather than duplicate; never leave open work under a closed epic, and reopen that epic when reopening its
  child.
- `parent` means scope membership, not execution order; siblings need not be serial. Before blocking links, check the
  affected blocking graph for cycles. Parent-cycle rejection and ready queues do not establish blocking-graph safety.
- Defer dated work with a future schedule, not merely a deadline. Park undated work with metadata `someday=true` and
  unset it to resume. Duplicate, superseded, or declined dispositions do not mean the original implementation completed.

## Keep Useful Records

- Keep the current objective, scope, completion conditions, and essential remaining work readable without the
  conversation. Define session-local labels or avoid them; no fixed template is required. Update the body for accepted
  scope or plan changes, rather than appending successive versions. Preserve genuine history and immutable evidence;
  correct factual errors in editable records, including comments, and reconcile affected current summaries in place.
- Record material events in status/comments, not phase transitions or routine checks alone. Lead with the result or
  blocker. Include regressions, null results, declined/deferred work, residual risks, and evidence references when they
  affect continuation, decisions, or reopening. Detail is justified by that use, not a word-count target.
- Keep design, verification, documentation, and data evidence with its designated owner; link it rather than maintain
  copies, repeating at most headline numbers. Do not require procedure logs merely for tracking. Where another
  governing workflow requires detailed audit evidence, keep it in its owning notes/artifacts rather than issue prose.

## Operate And Recover

- Confirm the resolved workspace/project and daemon from current evidence before project-scoped reads or mutations;
  reuse that evidence while valid and recheck changed context. For a missing CLI or setup, load and apply
  [Initialization](references/initialization.md); reuse valid bindings. Read `kata quickstart` during initialization,
  for features this skill does not cover, or when installed behavior contradicts it.
- Prefer `--agent`; use `--json` for structured processing. Get syntax, unfamiliar flags, evidence types, and output
  shapes from installed `kata --help` and command `--help`, not memory. Pass titles/bodies literally using documented
  file/stdin inputs or literal-safe quoting/argument arrays; do not expand backticks or `$()` or assume literal `\n`
  becomes a newline.
- Use confirmed operation results without automatically repeating reads. Read back when the response lacks the
  needed state, concurrent changes matter, or relationship invariants require it. For issue-body writes, confirm the
  stored body from the response; if it is omitted, read back that body. Verify affected relationships from sufficient
  state, not ready queues or partial responses.
- After errors, inspect actual state and retry only missing steps. A mutation can succeed while its appended comment
  fails, including `close --comment`: check closure and comments, then repair only what is missing. Reuse idempotency
  keys and check comments before reposting. Stop if state cannot be established or no evidence-backed recovery step
  remains; a different error alone is not progress. Report the error and required tracking still pending.
- Diagnose from observed state; do not invent sleeps, serialize unrelated work, or weaken daemon checks to hide errors.
  `kata delete` and `kata purge` require explicit action-and-target approval.

## Verify And Close

- Verify current completion conditions, distinguishing implementation, verification, publication, and tracker state.
  Verify the actual delivered result; earlier verification does not cover changed decision-relevant substance or
  scope, including changes introduced during presentation edits. A commit, passing test, evidence flag, or successful
  close command alone does not prove the work complete. Never close merely to clear a queue or end a session.
- Close a parent only after every child is closed or moved out of its scope, required children are verified, and the
  parent's own conditions are met. If required work remains, do not close; label `needs-review` and state the
  gap. Reopen for unmet original criteria; organize new outcomes under Own And Organize Work.
- Keep the outcome/disposition and useful evidence references visible in an issue comment; reuse an existing current
  summary instead of repeating it. Use `--message` for a brief substantive closure reason identifying scope and
  verification, with task-appropriate evidence in installed-help-supported forms. When adding an outcome comment,
  combine it with closure using `--comment` where supported.
- Report verified external results promptly despite bookkeeping failures. Claim tracker/workflow completion only when
  required tracking is confirmed. Reconcile missing bookkeeping on the owning record; create no issue solely for it.
