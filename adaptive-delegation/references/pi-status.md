# Pi Status Input

For a known Pi async `status.json`, this optional Node.js helper selects one exact child `steps[].runId` and emits flat
`record-run` input:

```bash
node "$SKILL_DIR/scripts/pi-status.mjs" "$STATUS_JSON" --run-id "$CHILD_RUN_ID" |
  uv run "$SKILL_DIR/scripts/delegation.py" --project-root "$PROJECT_ROOT" \
    record-run "$RECORD_ID" --json -
```

Use the native child ID, not the wrapper/record ID, and the original record. `prepare` and parent `assess` are unchanged;
other hosts retain manual input. The helper reads only the supplied file: no Pi queries, artifact traversal, child
launches, or output assessment.

It copies per-step input/output tokens, duration converted from milliseconds to seconds, reported model/thinking/context,
and `totalCost.costUsd` as `host_estimate`, not a verified bill. Native `execution.status` overrides acceptance-derived
step status. Requested settings, wrapper totals, and report text are excluded. Missing fields stay omitted; this status
projection provides neither cache counts nor input inclusion semantics, so no cache ratio is derived.

Repeated snapshots update the same attempt without adding counters. Continuations with cumulative usage require manual
attribution, not a new attempt carrying old totals. Nested accounting and missing/ambiguous run IDs are rejected.

Supported contract: [observability](https://github.com/nicobailon/pi-subagents/blob/07bd09e0f93a19caee3c39e3cf4069c70ee8dbcd/docs/observability.md)
and [AsyncRunStepSummary](https://github.com/nicobailon/pi-subagents/blob/07bd09e0f93a19caee3c39e3cf4069c70ee8dbcd/src/runs/background/async-status.ts).
Unknown optional fields are ignored; malformed supported fields fail. Other native formats remain manual inputs.

From this skill directory, `node --test tests/test_pi_status.mjs` checks synthetic mapping/identity and CLI behavior,
not live Pi invocation or recording-time savings.
