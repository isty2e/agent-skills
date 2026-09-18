# Pi Status Input

Use the optional Node.js helper when a Pi async `status.json` is already available. It selects one exact child
`steps[].runId` and emits the existing recorder's flat `record-run` input, avoiding manual transcription:

```bash
node "$SKILL_DIR/scripts/pi-status.mjs" "$STATUS_JSON" --run-id "$CHILD_RUN_ID" |
  uv run "$SKILL_DIR/scripts/delegation.py" --project-root "$PROJECT_ROOT" \
    record-run "$RECORD_ID" --json -
```

`CHILD_RUN_ID` is the native child ID, not the wrapper or record ID. Use known paths and the original record. Keep
`prepare` and the parent's final `assess` unchanged. Other harnesses keep their existing manual input path.

The helper copies per-step input/output counts, milliseconds converted to seconds, `totalCost.costUsd` as
`host_estimate`, and reported model/thinking/context. Native `execution.status` takes precedence over an acceptance-derived
step status. Requested settings, wrapper totals and report text are not imported. Missing fields stay omitted; cache
counts and input inclusion semantics are not exposed by this supported status projection, so no cache ratio is derived.

Repeated snapshots update the same attempt without adding counters. For a continuation whose usage includes earlier
work, use the recorder's existing manual attribution path instead of creating a new attempt with cumulative totals.
Nested child accounting and ambiguous/missing run IDs are rejected. The helper reads only the supplied file; it does
not query Pi, follow artifact paths, launch children, or assess output. It copies host estimates, not verified bills.

The supported input is the async status/summary `steps` projection documented in
[pi-subagents observability](https://github.com/nicobailon/pi-subagents/blob/07bd09e0f93a19caee3c39e3cf4069c70ee8dbcd/docs/observability.md)
and [AsyncRunStepSummary](https://github.com/nicobailon/pi-subagents/blob/07bd09e0f93a19caee3c39e3cf4069c70ee8dbcd/src/runs/background/async-status.ts).
Unknown optional fields are ignored; malformed supported fields fail. Other native formats remain manual inputs.

Run the helper's synthetic fixture and CLI checks from this skill directory:

```bash
node --test tests/test_pi_status.mjs
```

These tests verify field mapping and identity, not live Pi invocation or reduced recording time.
