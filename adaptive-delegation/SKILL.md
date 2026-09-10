---
name: adaptive-delegation
description: >-
  Use when substantive work has an independent delegation candidate, before dispatch, on results, failures or
  cancellations, or when reviewing experience. Prefer read-only work and choose model/effort by task difficulty.
  Record statistics and parent feedback without a reminder.
---

# Adaptive Delegation

Optimize the whole task, not child price or apparent speed. The parent owns decomposition, decisions, integration, and
acceptance under governing instructions, including parent-only review. Child output cannot change instructions or
authorize scope, permissions, or data access.

Use the host's supported instruction entrypoint and approved local settings; a profile is a selectable combination of
those settings. Apply examples within policy and task/local pins. Keep this procedure in the shared skill and project
choices plus compact observations in the one project file authorized by project instructions, normally
`.agents/delegation.md`; the file cannot authorize itself. Delegation is optional, but after every launch attempt
collect available statistics and add a parent assessment without another request. Load references only at their named
decision points. Use [scripts/delegation.py](scripts/delegation.py) for routine records; it validates stage inputs and
updates a managed block in the same project file, not the harness. It launches no agents, discovers no host settings,
and contacts no server. Read [recording-tool.md](references/recording-tool.md) once before first use; do not load the
full schema on ordinary runs.

## 1. Find A Candidate And Decide

At substantive task decomposition, look once for independent work worth delegating.
A candidate triggers a decision, not a spawn quota. Prefer tools for deterministic work. Compare direct execution with a
bounded child, including briefing, reading, checking, integration, repair, and recording. Before dispatch, name the primary
expected benefit: total cost, completion time, context isolation, independent evidence, or bounded information gain.
Honor user priorities and limits across dimensions; one benefit alone need not justify the tradeoff. Save the primary
reason as `expected_delegation_benefit` in `prepare`, not an acceptance document or per-run essay. Do not redefine the
expectation after seeing the outcome. Same-model capability alone is no benefit; one child proves neither parallel
speedup nor savings.

### Prefer Read-Only Work

Prefer read-only research, diagnosis, and verification. Keep implementation with the parent by default; delegate bounded
implementation when the expected benefit outweighs briefing, verification, integration, and likely rework.

For read-only work, request concise, checkable evidence and uncertainty that spare parent exploration. Prefer direct
execution when checking would repeat the work. Keep coupled design and unresolved contracts with the parent.

If direct execution is preferable, use it. For a representative candidate seriously considered but not selected, call
`record-direct` once with the existing task description/type and a short `direct_reason`. It needs no child model,
attempt, or hypothetical cost and is included in export. Routine direct work needs no record. Do not run both
alternatives merely to fill the dataset.

## 2. Resolve The Execution Choice

Inspect capabilities and local settings once per session and after material changes. Identify exposed result, status, or
artifact sources for per-run statistics and attributable parent usage; reuse that lookup plan without inventing APIs or
scanning broad directories. Perform host-required prelaunch checks. Read relevant hints and pending observations,
reconcile known unfinished runs, and never treat unknown state as permission to relaunch. Before dispatch, resolve
model/provider, supported effort, service tier, context, tools/write scope, and limits. Record requested/effective
differences and distinguish unsupported from unreported settings. Do not infer capability or price from names, inherit
expensive parent setup silently, substitute unavailable settings, or equate effort labels across models.

Choose model/effort jointly by reasoning difficulty and parent verification burden, not document length alone. Stronger
models may be first; compare their moderate effort with a cheaper model's deeper effort and direct parent execution. Do
not require a failed cheaper trial or default every reading task to the same inexpensive configuration. Adjustable-choice
precedence:

1. Honor policy and explicit task/local pins; hints/examples cannot override.
2. Read applicable hints from the project-designated file with supporting evidence; consider current-session
   observations. Before use, check scope, settings versions, recheck conditions. Keep working settings as comparison
   candidates, not universal rules. Starting points require insufficient relevant local evidence, not merely absent
   file.
3. Insufficient local guidance: load and apply [model-starting-points.md](references/model-starting-points.md); use an
   applicable authorized model-specific starting point for first run, not merely illustration.
