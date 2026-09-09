# Recording And Learning Checks

These are review cases and a host-test protocol, not measured compliance results. Keep expected outcomes separate from
prompts used to test skill selection; asking the agent to record defeats a no-reminder test. Use approved test projects,
models, tools, and budgets; this document does not authorize paid comparison runs.

## Contract Review Cases

Inspect the skill, supplied instructions, references, and template together. Static review establishes whether the
required behavior is specified, not whether a model will follow it.

| Case                                                                    | Expected behavior                                                                                                                                              |
| ----------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Substantive task with independent lookup; no delegation/logging request | Consider skill before choosing direct or delegated work; no spawn quota.                                                                                       |
| Trivial direct edit or single authoritative line                        | Use ordinary tools; no mandatory subagent or per-operation record.                                                                                             |
| First authorized delegation, absent file                                | Initialize project-root `.agents/delegation.md` and pending decision before dispatch without waiting for a lesson.                                             |
| Tracked record conflicts with a clean-checkout launch precondition      | Retain pending fields in permitted session state, launch once, then persist the attempt or failure; never weaken the launch precondition.                      |
| Old hints-only file, nested working directory, explicit override        | Preserve human content; extend the approved project file rather than choose the shell directory or a second destination.                                       |
| Completion omits usage; known status exposes it                         | Read completion, perform one bounded exposed lookup, retain source/values without a reminder.                                                                  |
| Unreported metric, failed lookup, or skipped collection                 | Keep unknowns with distinct reasons; do not invent values or label a skipped lookup unavailable telemetry.                                                     |
| Successful unchanged use, no new lesson                                 | Save statistics and parent assessment even when no hint changes.                                                                                               |
| Launch failure, cancellation, discarded/unused output                   | Retain decision, attempts, known charges and missing reasons; do not equate cancellation with stopped work or zero cost.                                       |
| Two children, one retry, duplicate/late notice                          | Keep identifiable children/attempts under one decision; update existing identities instead of adding executions.                                               |
| Cheap child needs substantial parent repair                             | Separate child quality from final acceptance; record repair after it happens and do not claim whole-task savings with missing material costs.                  |
| Shared parent review, restored history                                  | Use group attribution and provider inclusion semantics; do not count historical or overlapping totals twice.                                                   |
| Interrupted assessment, next session                                    | Read pending IDs and reconcile when skill activates; retain unresolved gaps, do not relaunch to recreate metrics.                                              |
| Missing authority or unwritable approved file                           | Disclose persistence gap, preserve permitted session evidence; no silent relocation, permission expansion, or repeated approval for already-authorized writes. |
| Concurrent session/human edit                                           | Re-read and reconcile known conflicts; preserve unrelated content and confirm the write.                                                                       |
| Consolidated successes plus failure and missing costs                   | Preserve membership/counts, scope, missingness and counterevidence; pending entries remain identifiable and no fabricated rates/quantiles.                     |
| Fresh session with applicable hint, then contrary evidence              | Apply within scope/pins; retain new observation and keep/adjust/revert on evidence without mandatory rule change.                                              |
| Authorized multi-project review                                         | Read observations and hints; retain provenance/counterevidence and propose reviewed shared changes without automatic raw-data publication.                     |

## No-Reminder Host Check

1. Adopt the skill and project section in an approved test project. Check description discovery, standing-instruction
   loading, and write access to the designated file. Record host and skill revisions.
2. Give an ordinary substantive task with a plausible independent subtask. Do not mention this skill, subagents,
   telemetry, or logging. Inspect whether the skill is considered before execution. Direct execution can be correct;
   that outcome does not exercise post-delegation recording.
3. In an ordinary task that actually delegates, compare runtime IDs with project observations. Check pending creation,
   bounded statistics retrieval, subsequent parent assessment, and persistence without prompting. Use existing failures
   and cancellations where available; do not cause expensive failures merely to complete a table.
4. Start a fresh session on a comparable task without copied prior conversation. Verify reading/applicability judgment
   for existing hints and retention of the new outcome. Inspect actual settings/handoff, not just claimed hint use.
5. Mark observed/not-observed/not-exercised with evidence. Separate activation, collection, persistence, and assessment
   failures. If runtime inventory is exposed, report record and terminal-assessment coverage against it; otherwise
   describe checked cases, not complete capture.

Static review and token counts do not replace host checks. This change installs no hooks/adapters and promises no
collection after a session is terminated.
