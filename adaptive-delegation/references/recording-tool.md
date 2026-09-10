# Staged Recording Tool

One local recorder, not a runner or host adapter. Python 3.11+ with `jsonschema>=4.23,<5`; `uv run` can resolve the
inline script dependency. Use the approved project root and one record path throughout the session. Never discover
credentials, model catalogs, or telemetry by scanning directories. No acceptance document or local acceptance reference
is required.

## Normal Path

Set these to already-known paths. The shell function avoids repeating them; it creates no persistent configuration.

```bash
SKILL_DIR=/path/to/agent-skills/adaptive-delegation
PROJECT_ROOT=/path/to/project
record() { uv run "$SKILL_DIR/scripts/delegation.py" --project-root "$PROJECT_ROOT" "$@"; }

record prepare --task-type verify --task-description 'Check active-bound derivatives.' \
  --requested-child-model 'provider/model-id' --requested-child-effort high \
  --requested-context fresh --model-selection-reason exploration --expected-delegation-benefit reduce_context
```

The model above is a placeholder, not a recommendation. Reuse the returned `record_id` (shown below as `$RECORD_ID`).
Run the child with the native harness. Do not generate another task or acceptance description for recording.

```bash
record record-run "$RECORD_ID" --run-id "$NATIVE_RUN_ID" --execution-status completed \
  --elapsed-seconds 92 --input-tokens 18000 --output-tokens 2100

record assess "$RECORD_ID" --output-quality incomplete --output-use used_after_local_fix \
  --delegation-usefulness unknown --note 'Parent added the omitted active-bound case.'

record show
```

The usefulness value is a parent judgment against the original purpose, including all retries and parent work; the
example leaves it unknown instead of inferring it from output quality. Add it to the final output assessment, not
another mandatory command. Use `show` once at task closure, not after every child or successful write.

The numbers are synthetic examples. Supply only actual reported values. Omit unavailable measurements; if known, use
`--missing-metrics-reason not_reported`, `no_exposed_lookup`, `lookup_failed`, `not_attributable`, or `not_collected`.
`--metrics-source` is an optional short label, not a request to create evidence documents. Do not turn a missing field
into an investigation. Commands report short JSON, not the stored record. `show RECORD_ID` explicitly requests detail.

Global `--project-root` and optional `--record-file` precede the subcommand. `--record-file` defaults to
`.agents/delegation.md` under that root; relative overrides use the same root. The root must already exist. Choose an
override only when authorized, not as a silent fallback after a write failure.

For any write stage, `--json FILE` or `--json -` accepts a flat JSON object containing the same underscore-named fields
as the flags. Flags may add distinct fields; specifying one field twice is an error. This permits reuse of existing
structured inputs without generating a JSON document as a separate task. Omission preserves prior values; explicit null
clears a nullable measurement. No automatic host discovery or provider-specific import is included.

## Which Stage Owns Which Fields?

| Stage           | Required input                                                                          | Useful optional input                                                                                                          | Automatically filled                                               |
| --------------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------ |
| `prepare`       | `task_description`, `task_type`, `requested_child_model`, `expected_delegation_benefit` | Parent model/effort, host, workspace task, domains, estimated difficulty, requested effort/context, selection reason, group ID | Record ID, revision, timestamps, default project name              |
| `record-direct` | `task_description`, `task_type`, `direct_reason`                                        | Known workspace/parent/task metadata                                                                                           | Identity, timestamps, direct mode; no child attempts               |
| `record-run`    | Record ID and at least one reported field                                               | Native run ID, status, effective child settings, seconds, token/cache counts, cost and its basis                               | Internal attempt ID; merges without adding counters                |
| `assess`        | Record ID and an output pair or `delegation_usefulness`                                 | Both output verdicts and usefulness together on the normal final call; short note and observed parent seconds                  | Assessment timestamp; correction history when explicitly requested |
| `export`        | Approved local destination                                                              | Record IDs to select; otherwise all managed records                                                                            | Validated JSON files named by record ID                            |

`prepare` records a selected delegated task, not every possibility considered. A distinct parallel task gets a separate
record; use the same optional `group_id` to group a fanout. Retries/continuations stay in the original record. Do not
repeat shared parent work in every fanout record; leave attribution unknown unless separable.

### Representative Direct Choices

When delegation was seriously considered but direct work was preferable, record once:

```bash
record record-direct --task-type lookup --task-description 'Read the already located option.' \
  --direct-reason 'Briefing and checking would duplicate one short source read.'
```