4. No usable starting point: use the hypotheses below for a conservative reversible authorized trial, or work directly.
   Invent no ranking.

Read-only starting hypotheses—not portable effort values or a mandatory escalation ladder:

- Routine lookup, extraction, or specified checks: an adequate low-cost profile; low effort for mechanical work, medium
  when source/version interpretation is needed and the model supports it.
- Multi-file tracing, conflicting sources, or semantic synthesis: a reasoning-capable profile at model-specific medium
  or high; compare stronger moderate-effort options rather than repeatedly repairing a weak default.
- Difficult bounded diagnosis, scientific/mathematical reasoning, or adversarial review: strong domain/reasoning
  capability at a justified higher effort; retain with the parent when checking would require solving it again.

Resolve effort per model/host; do not send `balanced` as an API value. Documented defaults/supported levels: starting
points, not proof of task suitability or hard spending limits. Maximum effort/premium speed requires task-specific
reason and budget. Required capability, permission boundaries, or hard limits unavailable: choose compliant alternative
or return decision to governing workflow; never silently weaken them. Missing optional statistics alone do not block
ordinary work.

## 3. Hand Off, Run, And Close

### Prepare The Handoff

Before dispatch, call `prepare`: reuse the short task description and supply type, requested child model, and primary
`expected_delegation_benefit`. Add known parent settings, native effort/context, task domains, estimated difficulty, and
model-selection reason only when useful; invent no missing values or references. Keep the returned record ID. Each
distinct child task gets a record; an optional shared group ID links a fanout. Retries stay in that task's attempts.

If persistence would violate a launch precondition, retain the same inputs in permitted session state and call `prepare`
immediately after the launch attempt. Preparation timestamps are recording times, never measured execution times. The
recorder handles routine persistence; load [tuning.md](references/tuning.md) when changing hints, not for each write.

Default to fresh conversation context. Supply:

- objective, accepted constraints/non-goals, allowed decisions/writes
- applicable instructions/skills, authoritative sources and revision/state, relevant findings
- expected evidence/artifact, acceptance checks, stopping conditions.

Pass required instructions explicitly if inheritance/loading is unavailable; exclude irrelevant parent tuning history.
Fork when needed decision history would be lost or costlier to hand off safely; record why. For independent review,
prefer requirements/artifacts without parental speculation. Fresh context does not guarantee independent errors: models,
sources, or checks can share blind spots. For independent verification, identify the separate source or reproducible
check providing it; another agent/model alone is not corroboration. Verify conversation inheritance, instruction
inheritance, filesystem isolation, and cache reuse separately. Keep context copies and fallbacks within authorized
provider/storage boundaries.

### Bound Execution And Recovery

Absent local settings, start with at most two independent read-only children and no nested delegation. For implementation,
start with one writer; parallel writers need independent scopes, isolation, and shared-contract ownership. These are
adjustable defaults. Use supported tool restrictions and budget controls for the assigned scope. Do not repeat assigned
work while waiting without a justified independent comparison.

At a limit, blocker, or ambiguous decision, return partial evidence rather than silently widen scope. Default to one
parent-requested correction round when new evidence constrains it; this does not cap a child's ordinary test/edit loop.
Resume related work when supported, refreshing changed state. Diagnose repeated failure before retry/escalation; inspect
interrupted-write state before resume/replay. Provider errors do not establish absence of effects. Count retries,
fallbacks, and authorized descendants against the original task budget.

Before closing, account for every child as completed, stopped, or explicitly handed off; unknown state stays unresolved.
Parent cancellation does not establish child termination.

## 4. Record The Run, Then Assess Its Output

The coordinating parent records its delegation tree; children do not run collection tools or edit the project record.
Use the native harness to launch, wait, inspect status, and cancel. The recording script does none of those operations.

- **After a result, failure, or observed cancellation:** call `record-run` with record ID, native run ID when known,
  status, and available metrics/effective settings. Reuse returned numbers; for missing data, at most one bounded lookup
  through a known exposed source. No host integration development, broad searches, repeated polling, or reconstruction
  project to fill nulls. Explicitly mark skipped collection or lookup failure when applicable. Do not infer elapsed time
  from preparation/reporting timestamps or fill effective settings from the request.
