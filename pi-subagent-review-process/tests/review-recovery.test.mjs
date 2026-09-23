import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";
import { inspectReviewRun, validateReviewRun } from "../scripts/review-gate.mjs";
import { buildSubagentRequest, captureReviewMaterial, verifyReviewMaterial } from "../scripts/review-wave.mjs";

const output =
  "# In-scope findings\nNO FINDING\n# Out-of-scope findings\nNO FINDING\n# Residual risks\nSource checks only.\n";
function packet(cwd = "/review") {
  return {
    cwd,
    materialDir: join(cwd, "material"),
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
function input() {
  const results = ["a", "b"].map((key) => ({ workflowKey: key, runId: `run-${key}`, success: true, output }));
  return {
    packet: packet(),
    now: 100000,
    results,
    status: {
      state: "complete",
      runId: "wrapper",
      endedAt: 1000,
      steps: results.map(({ workflowKey, runId }) => ({ workflowKey, runId, status: "completed" })),
      workflow: { value: results },
    },
  };
}

test("strict success still requires every selected lane and never authorizes disposition", () => {
  const report = validateReviewRun(input());
  assert.equal(report.machineGatePassed, true);
  assert.equal(report.finalDispositionAuthorized, false);
  assert.equal(report.reviewComplete, true);
  assert.deepEqual(report.requiredLaneKeys, ["a", "b"]);
});

test("partial diagnostics retain ready siblings while strict validation fails", () => {
  const value = input();
  value.results[1].output = "EVIDENCE_UNAVAILABLE: cannot read material";
  const report = inspectReviewRun(value);
  assert.equal(report.machineGatePassed, false);
  assert.equal(report.reviewComplete, false);
  assert.deepEqual(
    report.receipts.map(({ key }) => key),
    ["a"],
  );
  assert.equal(report.laneResults[1].failures[0].code, "evidence_unavailable");
  assert.throws(
    () => validateReviewRun(value),
    (error) => error.report?.receipts.length === 1,
  );
});

test("format errors are distinct from missing evidence", () => {
  const value = input();
  value.results[1].output = "# Findings\nKnown candidate evidence.";
  assert.equal(inspectReviewRun(value).laneResults[1].failures[0].code, "report_format");
  value.results[1].output = `${output}\n- EVIDENCE_UNAVAILABLE: missing source`;
  assert.equal(inspectReviewRun(value).laneResults[1].failures[0].code, "evidence_unavailable");
  value.results[1].output = `${output}\nThe source mentions EVIDENCE_UNAVAILABLE as a literal.`;
  assert.equal(inspectReviewRun(value).machineGatePassed, true);
});

test("wrapper failure blocks full gate, not independent lane diagnostics", () => {
  const value = input();
  value.status.state = "failed";
  value.status.error = "wrapper failed after child receipts";
  const report = inspectReviewRun(value);
  assert.equal(report.machineGatePassed, false);
  assert.equal(report.receipts.length, 2);
  assert.ok(report.workflowFailures.length > 0);
});

test("duplicate identity cannot be admitted as reusable evidence", () => {
  const value = input();
  value.results[1].runId = value.results[0].runId;
  assert.equal(inspectReviewRun(value).receipts.length, 0);
  const another = input();
  another.results.push({ ...another.results[0] });
  assert.deepEqual(
    inspectReviewRun(another).receipts.map(({ key }) => key),
    ["b"],
  );
});

test("missing and unexpected lanes keep the gate incomplete", () => {
  const value = input();
  value.results.pop();
  assert.equal(inspectReviewRun(value).machineGatePassed, false);
  value.results.push({ workflowKey: "foreign", runId: "foreign", success: true, output });
  assert.equal(inspectReviewRun(value).machineGatePassed, false);
});

test("nonterminal and unsettled runs do not pass", () => {
  for (const time of [undefined, NaN, "1000", -1]) {
    const value = input();
    value.status.endedAt = time;
    assert.equal(inspectReviewRun(value).machineGatePassed, false);
  }
  const value = input();
  value.results[0].completedAt = value.now - 1;
  assert.equal(inspectReviewRun(value).machineGatePassed, false);
  value.results[0].completedAt = 1000;
  value.status.steps[0].status = "running";
  assert.equal(inspectReviewRun(value).machineGatePassed, false);
});

test("recovery subset passes only its own gate and retains original required coverage", () => {
  const value = input();
  value.laneKeys = ["b"];
  value.results = value.results.slice(1);
  value.status.steps = value.status.steps.slice(1);
  const report = validateReviewRun(value);
  assert.equal(report.machineGatePassed, true);
  assert.equal(report.reviewComplete, false);
  assert.equal(report.finalDispositionAuthorized, false);
  assert.deepEqual(report.requiredLaneKeys, ["a", "b"]);
  assert.deepEqual(report.selectedLaneKeys, ["b"]);
});

test("lane selection preserves model and original task while rejecting unknown/duplicate keys", () => {
  const original = buildSubagentRequest(packet());
  const subset = buildSubagentRequest(packet(), ["b"]);
  assert.equal(subset.model, original.model);
  assert.match(subset.workflowScript, /"key":"b"/);
  assert.doesNotMatch(subset.workflowScript, /"key":"a"/);
  assert.match(subset.workflowScript, /return runs\.all\(lanes\);$/);
  assert.throws(() => buildSubagentRequest(packet(), ["missing"]));
  assert.throws(() => buildSubagentRequest(packet(), ["a", "a"]));
});

test("every initial and recovery review lane forbids broad-root enumeration and scope expansion", () => {
  const gitPacket = {
    ...packet(),
    target: {
      repository: "example/repo",
      base: "a".repeat(40),
      head: "b".repeat(40),
    },
  };
  delete gitPacket.reviewFiles;

  for (const value of [packet(), gitPacket]) {
    for (const laneKeys of [[], ["b"]]) {
      const request = buildSubagentRequest(value, laneKeys);
      const lanes = JSON.parse(request.workflowScript.match(/^const lanes = (.*);\n/)[1]);
      for (const { task } of lanes) {
        assert.match(task, /Never run recursive searches or enumerations from \/, \$HOME, ~, any home directory/);
        assert.match(task, /broad parent directories, regardless of tool, depth, or output limit/);
        assert.match(task, /Do not expand the reviewed target into unrelated audits/);
        assert.match(task, /Inspect surrounding context as needed to find and validate in-scope findings/);
        assert.match(task, /report incidental pre-existing issues as out-of-scope findings/);
      }
    }
  }
});

async function withCapture(fn) {
  const cwd = await mkdtemp(join(tmpdir(), "review-recovery-test-"));
  try {
    await writeFile(join(cwd, "plan.md"), "Pinned review input.\n");
    const value = packet(cwd);
    const captured = await captureReviewMaterial(value);
    await fn(value, captured);
  } finally {
    await rm(cwd, { recursive: true, force: true });
  }
}

test("captured inputs can be reused without reading changed live source", async () => {
  await withCapture(async (value, captured) => {
    await writeFile(join(value.cwd, "plan.md"), "Changed live source, not the review target.\n");
    const normalized = await verifyReviewMaterial(value);
    assert.equal(normalized.materialDir, value.materialDir);
    assert.equal(captured.manifest.version, 2);
    assert.match(captured.manifest.files.reviewFiles[0].sha256, /^[0-9a-f]{64}$/);
    await assert.rejects(() => captureReviewMaterial(value), /EEXIST/);
  });
});

test("reuse refuses altered capture, packet, or legacy manifest", async () => {
  await withCapture(async (value, captured) => {
    await assert.rejects(() => verifyReviewMaterial({ ...value, model: "different" }), /original packet/);
    await assert.rejects(() => verifyReviewMaterial({ ...value, constraints: ["Changed"] }), /original packet/);
    const saved = captured.manifest.files.reviewFiles[0];
    await writeFile(saved.path, "Tampered target.\n");
    await assert.rejects(() => verifyReviewMaterial(value), /material changed/);
    await writeFile(captured.normalized.materials.manifestPath, JSON.stringify({ version: 1 }));
    await assert.rejects(() => verifyReviewMaterial(value), /original packet/);
  });
});

test("CLI recovery reuses the original capture and failed gate emits actionable JSON", async () => {
  await withCapture(async (value, captured) => {
    const packetPath = join(value.cwd, "packet.json");
    await writeFile(packetPath, JSON.stringify(value));
    const wave = fileURLToPath(new URL("../scripts/review-wave.mjs", import.meta.url));
    const before = await readFile(captured.normalized.materials.manifestPath, "utf8");
    const launch = spawnSync(process.execPath, [wave, packetPath, "--reuse-material", "--lane", "b"], {
      encoding: "utf8",
    });
    assert.equal(launch.status, 0, launch.stderr);
    assert.doesNotMatch(JSON.parse(launch.stdout).workflowScript, /"key":"a"/);
    assert.equal(await readFile(captured.normalized.materials.manifestPath, "utf8"), before);
    const source = input();
    source.status.endedAt = Date.now() - 60000;
    source.results[1].output = "EVIDENCE_UNAVAILABLE";
    const statusPath = join(value.cwd, "status.json");
    await writeFile(statusPath, JSON.stringify(source.status));
    const gate = fileURLToPath(new URL("../scripts/review-gate.mjs", import.meta.url));
    const result = spawnSync(process.execPath, [gate, packetPath, statusPath], { encoding: "utf8" });
    assert.equal(result.status, 1, result.stderr);
    const report = JSON.parse(result.stdout);
    assert.equal(report.machineGatePassed, false);
    assert.deepEqual(
      report.receipts.map(({ key }) => key),
      ["a"],
    );
  });
});

test("Git comparison capture retains exact target and detects a changed patch on reuse", async () => {
  const cwd = await mkdtemp(join(tmpdir(), "review-git-test-"));
  try {
    const git = (...args) => {
      const result = spawnSync("git", ["-C", cwd, ...args], {
        encoding: "utf8",
        env: { ...process.env, GIT_CONFIG_NOSYSTEM: "1" },
      });
      assert.equal(result.status, 0, result.stderr);
      return result.stdout.trim();
    };
    git("init", "-q");
    git("config", "user.name", "Fixture");
    git("config", "user.email", "fixture@example.invalid");
    await writeFile(join(cwd, "file.txt"), "before\n");
    git("add", "file.txt");
    git("commit", "-qm", "initial");
    const base = git("rev-parse", "HEAD");
    await writeFile(join(cwd, "file.txt"), "after\n");
    git("commit", "-qam", "changed");
    const head = git("rev-parse", "HEAD");
    const value = packet(cwd);
    delete value.reviewFiles;
    value.target = { repository: "fixture/repo", base, head };
    const captured = await captureReviewMaterial(value);
    await verifyReviewMaterial(value);
    const patch = captured.normalized.materials.diffPath;
    assert.match(await readFile(patch, "utf8"), /\+after/);
    await writeFile(patch, "altered\n");
    await assert.rejects(() => verifyReviewMaterial(value), /material changed/);
  } finally {
    await rm(cwd, { recursive: true, force: true });
  }
});
