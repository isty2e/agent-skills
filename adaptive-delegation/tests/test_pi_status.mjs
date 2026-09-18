import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

import { recordRunFromPiStatus } from "../scripts/pi-status.mjs";

function status() {
  return {
    lifecycleArtifactVersion: 3,
    runId: "wrapper",
    state: "complete",
    totalTokens: { input: 9000, output: 8000 },
    totalCost: { costUsd: 500 },
    steps: [
      { runId: "other", status: "completed", tokens: { input: 10, output: 2 } },
      {
        runId: "child",
        status: "completed",
        durationMs: 92500,
        model: "provider/worker",
        thinking: "xhigh",
        context: "fresh",
        requestedModel: "different-request",
        tokens: { input: 1234, output: 56, total: 1290 },
        totalCost: { inputTokens: 1234, outputTokens: 56, costUsd: 0.12 },
        task: "private task",
        recentOutput: ["private output"],
        sessionFile: "/private/session",
      },
    ],
  };
}

test("projects child-scoped facts without wrapper totals or private text", () => {
  assert.deepEqual(recordRunFromPiStatus(status(), "child"), {
    run_id: "child",
    execution_status: "completed",
    metrics_source: "pi-subagents async status step",
    missing_metrics_reason: "not_reported",
    child_model: "provider/worker",
    child_effort: "xhigh",
    context: "fresh",
    elapsed_seconds: 92.5,
    input_tokens: 1234,
    output_tokens: 56,
    cost_amount: 0.12,
    cost_currency: "USD",
    cost_basis: "host_estimate",
  });
});

test("selection is exact, unique, and independent of position", () => {
  const value = status();
  const expected = recordRunFromPiStatus(value, "child");
  value.steps.reverse();
  assert.deepEqual(recordRunFromPiStatus(value, "child"), expected);
  for (const id of ["wrapper", "chil", "missing", ""]) {
    assert.throws(() => recordRunFromPiStatus(value, id));
  }
  value.steps.push({ ...value.steps[0] });
  assert.throws(() => recordRunFromPiStatus(value, "child"), /found 2/);
});

test("missing data remains omitted rather than copied from request or wrapper", () => {
  const value = status();
  value.steps = [{ runId: "child", requestedModel: "expensive:max" }];
  const record = recordRunFromPiStatus(value, "child");
  assert.equal(record.execution_status, "unknown");
  for (const key of [
    "child_model",
    "child_effort",
    "context",
    "cost_amount",
    "elapsed_seconds",
    "input_tokens",
    "cache_read_tokens",
  ]) {
    assert.equal(Object.hasOwn(record, key), false);
  }
});

test("execution completion is not replaced by failed acceptance", () => {
  const value = status();
  value.steps[1].status = "failed";
  value.steps[1].execution = { status: "completed", success: true };
  value.steps[1].acceptance = { status: "failed" };
  assert.equal(recordRunFromPiStatus(value, "child").execution_status, "completed");
  value.steps[1].execution.status = "failed";
  value.steps[1].status = "completed";
  assert.equal(recordRunFromPiStatus(value, "child").execution_status, "failed");
});

test("paused, partial and unfamiliar states do not imply completion or cancellation", () => {
  for (const native of ["paused", "partial", "detached", "pending", "future-state"]) {
    assert.equal(recordRunFromPiStatus({ steps: [{ runId: "a", status: native }] }, "a").execution_status, "unknown");
  }
  assert.equal(
    recordRunFromPiStatus({ steps: [{ runId: "a", status: "stopped" }] }, "a").execution_status,
    "cancelled",
  );
});

test("reported zero remains zero, optional null remains absent", () => {
  const value = {
    steps: [{ runId: "a", durationMs: 0, tokens: { input: 0, output: null }, totalCost: { costUsd: 0 } }],
  };
  const record = recordRunFromPiStatus(value, "a");
  assert.equal(record.input_tokens, 0);
  assert.equal(record.elapsed_seconds, 0);
  assert.equal(record.cost_amount, 0);
  assert.equal(Object.hasOwn(record, "output_tokens"), false);
});

test("invalid known numeric fields fail without manufacturing values", () => {
  for (const value of [-1, Infinity, NaN, "12", true]) {
    assert.throws(() => recordRunFromPiStatus({ steps: [{ runId: "a", durationMs: value }] }, "a"));
    assert.throws(() => recordRunFromPiStatus({ steps: [{ runId: "a", totalCost: { costUsd: value } }] }, "a"));
  }
  for (const value of [-1, 0.5, Number.MAX_SAFE_INTEGER + 1, "12"]) {
    assert.throws(() => recordRunFromPiStatus({ steps: [{ runId: "a", tokens: { input: value } }] }, "a"));
  }
});

test("rejects nested accounting and malformed supported fields", () => {
  for (const patch of [
    { children: [{}] },
    { tokens: [] },
    { totalCost: 5 },
    { execution: "completed" },
    { thinking: false },
    { model: 3 },
  ]) {
    assert.throws(() => recordRunFromPiStatus({ steps: [{ runId: "a", ...patch }] }, "a"));
  }
  assert.throws(() => recordRunFromPiStatus({}, "a"));
  assert.throws(() => recordRunFromPiStatus(null, "a"));
});

test("identical snapshots give identical receipts without accumulation", () => {
  const value = status();
  assert.deepEqual(recordRunFromPiStatus(value, "child"), recordRunFromPiStatus(value, "child"));
});

test("CLI emits only reusable JSON and fails with empty stdout for a missing child", async () => {
  const dir = await mkdtemp(join(tmpdir(), "pi-status-test-"));
  try {
    const path = join(dir, "status.json");
    await writeFile(path, JSON.stringify(status()));
    const script = fileURLToPath(new URL("../scripts/pi-status.mjs", import.meta.url));
    const run = (...args) => spawnSync(process.execPath, [script, ...args], { encoding: "utf8" });
    const ok = run(path, "--run-id", "child");
    assert.equal(ok.status, 0, ok.stderr);
    assert.deepEqual(JSON.parse(ok.stdout), recordRunFromPiStatus(status(), "child"));
    const bad = run(path, "--run-id", "wrapper");
    assert.equal(bad.status, 2);
    assert.equal(bad.stdout, "");
    assert.match(JSON.parse(bad.stderr).error, /found 0/);
    assert.equal(run("--help").status, 0);
  } finally {
    await rm(dir, { recursive: true, force: true });
  }
});