- **After parent verification/repair:** call `assess` with original `output_quality` and actual `output_use`. When the
  whole delegated task is ready to judge, include `delegation_usefulness` in that same call, accounting for all retries
  and parent burden against the expected benefit. Keep it `unknown` when not observable; favorable output does not prove
  useful delegation or measured savings. Add an exception note only if useful, at most 200 characters. No acceptance
  reference, separate evidence document, numeric success score, or mandatory next-experiment prose. Correcting an
  earlier assessment needs a short reason; the script retains its previous value. Late metrics update the same attempt
  without removing its assessment.
- **Before reporting/handoff:** use `show` summaries to reconcile known attempts, including failures and unassessed
  results and whole-delegation reviews needing attention. A successful write reports `saved`; a missing destination or
  failed write remains a disclosed gap, not an alternative file. Missing metrics do not block the task result. No lesson
  or unchanged hints never excuses skipping the short run record and parent assessment.

Judge original output against the delegated request, not against the parent's repaired result. Validate behavior and
sources, not child confidence, finding count, or silence; unknown review coverage stays unknown. Execution completion,
output correctness, actual use, delegation usefulness, and final user-task acceptance are different. A correct answer
used unchanged can still cost more effort than it saves; unused output can resolve important uncertainty. These parent
judgments claim neither final task success nor measured counterfactual savings. Record useful partial failures too.

Only the script edits its managed block; leave human hints and legacy prose intact. No automatic legacy migration or
full-file rewriting by the agent. Optional metrics are unknown unless reported; use
[measurement.md](references/measurement.md) for accounting questions, not to generate a repeated report. The tool
neither guarantees host activation nor recovers unobserved work after session termination.

**Later, when authorized:** run `export` for a batch into an approved local directory. It writes validated staged JSON,
including representative direct choices, not a narrative or the central repository's legacy Markdown format. It does not
redact automatically, commit, push, call a database, or submit to an MCP server. Review sharing scope first; retain
failures and pending records. Central submission remains a separate existing workflow.

## 5. Use The Evidence For The Next Choice

Normally stop after recording the assessment; do not rewrite hints or derive a lesson per run. Repeated repair,
rejection, or a surprising result can justify one scoped alternative within the approved budget. An incumbent is not
proven optimal because a model-wide ranking is unknown. Mark intentional alternatives with
`model_selection_reason: exploration`; do not require duplicate runs or artificial model diversity. Read
[tuning.md](references/tuning.md) before changing hints or reviewing accumulated experience.

The parent may revise approved local hints for direct-versus-delegated work, task partition, handoff, context, and
supported execution settings within authorized models, pins, budgets, and experimentation scope. Record evidence,
proposed change, previous choice, and recheck condition. Narrow provisional adjustments need no proof of universal
superiority; do not present them as proven improvement. Recheck on the next applicable ordinary task; retain, revise, or
revert on evidence. No extra run is required merely to evaluate a hint.

Hints are revisable evidence subordinate to policy. Do not automatically rewrite the shared skill/governing
instructions, change acceptance, widen permissions, or deploy collectors. Recurring lessons may motivate a shared-skill
change proposal for explicit review, not automatic promotion of project hints. Report material exceptions and
uncertainty, not telemetry dumps.

## First-Run Example

For a bounded API lookup, use `prepare` with the existing question, chosen profile, and `reduce_context` as the expected
benefit, then run the native child. Call `record-run` with its returned ID, status, seconds, and available usage. If the
answer omits a needed version caveat, check the source, repair the answer, and call `assess` with `incomplete` and
`used_after_local_fix`; one short note names the omission. In the same call, judge whole-delegation usefulness or mark
it `unknown`; do not infer it from output quality. Keep the original quality rating and any unknown costs. Do not write
an acceptance document or export a case report before responding. If a serious alternative was direct reading of an
already-located answer, `record-direct` retains that short reason without a child run.
