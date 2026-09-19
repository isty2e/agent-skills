import assert from "node:assert/strict";
import { mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";
import { materializeWorkflowResults, validateReviewRun } from "../scripts/review-gate.mjs";

const output =
  "# In-scope findings\nNO FINDING\n# Out-of-scope findings\nNO FINDING\n# Residual risks\nSource checks only.\n";
function packet() {
  return {
    cwd: "/review",
    materialDir: "/review-material",
    reviewFiles: ["plan.md"],
    model: "review-model:xhigh",
    constraints: ["Read-only"],
    reviewSkills: ["code-review-vector"],
    lanes: [
      { key: "a", agent: "reviewer", task: "Check A", routedSkills: ["code-review-vector"] },
      { key: "b", agent: "reviewer", task: "Check B", routedSkills: ["code-review-vector"] },
    ],
  };
}
function status() {
  return {
    state: "complete",
    runId: "wrapper",
    endedAt: 1000,
    steps: [
      { workflowKey: "a", runId: "run-a", status: "completed" },
      { workflowKey: "b", runId: "run-b", status: "completed" },
    ],
    workflow: {
      value: [
        { runId: "run-b", success: true, output },
        { runId: "run-a", success: true, output },
      ],
    },
  };
}

test("keyless receipts follow child identity, not array position", async () => {
  const value = status();
  const results = await materializeWorkflowResults(value);
  assert.deepEqual(
    results.map(({ workflowKey }) => workflowKey),
    ["b", "a"],
  );
  assert.equal(validateReviewRun({ packet: packet(), status: value, results, now: 100000 }).machineGatePassed, true);
});

test("file-only receipts use their explicit output reference, not artifact ordering", async () => {
  const dir = await mkdtemp(join(tmpdir(), "review-output-reference-"));
  try {
    const reportPath = join(dir, "report.md");
    const unrelatedPath = join(dir, "unrelated.md");
    await writeFile(reportPath, output);
    await writeFile(unrelatedPath, `${output}Unrelated artifact.\n`);

    for (const firstArtifact of [dir, unrelatedPath]) {
      const value = status();
      value.workflow.value[0] = {
        runId: "run-b",
        success: true,
        outputReference: reportPath,
        artifactPaths: [firstArtifact, reportPath],
      };
      const results = await materializeWorkflowResults(value);
      assert.equal(results[0].output, output);
      assert.equal(validateReviewRun({ packet: packet(), status: value, results, now: 100000 }).machineGatePassed, true);
    }

    const missing = status();
    missing.workflow.value[0] = {
      runId: "run-b",
      success: true,
      outputReference: join(dir, "missing.md"),
      artifactPaths: [unrelatedPath],
    };
    const results = await materializeWorkflowResults(missing);
    assert.match(results[0].outputReadError, /cannot read/);
    assert.equal(results[1].output, output);
  } finally {
    await rm(dir, { recursive: true, force: true });
  }
});

test("explicit no-unavailable-evidence annotation does not invalidate a complete report", () => {
  const value = status();
  const results = value.workflow.value.map((entry) => ({
    ...entry,
    workflowKey: entry.runId === "run-a" ? "a" : "b",
    output: `${output}EVIDENCE_UNAVAILABLE:none\n`,
  }));
  assert.equal(validateReviewRun({ packet: packet(), status: value, results, now: 100000 }).machineGatePassed, true);
});

test("one unavailable output artifact does not discard another lane's returned evidence", async () => {
  const value = status();
  value.workflow.value[0] = {
    runId: "run-b",
    success: true,
    artifactPaths: { outputPath: "/nonexistent-review-fixture/output.md" },
  };
  const results = await materializeWorkflowResults(value);
  assert.equal(results.find(({ runId }) => runId === "run-a").output, output);
  assert.match(results.find(({ runId }) => runId === "run-b").outputReadError, /cannot read/);
});