`execution_mode: direct` records have no child fields, attempts, or delegation assessment. They are exported but never
counted as missing runs, failed children, or zero-cost alternatives. No `record-run` or `assess` follows; those commands
reject direct records. If a later task is delegated, use a new `prepare` record rather than changing this past choice.
Keep `direct_reason` to 200 characters. Do not log all direct work, require hypothetical child settings/costs, or infer
population-wide non-delegation rates from representative cases. Existing prose remains untouched, not auto-imported.

Common context such as parent settings can be supplied from an already-known session value, but the script does not
infer them. Absent effective settings remain unknown; first-attempt requested settings come from `prepare`. A later
attempt's request is unknown unless explicitly supplied with `--requested-child-model`, `--requested-child-effort`, and
`--requested-context`. No model names or effort values are automatically substituted.

## Small Classification Vocabulary

- `task_type`: `lookup`, `summarize`, `investigate`, `implement`, `review`, `verify`, `other`. Review finds candidate
  problems; verify checks an already specified claim or behavior. Choose the primary purpose.
- `estimated_difficulty`: optional `routine`, `reasoning_required`, `open_ended`. This is a pre-run estimate, not a
  label revised after failure. Domain tags are optional free strings, not an exhaustive taxonomy.
- `model_selection_reason`: `default`, `previous_results`, `exploration`, `explicit_instruction`, `unknown`. It explains
  the model/effort choice, not the output verdict. A model explicitly present in a tool call does not imply a user pin.
- `execution_status`: `running`, `completed`, `failed`, `cancelled`, `unknown`. A cancellation request is not an
  observed stop; keep the state running/unknown until the harness reports termination.

### Delegation Purpose And Usefulness

`expected_delegation_benefit` is the primary purpose, chosen before execution: `save_time`, `save_cost`,
`reduce_context`, `independent_check`, or `explore_options`; `unknown` is allowed when the original expectation was not
retained. It is distinct from why a particular model was selected. Record it in `prepare`; never invent it
retrospectively from success.

`delegation_usefulness` belongs to the entire record, including retries and parent checking, repair, and recording:

| Value                     | Meaning                                                                                          |
| ------------------------- | ------------------------------------------------------------------------------------------------ |
| `helpful`                 | Parent judges that useful contribution justified the total burden under the original purpose     |
| `no_benefit`              | No meaningful contribution was observed, without clear evidence of excess burden                 |
| `burden_exceeded_benefit` | Parent judges that extra burden outweighed the contribution                                      |
| `unknown`                 | Available evidence does not support that judgment; never infer helpfulness from a correct output |

These are ordinal judgments, not measured savings or a numeric success score. An unchanged correct answer may duplicate
parent work; unused output may resolve uncertainty. Keep any note short and optional. Missing costs need not prevent a
scoped usefulness judgment, but a cost-saving claim still needs comparable accounting.

Normally include usefulness in the final `assess` call with output verdicts. For intermediate attempts, record output
only; after retries, judge the whole task, not just the best attempt. It can also be supplied alone without repeating
output flags or an attempt selector. Nonterminal runs allow only `unknown` and remain pending for review.

### Parent Output Verdicts

`output_quality` refers to the original returned artifact, before parent repair:

| Value                | Meaning                                                                        |
| -------------------- | ------------------------------------------------------------------------------ |
| `meets_requirements` | Checked output meets the delegated request                                     |
| `incomplete`         | Required parts are missing; no material error established in the provided part |
| `incorrect`          | A material error was found; takes precedence over simple omissions             |
| `unverified`         | Not enough checking/evidence to classify the output                            |
| `no_output`          | No artifact exists to assess                                                   |

`output_use` records actual handling:

| Value                     | Meaning                                                        |
| ------------------------- | -------------------------------------------------------------- |
| `used_as_is`              | Used without material changes                                  |
| `used_after_local_fix`    | Core approach preserved; local fixes or additions              |
| `used_after_major_rework` | Parent substantially re-solved or rebuilt the core approach    |
| `rejected`                | Not adopted because it was unsuitable                          |
| `not_used`                | Unused for another reason, such as duplication or cancellation |
| `pending`                 | Use has not been decided                                       |
| `no_output`               | Nothing exists to use                                          |

These are judgments, not proof. `incorrect` with `used_as_is` may describe an error discovered later; the validator must
not erase that evidence. A failed run can return useful partial output. Checking time is separate from the amount of
repair. No global success score or final user-task acceptance is derived from these two enums. Notes are optional and
limited to 200 characters, not a mandatory rationale field.

