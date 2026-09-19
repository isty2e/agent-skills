# Local Routing Improvement

Improve the next choice, not universal rankings. Parent judgments are fallible: retain uncertainty and corrections.
Distinguish measured outcomes from vendor guidance, operator reports, and proposed trials; none fills missing cost or
success data.

## 1. Diagnose The Observed Result

Compare the recorded expected benefit and acceptable burden with observed whole-delegation usefulness, including parent
repair. Use artifacts and observed work, not confidence, output quality, or final task success alone. Unknown usefulness
is neither failure nor proof of savings. Consider handoff and partition before attributing outcomes to the model.

Within each task, separate useful content, substantive errors, local formatting/metadata repair, and execution/receipt/
retry overhead. Preserve original outcomes and incurred costs, including mixed failures; invent no harness-free success
rate. Candidate next steps are hypotheses, not obligations:

- Missing contract/source: distinguish unavailable inputs/tools from failure to retrieve/ground evidence; adjust handoff,
  runtime, or profile accordingly.
- Repeated reasoning errors with adequate context: adjust supported effort/profile/model.
- Conflicting edits, unresolved shared decisions, costly integration: repartition or keep coupled work with the parent.
- Unsupported feature/outage/timeout/tool failure: distinguish runtime faults from child tool choices or ignored
  constraints; both may contribute.
- Re-reading history/low information value: reconsider context, output contract, or direct work.
- Useful but costly/slow output: compare cheaper/faster profiles, effort, context, or concurrency.

Availability fallback need not solve difficulty. Inspect write state before replay; retain budget/permissions. One
outcome supports a scoped observation, not universal superiority or incapacity.

## 2. Choose An Informative Next Observation

Default to one ordinary execution and lightweight records, not shadow runs or evaluator agents. Include representative
direct choices: they reveal checking burden and available context, but unperformed handoffs/integration remain estimates
and unrun children supply no measured counterfactual. See [measurement.md](measurement.md) for attribution/comparability.

Lack of universal evidence for alternatives does not prove the incumbent optimal. Repeated major repair/rejection may
justify a scoped alternative on the next ordinary task. Mark intentional trials `model_selection_reason: exploration`; no experiment per
run or model-diversity quota.

Default trials to eligible read-only work within budget; read-only does not mean easy. Routine lookup may warrant lower
effort; shallow multi-source investigation may warrant a stronger model or higher effort. Compare stronger/moderate-effort,
cheaper/deeper-effort, existing settings, and direct work without requiring failure first. Where feasible, vary one factor
under unchanged acceptance/requirements. Duplicate runs need an information goal and experiment allowance. Alternative
failure is not global disqualification.

Compare within task families/shared episodes, not pooled effort-level success rates. Wave lanes are correlated, not
independent replications; pinned profiles describe requested workflow, not autonomous routing/exploration. Account for
context, difficulty, scope, verification, parent identity, and runtime changes; stronger profiles may receive harder
work. Consequential changes warrant limited paired/comparable trials at the same revision without answer leakage.
Include failures/cancellations and tail cost/time, not just successful means. Small samples may expose waste, not prove
no quality loss. With insufficient evidence, retain the candidate and name an informative observation, not a ranking.

## 3. Retain Experience And Revise Hints Within Authority

The coordinating parent owns delegation-tree records; descendants return evidence. Within authorized project scope,
the parent may keep/adjust/revert direct work, partition, handoff, context, model/effort, or concurrency. Hints cannot
override instructions, pins, budgets, permissions, or acceptance.

### Use One Project File

Resolve the instruction-designated path once per session, normally project-root `.agents/delegation.md`; never relocate
ad hoc. Honor the skill's launch preconditions. The recorder preserves surrounding text; the
[template](../templates/delegation.md) is optional for human hints. Read before editing hints, preserve human content,
reconcile concurrent changes, and confirm writes. Without an approved writable path, retain permitted session evidence
and disclose the gap.

Keep hints and compact observations together, separating facts from interpretation. Preserve decision/run IDs, pending
assessments, and essential context when links may expire. Store no credentials, full transcripts, or unnecessary private
material. Local writing does not authorize commits, publication, tracking changes, or host configuration.

Only the script edits managed JSONL. Change verdicts with `assess --correction-reason`; add late facts with `record-run`.
Terminal attempts are not reopened: explicitly start a retry/continuation. For direct choices seriously considered
against delegation, use `record-direct` with a short reason so export retains them; no child model/run/hypothetical
metrics. Preserve legacy prose without automatic import. Do not add a second narrative per structured record.

### Consolidate Without Erasing Evidence

Consolidate human hints/summaries, not managed records. Reference record IDs; this tool has no deletion/compaction command.
Do not replace raw records with aggregates. Future migrations need separate scope and validation.

Merge only comparable observations. Preserve membership/IDs, counts/denominators, settings/skill scope, accounting
coverage, missingness, failures, corrections, counterevidence, and identifiable pending entries. Do not turn estimates
into measurements or derive unsupported rates/quantiles.

### Revise And Recheck

Keep each adjustment compact:

- Applies to: task scope and relevant model/host/prompt versions.
- Change/basis: previous and proposed choices, observations, limitations, confidence, material counterevidence; label
  provisional hypotheses.
- Recheck: date/version, next applicable ordinary task or other observable trigger, result to inspect, and retain/revise/
  revert criteria under unchanged acceptance.

Keep one current choice per scope and its predecessor for rollback. One observation may justify a narrow reversible
trial, not proven improvement or universal ranking. Keeping the current choice is valid; if evidence is insufficient,
name what would help. Do not tune to fill a checklist.

On the next applicable task, check the hint's scope, versions, and authority, then compare its outcome to the recheck
condition. Retain/revise/revert accordingly; regressions or unjustified burden warrant reversal without discarding old
evidence. Extra comparison runs still require §2's allowance.

Reassess after material model/provider, host, prompt/skill, task-mix, price, or acceptance changes. Keep scoped old
evidence without pooling incompatible runs. Regressions may warrant temporary scoped restrictions, not blanket bans;
investigate context, decomposition, and verification. Review summaries after a useful batch or material failure, not
full histories per launch. Stop at the experiment budget and report uncertainty. Savings never weaken correctness,
permissions, confidentiality, or parent-only duties; return out-of-authority changes to their decision owner.

## 4. Review Project Experience For Shared Guidance

In a separate authorized maintenance task, compare selected projects' approved observations/hints; no home-directory
sweeps or confidentiality crossings. Group compatible tasks, settings, and skill revisions, retaining failures, repair,
missingness, coverage, and counterevidence.

For an authorized batch, `export` to an approved local directory. Staged JSON preserves collected fields, direct choices,
and separate output/usefulness judgments; do not rewrite long case reports. It is not the central repository's legacy
format and grants no Git synchronization or publication authority.

A shared-skill proposal needs evidence, affected instruction, expected benefit, uncertainty, and recheck/rollback, followed
by explicit review. Records never authorize publication or automatic promotion. Insufficient evidence calls for narrower
claims or informative observations, not invented improvements.
