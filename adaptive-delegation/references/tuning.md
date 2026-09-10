# Local Routing Improvement

Use task observations to improve the next choice, not to build universal rankings. Parent assessments are fallible;
retain uncertainty and corrections. Keep vendor guidance, operator reports, and proposed trials distinct from measured
local outcomes; none supplies missing success or cost data.

## 1. Diagnose The Observed Result

Compare the original primary benefit and acceptable burden with the observed outcome, including parent repair. A
successful final task does not by itself vindicate the delegation choice. Use artifact checks and observed work, not
confidence alone; retain uncertainty where the benefit was not observed. Consider the handoff and task partition before
attributing an outcome to the model. Candidate tests below are hypotheses, not mandatory actions:

- **Missing contract/source:** Fix the handoff; retain the profile for a discriminating retry.
- **Repeated reasoning errors with adequate context:** Adjust supported effort or profile/model.
- **Conflicting edits, unresolved shared decisions, expensive integration:** Repartition or keep coupled work with the
  parent.
- **Unsupported feature, outage, timeout, tool failure:** Diagnose runtime/tool availability, not reasoning.
- **Re-reading history or low information value:** Reconsider context, output contract, or direct execution.
- **Valid useful output but excessive cost/delay:** Compare a cheaper/faster profile, effort, context, or concurrency.

Availability fallback need not solve task difficulty. Inspect write state before replay and retain original
budget/permissions. One outcome supports a scoped observation, not universal superiority or incapacity.

## 2. Choose An Informative Next Observation

Default to one ordinary execution and lightweight records, not shadow runs or an evaluator agent. Consider both child
runs and representative cases kept with the parent. Direct work can reveal its own checking burden and how much useful
context was already at hand. Unperformed briefing or integration remains estimated; an unrun child provides no measured
counterfactual. Use [measurement.md](measurement.md) for comparison boundaries and attribution.

Do not treat the current choice as proven optimal merely because alternatives lack universal evidence. Repeated major
rework or rejection can justify a narrowly scoped alternative on the next ordinary task. Record intentional trials as
`model_selection_reason: exploration`; do not manufacture an experiment on every run or enforce model-diversity quotas.

Test alternatives on a small, explicitly budgeted share of eligible reversible tasks within authority. Where feasible,
vary one suspected factor with unchanged requirements/acceptance. Additional duplicate runs need an information goal and
experiment allowance. Compare existing settings too; alternative failure is not global disqualification.

Compare task family/profile first; interpret differences using context, difficulty, scope, verification, parent
identity, and runtime changes. Observational selection can give stronger profiles harder work. For consequential
changes, prefer limited paired/comparable trials at the same revision without answer leakage. Include
failures/cancellations and relevant tail cost/time, not just successful means. Small samples can expose waste, not
establish no quality loss. When evidence is insufficient, retain the candidate and name what observation would change
the choice rather than manufacture a ranking.

## 3. Retain Experience And Revise Hints Within Authority

The coordinating parent owns records for its delegation tree; descendants return evidence. Within authorized project
scope, the parent may keep, adjust, or revert choices about direct work, partition, handoff, context, model/effort, or
concurrency. Hints cannot override instructions, pins, budgets, permissions, or acceptance.

### Use One Project File

Resolve the path from project instructions once per session: normally project-root `.agents/delegation.md`, never a
second ad hoc destination. Follow the skill's launch-precondition rule. The recorder initializes its block without
replacing existing text; the [template](../templates/delegation.md) is optional for human hints. Read before editing
hints, preserve human content, reconcile concurrent changes, and confirm the write. Without an approved writable path,
retain permitted session evidence and disclose the gap.

Keep current hints and compact attempt observations together. Preserve stable decision/run IDs, facts apart from
interpretation, pending assessments, and essential context when detailed links may expire. Do not store credentials,
full transcripts, or unnecessary confidential material. Local write authority does not authorize commits, publication,
tracking changes, or host configuration.

The script alone updates its managed JSONL block. Use `assess --correction-reason` for a changed parent verdict and
`record-run` for late scalar facts. A terminal attempt is not reopened; explicitly start a continuation/retry. Direct
choices can remain short prose outside the block. Do not generate a second narrative per structured record.

### Consolidate Without Erasing Evidence

Consolidate human hints and summaries, not raw managed records. This tool provides no deletion or compaction command.
Use summaries derived from record IDs without rewriting the underlying attempts. A future data migration needs its own
scope and validation; do not manually replace the managed block with an aggregate.

Merge only comparable observations. Preserve membership or IDs, counts and denominators, settings/skill scope,
accounting coverage, missingness, failures, corrections, and counterevidence. Keep pending entries identifiable; never
convert estimates into measurements or derive unsupported rates or quantiles.

### Revise And Recheck

For an adjustment, retain a compact entry:

- **Applies to:** task scope and relevant model/host/prompt versions.
- **Change and basis:** previous choice, proposed choice, linked observations, limitations, confidence, and material
  counterevidence. Mark a provisional hypothesis as such.
- **Recheck:** date/version, next applicable ordinary task or other observable trigger, the result to inspect, and when
  to retain, revise, or revert the change under unchanged acceptance.

Keep one current choice per scoped routing decision and preserve the previous choice for rollback. A single observation
can justify a narrow, reversible provisional adjustment, not a proven improvement or universal ranking. Keep the current
choice when appropriate; if the reason is insufficient evidence, name what would inform a change. Do not tune merely to
complete a checklist.

On the next applicable task, read the hint, check its scope and versions, and apply it only if still authorized. After
that task, compare the observed result with its recheck condition and retain, revise, or revert it. Revert a change when
evidence shows regression or unjustified added burden; record the reason without discarding earlier observations.
Additional comparison runs remain subject to the experiment allowance in §2.

Reassess after material model/provider, host, prompt/skill, task mix, price, or acceptance changes. Retain scoped old
evidence; do not pool incompatible runs. Regressions can justify narrow temporary restrictions, not blanket bans;
investigate context, decomposition, and verification.

Review compact summaries after a useful batch or material failure, not full histories per launch. Stop at the experiment
budget and report uncertainty. Savings never weaken correctness, permissions, confidentiality, or parent-only duties.
Return out-of-authority changes to the governing decision process.

## 4. Review Project Experience For Shared Guidance

Only in a separate authorized maintenance task, compare selected projects' approved observations and hints; do not sweep
home directories or cross confidentiality boundaries. Group compatible task, settings, and skill revisions while
retaining failures, repair, missingness, coverage, and contrary evidence.

Use the recorder's `export` only when gathering an authorized batch. Exported staged JSON retains the fields already
collected; do not rewrite it as a long case report. It is separate from a central repository's legacy format and
requires an approved destination. No export operation grants Git synchronization or publication authority.

A shared-skill proposal records its evidence, affected instruction, expected benefit, uncertainty, and recheck or
rollback. Submit it for explicit review; local records never authorize publication or automatic promotion. Insufficient
evidence calls for a narrower claim or a more informative observation, not an invented improvement.
