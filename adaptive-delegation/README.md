# Adaptive Delegation

Choose useful subagent work and retain project-specific experience with small, validated stage inputs.

## Setup

Keep this directory intact in your host's skill path. Merge [assets/AGENTS.section.md](assets/AGENTS.section.md) into
the instructions that host actually reads; do not replace existing project policy. The adopted section authorizes local
record updates within repository policy, not publication or changed permissions.

The recorder needs Python 3.11+ and `jsonschema` 4.x. `uv run scripts/delegation.py ...` uses the inline dependency
metadata; alternatively install `jsonschema>=4.23,<5` once and run with Python. Dependency installation may require
network access; the recorder itself has no network operations. There is no server, hook, provider adapter, background
collector, or subagent launcher.

## Routine Use

Use the project-root `.agents/delegation.md`, or one explicitly approved override. Pass the known root; the tool never
searches upward or scans home directories. It updates one managed JSONL block and preserves surrounding hints and legacy
records. Do not type or rewrite that block manually.

| Moment                         | Command      | Parent input                                                                       |
| ------------------------------ | ------------ | ---------------------------------------------------------------------------------- |
| Before dispatch                | `prepare`    | Short existing task, type, requested model; optional known settings/classification |
| After native execution         | `record-run` | Run/status and exposed scalar metrics; unknown values may be omitted               |
| After checking/repair          | `assess`     | Two output enums; optional exception note up to 200 characters                     |
| Separate authorized collection | `export`     | Approved local destination; existing records are copied as JSON                    |

`show` lists compact pending/assessment summaries, `validate` checks managed records, and `schema` prints the canonical
record or stage-input schema. Commands return short JSON and exit nonzero on invalid input. They do not require complete
telemetry. Requested configuration never fills effective configuration, and timestamps never fabricate elapsed time.

See [recording-tool.md](references/recording-tool.md) for runnable examples and enum meanings. The parent uses existing
harness tools to obtain metrics; child-side collection is not required. Script invocation still depends on the agent
following the skill. Unit tests do not establish no-reminder behavior in Pi, Codex, or Claude.

## Storage And Export

Record and attempt IDs are generated. Repeated run updates merge by identity without adding token counts; late metrics
preserve assessment. Explicit corrections retain prior assessments. Existing prose is neither imported nor counted, and
old records remain readable. Do not log the same run once as prose and again as a new staged record.

`export` writes one `adaptive-delegation/staged-record` JSON file per record, including failed/pending records. It does
not convert or replace the legacy YAML-frontmatter Markdown format in `subagent-stats`. Use an approved new-format
output subdirectory; Git synchronization and any future format migration are separate. Local export is not remote
submission or automatic redaction. Check task text and optional source labels before sharing.

Routine recording needs no new hint or essay. Keep current choices in the same project file; review accumulated evidence
and update hints only when useful. Shared-skill changes require separate authorized review.

## Checks And References

From this skill directory, with the dependency installed:

```bash
python -m unittest discover -s tests -v
```

- [SKILL.md](SKILL.md): activation and stage workflow.
- [schemas/record.schema.json](schemas/record.schema.json): canonical schema, stage fields, and validation enums.
- [references/measurement.md](references/measurement.md): units, missingness, cache and cost semantics.
- [references/model-starting-points.md](references/model-starting-points.md): optional model starts; not changed by the
  recorder.
- [references/tuning.md](references/tuning.md): project evidence, hint ownership, and shared review.
- [templates/delegation.md](templates/delegation.md): human hint area, without a per-run report template.
- [evaluations/recording.md](evaluations/recording.md): integration and no-reminder host checks.

[MIT](LICENSE).
