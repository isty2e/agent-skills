# Adaptive Delegation

Choose useful subagent work, match model/effort to the task, and check returned evidence. Statistics collection is opt-in.

## Setup

Keep this directory intact in your host's skill path. Merge [assets/AGENTS.section.md](assets/AGENTS.section.md) into
the instructions that host actually reads; do not replace existing project policy. When upgrading, replace the old
adopted delegation section too: its per-run recording requirements otherwise remain in force. No recorder dependencies
or record-file setup are needed for ordinary delegation. This skill adds no launcher, server, hook, or background collector.

## Delegation Policy

Prefer read-only research, diagnosis, and verification. Keep implementation with the parent by default; delegate bounded
work when its expected benefit outweighs briefing, verification, integration, and likely rework. Choose model/effort by
task difficulty and parent checking burden. See [selection guidance](SKILL.md#1-find-a-candidate-and-decide) and
[model starts](references/model-starting-points.md).

## Routine Use

1. Choose a useful independent task, or work directly when handoff/checking would repeat the work.
2. Reuse an applicable approved profile. Check unresolved support or material changes, not every setting on every launch.
3. Provide the objective, inputs, allowed actions, constraints, expected result, and completion criteria.
4. Use the native harness, check returned evidence, and account for the child's actual completion, stop, or handoff.

When collection is inactive, do not call `prepare`, `record-run`, `assess`, or `record-direct`, look up telemetry, or
create/reconcile a statistics file for routine work. Project hints may be used or revised when useful;
`.agents/delegation.md` is not a launch prerequisite.
Trying another model, a failed child, or an existing record block does not activate collection.

## Optional Statistics Collection

Activation sources, scope, and termination are defined in
[the collection policy](SKILL.md#6-optional-statistics-collection). Existing records can be analyzed without starting new
collection. The recorder, status helper, schemas, and tests are retained; no activation flag or runtime blocker is added.

For requested collection, the recorder needs Python 3.11+ and `jsonschema` 4.x. `uv run scripts/delegation.py ...` uses
the inline dependency metadata; alternatively install `jsonschema>=4.23,<5` once and run with Python. Dependency
installation may require network access; the recorder itself has no network operations.

Follow [recording-tool.md](references/recording-tool.md) for stage calls, examples, and preservation rules. Use the known
project root and approved record path; the tool never searches upward or scans home directories. It updates one managed
JSONL block while preserving hints and legacy records. Requested settings never fill effective settings, and unknown
metrics or usefulness remain unknown rather than becoming zero or inferred savings.

## Storage And Export

Record and attempt IDs are generated. Repeated run updates merge by identity without adding token counts; late metrics
preserve assessment. Explicit corrections retain prior assessments. Existing prose is neither imported nor counted, and
old records remain readable. Do not log the same run once as prose and again as a new staged record.

`export` writes one `adaptive-delegation/staged-record` JSON file per record, including failed/pending delegations and
representative direct choices. Direct choices have no child attempts or inferred counterfactual metrics. It does not
convert or replace the legacy YAML-frontmatter Markdown format in `subagent-stats`. Use an approved new-format output
subdirectory; Git synchronization and any future format migration are separate. Local export is not remote submission or
automatic redaction. Check task text and optional source labels before sharing.

Storage, correction, and export are optional measurement operations, not routine closeout requirements. Existing data
needs no deletion or migration. Keep current hints in the approved project file and update them only when useful;
shared-skill changes and publication require separate authority.

## Checks And References

When maintaining the recorder, from this skill directory with its dependency installed:

```bash
python -m unittest discover -s tests -v
node --test tests/test_pi_status.mjs
```

- [SKILL.md](SKILL.md): ordinary delegation and explicit collection activation.
- [references/recording-tool.md](references/recording-tool.md): optional recording workflow and CLI examples.
- [schemas/record.schema.json](schemas/record.schema.json): canonical schema, stage fields, and validation enums.
- [references/measurement.md](references/measurement.md): units, missingness, cache and cost semantics.
- [references/model-starting-points.md](references/model-starting-points.md): optional model starts; not changed by the
  recorder.
- [references/tuning.md](references/tuning.md): project evidence, hint ownership, and shared review.
- [templates/delegation.md](templates/delegation.md): human hint area, without a per-run report template.
- [evaluations/recording.md](evaluations/recording.md): default non-collection and explicit collection host checks.

Script tests do not establish host activation behavior. Static review does not prove that an agent follows the opt-in rule.

[MIT](LICENSE).
