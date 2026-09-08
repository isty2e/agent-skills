# Measurement And Attribution

Reuse runtime events and approved task records. Runtime owns usage/lifecycle facts; the parent owns assessment. Record
available facts without requiring unsupported fields or inventing values.

## Start With The Decision Record

For ordinary work, link the task and any attempts to a compact record:

- the candidate, primary expected benefit, acceptable extra burden, and direct/delegated choice with its selection basis
- reported effective settings and any requested/effective differences
- evidence/artifact references, execution outcome, parent assessment, and final acceptance
- available usage/time, failures and repair burden, with unknowns and attribution limits
- whether the original expectation was met, the supporting evidence, and the next choice: keep, adjust, revert, or
  gather more evidence; link any local hint revision.

Reuse existing task records and references rather than copying them into a second log. The project hint file retains
current choices and concise evidence, not every execution record. For a representative candidate kept with the parent,
record why, actual burden if observed, and when to reconsider delegation. Do not record every direct operation or run a
child merely to populate a baseline. An unrun alternative has an estimate, not an observed outcome.

The skill's first-run example illustrates this record. Use the detail below when establishing collection or making
comparisons; a short routine record is not evidence for claims it cannot support.

## Add Detail For Comparisons

Record task/delegation ID, linked attempts, and available facts needed to reconstruct the comparison:

- **Task:** Family, objective/acceptance reference, revision/state, primary expected benefit and acceptable extra
  burden, relevant scope/verification difficulty, routine/experimental selection, and selection basis/source: local
  measurement, operator report, vendor guidance, or proposed trial.
- **Configuration:** Host/version, parent/child identities, profile/settings version, requested/effective
  model/provider/version or unresolved alias, effort, service tier, fresh/fork/resume, permissions/limits, and override
  reason.
- **Execution:** Start/end, terminal status, attempts/fallback/descendants, and artifact/check references.
- **Usage:** Input/output and reported cache/reasoning categories with inclusion semantics, currency/cost source or
  quota measure, and completeness/missing fields.
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

Keep source records separate from derived summaries. Deduplicate delivered results by stable event/attempt IDs. Without
durable storage or usable telemetry, retain permitted notes and disclose limits. Use [tuning.md](tuning.md) to interpret
these observations before changing routing.
