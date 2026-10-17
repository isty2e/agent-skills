import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";
import { inspectReviewRun, materializeWorkflowResults, validateReviewRun } from "../scripts/review-gate.mjs";

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

async function withReports(fn) {
  const dir = await mkdtemp(join(tmpdir(), "review-saved-report-"));
  try {
    const reportPath = join(dir, "report.md");
    const unrelatedPath = join(dir, "unrelated.md");
    await writeFile(reportPath, output);
    await writeFile(unrelatedPath, `${output}Unrelated artifact.\n`);
    const notice = `Output saved to: ${reportPath} (${Buffer.byteLength(output)} B, 6 lines). Read this file if needed.`;
    await fn({ dir, reportPath, unrelatedPath, notice });
  } finally {
    await rm(dir, { recursive: true, force: true });
  }
}

test("native file-only notifications load the saved report without changing provenance", async () => {
  await withReports(async ({ dir, reportPath, unrelatedPath, notice }) => {
    const value = status();
    value.workflow.value[0] = {
      runId: "run-b",
      agent: "reviewer",
      ok: true,
      output: notice,
      outputReference: reportPath,
      artifactPaths: [dir, unrelatedPath, reportPath],
      timestamp: 1000,
      completedAt: 1500,
    };
    const original = structuredClone(value);
    const results = await materializeWorkflowResults(value);
    assert.deepEqual(results[0], { ...original.workflow.value[0], workflowKey: "b", output });
    assert.deepEqual(value, original);

    const report = validateReviewRun({ packet: packet(), status: value, results, now: 100000 });
    assert.equal(report.machineGatePassed, true);
    assert.equal(report.reviewComplete, true);
    assert.equal(report.terminalAt, 1500);
    assert.equal(report.finalDispositionAuthorized, false);
    assert.equal(report.receipts.find(({ key }) => key === "b").output, output);
  });
});

test("explicit report references take precedence over complete inline previews", async () => {
  await withReports(async ({ reportPath }) => {
    const value = status();
    value.workflow.value[0].output = `${output}A different inline preview.\n`;
    value.workflow.value[0].outputReference = reportPath;
    const results = await materializeWorkflowResults(value);
    assert.equal(results[0].output, output);
    assert.equal(validateReviewRun({ packet: packet(), status: value, results, now: 100000 }).machineGatePassed, true);
  });
});

test("inline reports without an explicit reference do not require other artifacts", async () => {
  await withReports(async ({ dir }) => {
    for (const outputReference of [undefined, " \t"]) {
      const value = status();
      value.workflow.value[0].outputReference = outputReference;
      value.workflow.value[0].artifactPaths = [join(dir, "missing.md")];
      const results = await materializeWorkflowResults(value);
      assert.equal(results[0].output, output);
      assert.equal(validateReviewRun({ packet: packet(), status: value, results, now: 100000 }).machineGatePassed, true);
    }
  });
});

test("missing or unreadable explicit reports cannot fall back to inline or other artifacts", async () => {
  await withReports(async ({ dir, reportPath, unrelatedPath, notice }) => {
    for (const outputReference of [join(dir, "missing.md"), dir]) {
      for (const display of [notice.replace(reportPath, outputReference), output]) {
        const value = status();
        value.workflow.value[0] = {
          runId: "run-b",
          ok: true,
          output: display,
          outputReference,
          artifactPaths: [unrelatedPath],
        };
        const results = await materializeWorkflowResults(value);
        const input = { packet: packet(), status: value, results, now: 100000 };
        const report = inspectReviewRun(input);
        assert.equal(report.machineGatePassed, false);
        assert.equal(report.reviewComplete, false);
        assert.equal(report.finalDispositionAuthorized, false);
        assert.equal(report.laneResults.find(({ key }) => key === "b").failures[0].code, "output_unavailable");
        assert.deepEqual(report.receipts.map(({ key }) => key), ["a"]);
        assert.throws(() => validateReviewRun(input), (error) => error.report?.machineGatePassed === false);
      }
    }
  });
});

