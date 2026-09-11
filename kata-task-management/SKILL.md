---
name: kata-task-management
description: Use Kata for substantive multi-step work, task planning, epic/task hierarchy, follow-ups, blockers, and verified completion. Load before substantive work or when initializing a Kata workspace, reorganizing issues, recovering failed mutations, or closing/reopening work; brief scoping and simple questions/lookups need no registration.
license: MIT
---

# Kata Task Management

Use [Kata](https://www.katatracker.com/) as the shared task ledger, not alongside a competing persistent TODO list or
status plan. Detailed design and verification artifacts may live elsewhere; link them from their owning issues.
Honor repository policy and existing approval boundaries. This skill does not authorize replacing another mandated
tracker, installing software or hooks, changing project bindings, or publishing work without the applicable approval.

## Start And Scope

- At the first Kata use in a session, run `kata quickstart` and confirm the intended workspace/project and daemon.
  Do not repeat quickstart per message; revisit it when the environment, version, or command semantics change.
  An explicit project/daemon selection or inherited configuration can target somewhere other than the current Git root.
- If Kata is missing or the workspace needs initialization, load and apply
  [Initialization](references/initialization.md) before changing setup. Reuse an existing valid binding.
- Before substantive multi-step work, search for the owning issue. Update a matching issue; create only when none fits,
  using an idempotency key retained for retries. Brief scoping, simple questions, and short lookups need no issue.
- Keep tasks in their owning project, including when work starts from another repository. Do not create practice,
  tutorial, or scratch issues unless explicitly requested. In shared queues, check and claim ownership before execution;
  a claim is not permission to change the task's scope.

## Plan And Organize

- Keep the issue body current: objective, scope, completion criteria, and the actionable plan. Comments record progress
  and decision history; reflect accepted scope or criteria changes in the body rather than leaving stale requirements.
  Detailed artifacts retain their designated authority; the issue links them rather than becoming a conflicting copy.
- When creating a task, inspect existing epics/tasks and assign an appropriate `parent`. Use an epic for one shared
  objective spanning independently assignable or verifiable tasks, not as a ceremonial wrapper for a standalone task.
- Revisit hierarchy as scope becomes clearer or related work grows, including initially unparented tasks. Reparent
  existing issues rather than duplicating them. Do not split every command or routine verification step into an issue.
- `parent` is scope membership, not execution order. `blocks` means this issue must finish before the target proceeds;
  `blocked_by` means the target must finish first. Use `related` for context without ordering. Siblings need not be serial.
- Before adding blocking links, inspect the affected blocking graph for cycles; afterward, verify the relationships and
  readiness. Parent-cycle rejection and a ready queue alone do not prove blocking-graph acyclicity.

## Commands And Recovery

- Prefer `--agent` for ordinary reads and mutations; use `--json` when a script needs structured data. Take syntax from
  `kata quickstart`, `kata --help`, and the relevant command's `--help`, not a remembered command dictionary. Verify
  unfamiliar flags, evidence types, and output shape against the installed version.
- Pass titles and bodies as literal arguments. Prefer documented file/stdin inputs for multiline text when available;
  otherwise use the shell's literal-safe quoting or an argument-array API. Do not put backticks or `$()` in an expanding
  shell string, or assume literal `\n` becomes a newline. Re-read meaningful body edits to confirm the stored text.
- After a mutation error, inspect actual issue state before retrying. A mutation can succeed while its attached comment
  fails; retry only the missing step. Reuse the original creation idempotency key rather than making a fresh issue.
- When removing a parent, read the current parent first: removal may assert that exact relationship. After relationship
  edits, re-read the affected issues rather than inferring success from a ready queue or a partial response.
- Investigate errors using current help and observed state. Do not invent sleeps, serialize unrelated work, or weaken
  daemon checks to hide a failure. Never run `kata delete` or `kata purge` without explicit approval for the action and
  target issue.

## Verify And Close

- Compare results with the issue's current completion criteria. Distinguish implementation, verification, and publication
  when the scope distinguishes them. Verify required child work and the parent's own criteria before closing a parent.
- Close each issue when its work is verified, with a substantive reason and task-appropriate evidence. Use evidence
  forms supported by installed help, such as `--commit`, `--pr`, `--test`, or `--reviewed`. A commit, passing test, evidence
  flag, or accepted close command alone does not establish completion.
- If required work remains, keep the issue open, label it `needs-review`, and state what remains. Do not close merely to
  clear a queue or end a session. Re-read state after closing to confirm the intended issue and result.
- Reopen when the original completion criteria were unmet. For a new deliverable or requirement, create separate linked
  work instead of silently expanding completed scope. Treat duplicate, superseded, or declined dispositions as such,
  not as evidence that the original implementation was completed.
