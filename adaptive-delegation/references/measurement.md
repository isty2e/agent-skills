# Measurement And Attribution

Use these definitions when analyzing existing records or collecting explicitly requested statistics. Ordinary
delegation does not require accounting or recorder calls. Runtime values come from existing harness tools; the recorder
validates supplied facts but does not discover or normalize provider APIs automatically. See
[recording-tool.md](recording-tool.md) for the opt-in workflow, calls, enums, and partial-record handling.

## Time And Missing Values

All duration fields use seconds. `elapsed_seconds` is the supplied attempt-start to observed terminal interval,
including tools/waiting where the source includes them. It is not a timeout or inference-only duration. Prepare, update,
and assess timestamps indicate recording events, never execution durations. Millisecond telemetry may be divided by
1,000 before submission; do not seek millisecond precision.

Optional `parent_work_seconds` covers attributable briefing, checking, integration, and repair for this record,
excluding children and recording. `parent_recording_seconds` covers attributable collection/recording. Both are optional
supplied measurements; no stopwatch or wall-time inference is installed. Whole-task wall time is not the sum of
overlapping child and parent durations. For fanout, leave shared parent attribution unknown rather than repeating a
group total per child.

An omitted or null metric is unknown, not zero. `missing_metrics_reason` is one short default for missing values in that
attempt: `not_reported`, `no_exposed_lookup`, `lookup_failed`, `not_attributable`, or `not_collected`. A skipped lookup
is not a failed/unavailable lookup. Leave unavailable detail unknown instead of filling every metric with repeated
prose. A short optional `metrics_source` identifies the supplied evidence; do not create a reference document for it.

## Tokens And Cache

Copy reported scalar counts; do not relabel their meaning silently. `input_token_scope` records the supplied input's
meaning:

- `includes_cache`: `input_tokens` is total input; cache counts are subsets.
- `excludes_cache`: `input_tokens` is uncached input; total input is input plus cache-read plus cache-write counts.
- `unknown`: inclusion semantics were not established; do not infer them from model or host names.

`show RECORD_ID` derives token-weighted cache-read share only when the necessary counts and input scope are known. For
`includes_cache`, divide cache-read by input. For `excludes_cache`, divide cache-read by input plus cache-read plus
cache-write. A zero denominator or unknown required count gives null, not zero. It is not a request cache-hit frequency
or a cost-saving estimate. Across attempts, aggregate compatible numerator/denominator counts, not an unweighted mean of
per-attempt ratios.

Store `output_tokens` in the source's documented scope. Do not add separately reported reasoning again when included.
This initial schema deliberately omits reasoning-only metrics and an additive `tokens_used` field. References to
original runtime records may retain further detail, but do not write a long provenance object per token category.

Repeated `record-run` calls replace supplied attempt totals, never add receipts together. A separate retry/continuation
has its own attempt; only newly consumed usage belongs there. Restored historical usage, parent totals that already
include children, and per-model totals already included in an attempt must not be counted again.

## Money And Outcome

Optional `cost_amount` requires `cost_currency` and `cost_basis`: `reported_charge`, `host_estimate`, or
`unverified_indicator`. It describes the attempt's supplied model-usage amount. Do not put session-wide or combined
parent/tool totals here. No pricing catalog, formula engine, currency converter, or quota-to-money conversion is
provided. If that scope cannot be established, omit the amount. Unknown pricing semantics can remain an unverified
indicator; that is not evidence of an actual bill. Costs from unlike bases are not automatically comparable.

The parent records `output_quality` before its own repair and `output_use` after handling the result. Runtime completion
is separate. Two favorable verdicts do not establish final task acceptance, independent review coverage, or low checking
cost. Unknown quality is a valid record, not an excluded failure. Do not force these observations into a numeric success
score or invent an unrun direct-work baseline.

Save `expected_delegation_benefit` before dispatch and `delegation_usefulness` after considering the whole record,
including retries, parent checking/repair, and recording burden. Usefulness is a parent judgment, not a monetary
estimate or a measured comparison. An unchanged correct answer need not be useful; unused output may resolve
uncertainty. Leave usefulness `unknown` when the expected benefit or total burden cannot be judged.

`record-direct` preserves a representative non-delegation choice and short reason in the same export. No child was run:
child usage and delegation usefulness do not apply, rather than being zero or a failed output. These selected direct
cases reveal conditions worth reviewing, not the denominator of all direct work.

## Later Comparisons

Retain raw records, including failures, retries, discarded outputs, and incomplete measurements; analytic eligibility
does not authorize deleting them. Select a cohort for the question before calculating a rate. Report its denominator
and exclusion counts alongside direct/delegated choices, missing usefulness judgments, and unassessed or pending
attempts. A direct choice is not an awaiting-run record.

### Usefulness Comparison Eligibility

For a model-conditioned comparison, select records attributable to one reported actual model, with terminal attempts
and a current definitive whole-delegation usefulness assessment covering those attempts. For an effort-conditioned
comparison, additionally require one reported actual effort across those attempts. Missing effort does not invalidate a
model-only comparison; missing parent-cost measurements do not invalidate observed usefulness. An empty eligible cell
has no rate, not a zero rate.

Exclude unrun records, unknown usefulness assessments, and missing/mixed attribution from both numerator and denominator.
Keep exclusion reasons and counts separate from outcomes. A whole assessment contaminated by prelaunch host failures cannot
be assigned to the model that eventually ran. Do not assign a retry/fallback's whole verdict to the initial requested
configuration, or invent a model verdict by subtracting host overhead. Keep such records for workflow interpretation.
Retain genuine post-launch failures, cancellations, incorrect output, repairs, and burden-exceeded results. Exclude
invalid attribution, not bad outcomes.

### Task Conditions And Observation Unit

Compare within task families and roles, then recorded type/difficulty and project conditions where available. A specified
reproduction check is not open review. Use recorded pre-run difficulty; do not infer missing difficulty from length or
relabel it after failure. Missing difficulty excludes a record only from the difficulty-conditioned comparison, not
type-only analysis. Same broad labels still do not establish matched tasks. Compare usefulness alongside original
quality and categorical repair; none alone measures savings or final acceptance.

Count a task's retries as one whole-delegation assessment. Parallel subtasks and resumed tasks may be correlated; do not
assume independent replications. A reused native ID is not by itself proof of duplicate tasks. Preserve task/attempt
identity and known continuation windows. Pinned profiles describe requested workflow, not autonomous routing. Account for
context, scope, verification, parent identity, and runtime changes; stronger profiles may receive harder work.

### Cost And Policy Interpretation

Compare compatible effort/context, usage scopes, and cost bases, including failures, retries, discarded outputs, and
recording overhead wherever attributable. Missing parent costs that could reverse a comparison prevent whole-task cost
ranking; a component comparison must remain labeled as such. These sparse records support narrower questions before
end-to-end savings claims.

Project hints remain separate from raw records even in the same file. Read [tuning.md](tuning.md) before changing policy.
Export is a mechanical, separately authorized local copy, not a requirement to write a standalone narrative. No
statistic alone authorizes sharing private project information.
