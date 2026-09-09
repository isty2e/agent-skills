# Measurement And Attribution

Runtime owns usage/lifecycle facts; the parent owns collection and assessment. Keep compact experience in the approved
project file, normally `.agents/delegation.md`; link detailed runtime records. Record available facts without requiring
unsupported fields or inventing values.

## Collect Without A Reminder

Identify exposed result/status/artifact sources and parent-usage coverage before the session's first delegation; reuse
that lookup plan until relevant host/settings changes. Resolve the approved project file under [tuning.md](tuning.md).

1. **Before dispatch:** save a project-unique decision ID, scope, expectation, and intended settings as pending. If the
   write would violate an enforced launch precondition such as a clean source checkout, keep those fields in permitted
   session state, launch once, then persist immediately with the returned attempt ID or failure. Never weaken the
   precondition. Attach later child/attempt IDs; record launch failure even without a child ID.
2. **Result/failure/cancellation:** read returned usage, then make one bounded exposed lookup for missing fields. Retain
   source, outcome, units, and inclusion scope. Do not poll for telemetry or scan unrelated sessions. Update late facts
   under existing IDs; notifications are not executions.
3. **After verification/repair:** add the parent assessment, effective settings, actual use, final acceptance or pending
   reason, and next choice to the same entry. Read exposed attributable parent usage; do not guess missing costs.
4. **Before reporting/handoff:** reconcile known runs and records; confirm the save or disclose its failure. Revisit
   pending entries on the next activation without relaunching work. If a runtime inventory is exposed, compare against
   it; otherwise report checked cases rather than claiming full capture.

Record whether collection was attempted. For each missing metric distinguish not reported by the checked source, no
exposed lookup, lookup failure, attribution unavailable, or not attempted. Skipping a lookup does not prove missing
telemetry. Do not repeat failed lookups without new evidence. Missing metrics or persistence do not block the work
result: preserve permitted session evidence and disclose the gap; do not silently choose another persistent location.

## Start With The Decision Record

For ordinary work, link the task and any attempts to a compact record:

- the candidate, primary expected benefit, acceptable extra burden, and direct/delegated choice with its selection basis
- reported effective settings and any requested/effective differences
- evidence/artifact references, execution outcome, parent assessment, and final acceptance
- available usage/time, failures and repair burden, with unknowns and attribution limits
- whether the original expectation was met, the supporting evidence, and the next choice: keep, adjust, revert, or
  gather more evidence; link any local hint revision.

Retain this compact record for every launch attempt, not only successful or informative runs, in the same project file
as current hints. Use [the template](../templates/delegation.md); update it even if the hint stays unchanged. Link full
artifacts without copying transcripts or depending on expiring links for essential facts. Do not retrospectively invent
pre-run expectations. For a representative direct choice, retain why, observed burden, and when to reconsider. Do not
record every direct operation or launch a child to populate a baseline. An unrun alternative is not an observed outcome.

The skill's first-run example illustrates this record. Use the detail below when establishing collection or making
comparisons; a short routine record is not evidence for claims it cannot support.

## Add Detail For Comparisons

Record task/delegation ID, linked attempts, and available facts needed to reconstruct the comparison:

- **Task:** Family, objective/acceptance reference, revision/state, primary expected benefit and acceptable extra
  burden, relevant scope/verification difficulty, routine/experimental selection, and selection basis/source: local
  measurement, operator report, vendor guidance, or proposed trial.
- **Configuration:** Host/version, parent/child identities, profile/settings version, requested/effective
  model/provider/version or unresolved alias, skill revision, effort, service tier, fresh/fork/resume, concurrency,
  permissions/limits, and override reason.
- **Execution:** Start/end, terminal status, attempts/fallback/descendants, and artifact/check references.
- **Usage:** Input/output and reported cache/reasoning categories with inclusion semantics, currency/cost source or
  quota measure, completeness/missing fields, collection attempts/sources/outcomes, and missing-value reasons.
- **Parent:** Contract assessment, use/disposition, evidence, usefulness, repair burden/diagnosis, expectation versus
  outcome, next choice or hint revision, and later corrections.

Keep decision-relevant metadata/references in approved storage, not credentials or unnecessary confidential prompts,
source, or transcripts. Scope aggregates to authorized project/account; cross-boundary sharing requires permission.

Use **unknown** for an applicable fact that was not reported or cannot be measured, including unsupported reporting. Use
**not-applicable** only when the fact does not apply, such as a child identity for a direct-only task. **Zero** means
observed zero. Keep measured values, estimates, and unavailable attribution distinct; lack of telemetry does not make
incurred cost inapplicable.

## Account For The Whole Task

Compare the same task boundary and starting state through acceptance or terminal failure. Include parent briefing,
children, checking, integration, repair, failures, cancellations, abandoned attempts, retries, fallback, available tool
charges, and authorized descendants. Measure direct-parent baselines identically; do not log only successful children.
Without a comparable baseline, natural logs describe cost, not savings.

Check accounting coverage as well as task comparability. Do not rank whole-task cost or claim savings when differences
in included costs or missing usage could reverse the conclusion. A run missing parent repair cost is not directly
comparable to one that includes it. You may compare equally covered components with that scope stated, but do not
present a component advantage as a whole-task advantage. Keep estimates separate and unresolved total cost unknown;
other observed benefits can still inform a bounded routing choice.

Count each newly billed event once. Restored history is not new usage; resubmitting it may incur input charges. Check
whether session/parent totals already include children/tools before adding components. Preserve provider inclusion
semantics when combining input/cache/reasoning/output. Mark incomplete totals; never replace missing usage with zero.

Attribute shared parent review to the group unless finer allocation is observed; equal division is not measured
attribution. Separate measurements from marginal-overhead estimates. Record child duration and elapsed task time to
acceptance/failure separately; summing parallel durations does not give wall time. Record blocked parent waiting only
when observable.

Distinguish reported charges, published-rate estimates, and subscription quota. Estimates need price/version/date and
units; quota is not API dollars. Compare currencies/quota systems only through explicit valid conversion. Require
observed usage for cache benefit, not fresh/fork assumptions.

## Summarize Without Hiding Failure

State rate units/denominators. Group retries by task for task rates; show attempt outcomes separately.

For comparable groups, report acceptance, unchanged-use and substantial-rework rates, cost per accepted task, elapsed
time, and failure/timeout counts. Divide all observed costs, including failures, by accepted tasks. With none accepted,
report undefined, total cost, and failures. Preserve completeness caveats. Show child assessment alongside final
acceptance so parent repairs do not hide failure.

Keep observations distinct from derived hints even in the same file. Deduplicate by decision/run/attempt IDs, including
membership retained in consolidated summaries. Preserve counts and missingness; do not pool incompatible settings or
accounting coverage. Report pending/unassessed runs separately and state the terminal cohort used for acceptance rates.
A completed-cohort rate must not conceal excluded observations. Use [tuning.md](tuning.md) before consolidating or
changing routing; missing records preclude a claim of complete capture.