test("malformed or unavailable saved reports cannot be hidden by valid inline reports", async () => {
  await withReports(async ({ reportPath, unrelatedPath }) => {
    for (const [savedOutput, failureCode] of [
      ["# Findings\nNot the required report.\n", "report_format"],
      [`${output}\nEVIDENCE_UNAVAILABLE: captured input is unavailable\n`, "evidence_unavailable"],
    ]) {
      await writeFile(reportPath, savedOutput);
      const value = status();
      value.workflow.value[0].outputReference = reportPath;
      value.workflow.value[0].artifactPaths = [unrelatedPath];
      const results = await materializeWorkflowResults(value);
      assert.equal(results[0].output, savedOutput);
      const report = inspectReviewRun({ packet: packet(), status: value, results, now: 100000 });
      assert.equal(report.machineGatePassed, false);
      assert.equal(report.laneResults.find(({ key }) => key === "b").failures[0].code, failureCode);
      assert.deepEqual(report.receipts.map(({ key }) => key), ["a"]);
    }
  });
});

test("materialized reports still require matching identity and settled timestamps", async () => {
  await withReports(async ({ reportPath, notice }) => {
    const value = status();
    value.workflow.value[0].output = notice;
    value.workflow.value[0].outputReference = reportPath;
    value.workflow.value[0].completedAt = 99999;
    const results = await materializeWorkflowResults(value);
    const report = inspectReviewRun({ packet: packet(), status: value, results, now: 100000 });
    assert.equal(results[0].completedAt, 99999);
    assert.equal(report.terminalAt, 99999);
    assert.equal(report.machineGatePassed, false);
    assert.equal(report.laneResults.every(({ ready }) => ready), true);

    const mismatched = status();
    mismatched.workflow.value[0] = {
      workflowKey: "b",
      runId: "run-b",
      ok: true,
      output: notice,
      outputReference: reportPath,
    };
    mismatched.steps[1].runId = "another-run";
    const mismatchedResults = await materializeWorkflowResults(mismatched);
    const rejected = inspectReviewRun({ packet: packet(), status: mismatched, results: mismatchedResults, now: 100000 });
    assert.equal(mismatchedResults[0].output, output);
    assert.equal(rejected.machineGatePassed, false);
    assert.equal(rejected.laneResults.find(({ key }) => key === "b").failures[0].code, "identity");
    assert.deepEqual(rejected.receipts.map(({ key }) => key), ["a"]);
  });
});

test("native file-only reports pass through the CLI while malformed reports fail", async () => {
  await withReports(async ({ dir, reportPath, notice }) => {
    const value = status();
    value.workflow.value[0] = { runId: "run-b", ok: true, output: notice, outputReference: reportPath };
    const packetPath = join(dir, "packet.json");
    const statusPath = join(dir, "status.json");
    await writeFile(packetPath, JSON.stringify(packet()));
    await writeFile(statusPath, JSON.stringify(value));
    const gatePath = fileURLToPath(new URL("../scripts/review-gate.mjs", import.meta.url));

    const completed = spawnSync(process.execPath, [gatePath, packetPath, statusPath], { encoding: "utf8" });
    assert.equal(completed.status, 0, completed.stderr);
    const report = JSON.parse(completed.stdout);
    assert.equal(report.machineGatePassed, true);
    assert.equal(report.finalDispositionAuthorized, false);
    assert.equal(report.receipts.find(({ key }) => key === "b").output, output);

    await writeFile(reportPath, "# Findings\nNot the required report.\n");
    const failed = spawnSync(process.execPath, [gatePath, packetPath, statusPath], { encoding: "utf8" });
    assert.equal(failed.status, 1, failed.stderr);
    const rejected = JSON.parse(failed.stdout);
    assert.equal(rejected.machineGatePassed, false);
    assert.equal(rejected.laneResults.find(({ key }) => key === "b").failures[0].code, "report_format");
    assert.deepEqual(rejected.receipts.map(({ key }) => key), ["a"]);
  });
});

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
