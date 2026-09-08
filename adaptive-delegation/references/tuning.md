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

Test alternatives on a small, explicitly budgeted share of eligible reversible tasks within authority. Where feasible,
vary one suspected factor with unchanged requirements/acceptance. Additional duplicate runs need an information goal and
experiment allowance. Compare existing settings too; alternative failure is not global disqualification.

Compare task family/profile first; interpret differences using context, difficulty, scope, verification, parent
identity, and runtime changes. Observational selection can give stronger profiles harder work. For consequential
changes, prefer limited paired/comparable trials at the same revision without answer leakage. Include
failures/cancellations and relevant tail cost/time, not just successful means. Small samples can expose waste, not
establish no quality loss. When evidence is insufficient, retain the candidate and name what observation would change
the choice rather than manufacture a ranking.

## 3. Revise Scoped Hints Within Authority

The parent owns hint updates; children may supply evidence or proposals. Within the approved local scope, the parent may
keep, adjust, or revert a hint without seeking permission for each update. Eligible changes include choosing direct
work, repartitioning, revising handoffs, and selecting allowed context, model/effort, or concurrency settings. Hints
cannot override pins, budgets, permissions, acceptance, or governing instructions. Changes outside that scope require
authorization rather than a self-assessment score.

### Use One Project File

Resolve the hint path from project instructions. When they adopt the default, use `.agents/delegation.md` relative to
the project root they govern, not the shell's current directory. Honor an explicitly designated alternative instead of
creating a second file. If the project root or authority is unclear, clarify before writing; without an approved file,
keep session-local notes and disclose the persistence limit.

Read the existing file before editing and preserve unrelated entries and human-authored content. If absent and creation
is authorized, initialize it from the [project hint template](../templates/delegation.md) when there is a useful
observation to retain. An empty file supplies no learned preference. Never overwrite an existing file with the template;
reconcile concurrent edits rather than replacing another session's work. Local update authority does not authorize
committing, publishing, or changing tracking policy.

Keep current routing decisions with concise evidence, counterevidence, and rollback context, not an append-only run log.
Link approved task records for detail; retain enough evidence in each hint to interpret it if a temporary report
expires. Local hints guide choices; editing the host's execution configuration still requires authority for that
surface.

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