## Partial Records, Retries, And Corrections

`record-run` updates by internal `--attempt-id`, native `--run-id`, or the sole existing attempt. It copies cumulative
values for that attempt; it never adds a repeated receipt's counters. Prefer `--attempt-id` after it is returned.

```bash
# A launch can fail before a native ID exists.
record record-run "$RECORD_ID" --execution-status failed --missing-metrics-reason no_exposed_lookup

# Start a distinct retry; FIRST_ATTEMPT is the internal attempt ID returned above.
record record-run "$RECORD_ID" --new-attempt --retry-of "$FIRST_ATTEMPT" \
  --run-id "$RETRY_RUN_ID" --execution-status running --requested-child-model 'provider/model-id'
```

Use `--attempt-id` to attach a subsequently learned native ID to an unidentified attempt. A new distinct native run ID
normally creates an attempt; if an unidentified attempt already exists, explicitly choose binding it or `--new-attempt`.
A resumed native run may reuse its ID: use `--new-attempt --retry-of ...`, then the new internal attempt ID. Multiple
attempts with the same native ID require the internal selector. Record only newly consumed usage for a continuation;
this script cannot subtract restored history or discover provider-side fallback calls.

A terminal attempt is not reopened. Duplicate terminal receipts are harmless; late metrics may still be added after
assessment. Changing a stored assessment requires `--correction-reason 'short explanation'`; the prior verdict is kept.
Repeated identical assessments are no-ops. Whole-delegation review stores its covered attempt IDs; a later retry makes
that review pending. Reassessment of expanded coverage preserves the previous review automatically. A changed output
assessment without a new usefulness judgment archives the previous utility review and marks it pending; late metrics
alone do not erase either judgment. Revising usefulness for the same attempts requires the same correction reason. An
omitted note preserves the prior note; JSON null explicitly clears it. No artifact output or incomplete statistics is
not a reason to omit the attempt.

`show` and `validate` list missing output assessments, nonterminal attempts, awaiting runs, and
`delegation_review_pending`. Direct records are identified separately, never awaiting runs. Older staged records without
`execution_mode` still mean delegate; absent expected benefit or usefulness remains unrecorded, not inferred. These
counts cover only tool-managed records, not legacy prose or unobserved host executions. `validate` requires well-formed
data, not complete metrics or a successful output.

## Export Later, In A Batch

```bash
record export --destination /approved/subagent-stats-checkout/staged-json
# Or select a record; --record-id may be repeated.
record export --destination /approved/export-dir --record-id "$RECORD_ID"
```

Exports include pending and failed delegations, their purpose/usefulness, and representative direct choices. No Markdown
narrative is generated. This is staged-record JSON format 1, identified by `format: adaptive-delegation/staged-record`;
it is not `subagent-stats`' legacy format 1. Existing Markdown files are untouched and no migration is attempted. No
credentials, network sync, Git commits/pushes, or automatic redaction. Use the existing authorized sharing process after
reviewing optional text and source labels.

Existing identical exports are unchanged. A newer conflicting destination revision, equal-revision divergence, or
identity mismatch is rejected. Multi-file exports are atomic per file, not a batch transaction; after an I/O failure,
safely rerun. Cross-machine Git conflicts remain outside this tool.

## Validation And Local Writes

The canonical [JSON Schema](../schemas/record.schema.json) supplies fields, enums, and CLI field help. `schema prepare`,
`schema record-direct`, `schema record-run`, or `schema assess` prints the stage-input schema; no root is needed. Do not
routinely load this large schema into the model context. `--help` is the short field reference.

Unknown keys, duplicate JSON keys, conflicting flags/JSON, negative/nonfinite numbers, and invalid enums fail with exit
status 2. Record errors are JSON on stderr; argument syntax errors use standard CLI diagnostics. Successful mutations
return a short receipt. Output verdict corrections preserve history; ordinary metric updates replace supplied fields.

One managed JSONL block in `.agents/delegation.md` is validated before each update. UTF-8 text outside it is preserved.
Writes use a cooperating-process lock and a temporary-file replacement; observed outside changes are rejected. This is
not protection against a non-cooperating editor racing the final replacement, network-filesystem locking anomalies, or
power-loss recovery. Do not edit the file simultaneously by hand. A crashed writer may leave a `.lock` file; verify its
owner is no longer writing before removing that lock manually. Record/export symlink files and malformed managed blocks
are refused. No broad filesystem migration or backup manager is included.
