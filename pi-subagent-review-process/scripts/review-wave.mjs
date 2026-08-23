#!/usr/bin/env node

import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { createReadStream, createWriteStream } from "node:fs";
import { mkdir, readFile, rename, rm, stat, writeFile } from "node:fs/promises";
import { isAbsolute, join, resolve } from "node:path";
import { pipeline } from "node:stream/promises";
import { pathToFileURL } from "node:url";

const KEY_PATTERN = /^[a-z0-9][a-z0-9._-]{0,63}$/;
const OBJECT_ID_PATTERN = /^(?:[0-9a-f]{40}|[0-9a-f]{64})$/;
const DEFAULT_TIMEOUT_MS = 7_200_000;
const MAX_GIT_STDERR_BYTES = 64 * 1024;

function requireString(value, label) {
  if (typeof value !== "string" || value.trim() === "") {
    throw new TypeError(`${label} must be a non-empty string`);
  }
  return value.trim();
}

function requireAbsolutePath(value, label) {
  const path = requireString(value, label);
  if (!isAbsolute(path)) throw new TypeError(`${label} must be an absolute path`);
  return resolve(path);
}

function requireStringArray(value, label) {
  if (!Array.isArray(value) || value.length === 0) {
    throw new TypeError(`${label} must be a non-empty string array`);
  }
  return value.map((entry, index) => requireString(entry, `${label}[${index}]`));
}

function normalizeTarget(target) {
  if (!target || typeof target !== "object" || Array.isArray(target)) {
    throw new TypeError("target must be an object");
  }
  const base = requireString(target.base, "target.base");
  const head = requireString(target.head, "target.head");
  if (!OBJECT_ID_PATTERN.test(base)) throw new TypeError("target.base must be a full Git object id");
  if (!OBJECT_ID_PATTERN.test(head)) throw new TypeError("target.head must be a full Git object id");
  if (base === head) throw new TypeError("target.base and target.head must differ");
  return {
    repository: requireString(target.repository, "target.repository"),
    base,
    head,
  };
}

function materialPaths(materialDir) {
  return {
    directory: materialDir,
    manifestPath: join(materialDir, "review-material.json"),
    changedFilesPath: join(materialDir, "changed-files.txt"),
    diffStatPath: join(materialDir, "diff-stat.txt"),
    diffPath: join(materialDir, "review.patch"),
  };
}

function buildLaneTask({ target, cwd, constraints, materials, requiredSkills, lane }) {
  return [
    "Read-only review lane.",
    `Repository: ${target.repository}`,
    `Working directory: ${cwd}`,
    `Exact base: ${target.base}`,
    `Exact head: ${target.head}`,
    "",
    "Parent-captured review material (read these first; do not ask the parent to provide a diff):",
    `- Material manifest: ${materials.manifestPath}`,
    `- Changed files: ${materials.changedFilesPath}`,
    `- Diff summary: ${materials.diffStatPath}`,
    `- Full patch: ${materials.diffPath}`,
    "- Use the read tool with offsets when an artifact is large.",
    "- Do not run git diff, git show, or git log. The parent has already captured the exact immutable comparison.",
    "- If a material file is unavailable or inconsistent, return EVIDENCE_UNAVAILABLE as the terminal report instead of asking for pasted diff content.",
    "",
    "Required routed skills:",
    ...requiredSkills.map((skill) => `- ${skill}`),
    "- Load and apply every routed skill before analysis; names in this prompt are not substitutes for their SKILL.md contents.",
    "",
    "Hard constraints:",
    ...constraints.map((constraint) => `- ${constraint}`),
    "- Keep the parent as the only final adjudicator.",
    "- Use supervisor/intercom only for a blocking decision or a meaningful progress checkpoint.",
    "",
    "Terminal report contract:",
    "## In-scope findings",
    "List concrete evidence-backed findings within the overall reviewed change boundary that can affect approval, or write NO FINDING. The lane focus organizes review work but does not redefine overall review scope; report a material cross-lane finding here and notify the parent.",
    "## Out-of-scope findings",
    "List concrete evidence-backed findings discovered during the lane that are outside the reviewed change boundary or pre-existing. These must be reported but must not affect approval. Write NO FINDING when empty.",
    "## Residual risks",
    "List verification limits only; do not promote speculation to findings.",
    "",
    `Decision lane: ${lane.task}`,
  ].join("\n");
}

export function normalizeReviewPacket(packet) {
  if (!packet || typeof packet !== "object" || Array.isArray(packet)) {
    throw new TypeError("review packet must be an object");
  }

  const cwd = requireAbsolutePath(packet.cwd, "cwd");
  const materialDir = requireAbsolutePath(packet.materialDir, "materialDir");
  const materials = materialPaths(materialDir);
  const model = requireString(packet.model, "model");
  const target = normalizeTarget(packet.target);
  const constraints = requireStringArray(packet.constraints, "constraints");
  const reviewSkills = [...new Set(requireStringArray(packet.reviewSkills, "reviewSkills"))];
  if (!reviewSkills.includes("code-review-vector")) {
    throw new TypeError("reviewSkills must include code-review-vector");
  }
  if (packet.context !== undefined && packet.context !== "fresh") {
    throw new TypeError("review packets require context='fresh'");
  }
  if (!Array.isArray(packet.lanes) || packet.lanes.length === 0) {
    throw new TypeError("review packet must contain at least one lane");
  }

  const seen = new Set();
  const lanes = packet.lanes.map((lane, index) => {
    if (!lane || typeof lane !== "object" || Array.isArray(lane)) {
      throw new TypeError(`lanes[${index}] must be an object`);
    }

    const key = requireString(lane.key, `lanes[${index}].key`);
    if (!KEY_PATTERN.test(key)) {
      throw new TypeError(`lanes[${index}].key is not a stable workflow key: ${key}`);
    }
    if (seen.has(key)) throw new TypeError(`duplicate lane key: ${key}`);
    seen.add(key);

    const routedSkills = [...new Set(requireStringArray(lane.routedSkills, `lanes[${index}].routedSkills`))];
    const requiredSkills = [...new Set([...reviewSkills, ...routedSkills])];
    const normalized = {
      key,
      agent: requireString(lane.agent, `lanes[${index}].agent`),
      skill: requiredSkills.join(", "),
      task: buildLaneTask({
        target,
        cwd,
        constraints,
        materials,
        requiredSkills,
        lane: { task: requireString(lane.task, `lanes[${index}].task`) },
      }),
    };
    if (lane.cwd !== undefined && requireAbsolutePath(lane.cwd, `lanes[${index}].cwd`) !== cwd) {
      throw new TypeError(`lanes[${index}].cwd must equal the packet cwd`);
    }
    if (lane.context !== undefined && lane.context !== "fresh") {
      throw new TypeError(`lanes[${index}].context must be 'fresh'`);
    }
    if (lane.output !== undefined) normalized.output = lane.output;
    if (lane.outputMode !== undefined) normalized.outputMode = lane.outputMode;
    if (lane.skill !== undefined) {
      throw new TypeError(`lanes[${index}].skill is derived from reviewSkills and routedSkills`);
    }
    return normalized;
  });

  return {
    cwd,
    materialDir,
    materials,
    model,
    target,
    constraints,
    reviewSkills,
    lanes,
    context: "fresh",
    chatProgress: packet.chatProgress ?? "off",
    timeoutMs: packet.timeoutMs ?? DEFAULT_TIMEOUT_MS,
    ...(packet.mission === undefined ? {} : { mission: packet.mission }),
    ...(packet.control === undefined ? {} : { control: packet.control }),
  };
}

function buildWorkflowFromNormalized(normalized) {
  return [
    `const lanes = ${JSON.stringify(normalized.lanes)};`,
    "return await runs.all(lanes);",
  ].join("\n");
}

function buildSubagentRequestFromNormalized(normalized) {
  return {
    workflowScript: buildWorkflowFromNormalized(normalized),
    async: true,
    context: normalized.context,
    chatProgress: normalized.chatProgress,
    cwd: normalized.cwd,
    model: normalized.model,
    timeoutMs: normalized.timeoutMs,
    ...(normalized.mission === undefined ? {} : { mission: normalized.mission }),
    ...(normalized.control === undefined ? {} : { control: normalized.control }),
  };
}

export function buildReviewWorkflow(packet) {
  return buildWorkflowFromNormalized(normalizeReviewPacket(packet));
}

export function buildSubagentRequest(packet) {
  return buildSubagentRequestFromNormalized(normalizeReviewPacket(packet));
}

async function runGitText({ cwd, args, maximumBytes = 4096 }) {
  let stdout = "";
  let stderr = "";
  await new Promise((resolvePromise, rejectPromise) => {
    const child = spawn("git", ["-C", cwd, "--no-pager", ...args], {
      stdio: ["ignore", "pipe", "pipe"],
      env: { ...process.env, GIT_PAGER: "cat" },
    });
    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");
    child.stdout.on("data", (chunk) => {
      stdout += chunk;
      if (stdout.length > maximumBytes) child.kill("SIGKILL");
    });
    child.stderr.on("data", (chunk) => {
      if (stderr.length < MAX_GIT_STDERR_BYTES) stderr += chunk.slice(0, MAX_GIT_STDERR_BYTES - stderr.length);
    });
    child.on("error", rejectPromise);
    child.on("close", (code, signal) => {
      if (stdout.length > maximumBytes) rejectPromise(new Error(`git ${args[0]} output exceeded ${maximumBytes} bytes`));
      else if (code === 0) resolvePromise();
      else rejectPromise(new Error(`git ${args[0]} failed (${signal ?? code}): ${stderr.trim()}`));
    });
  });
  return stdout.trim();
}

async function runGitCapture({ cwd, args, outputPath }) {
  const temporaryPath = `${outputPath}.tmp-${process.pid}-${Date.now()}`;
  await rm(temporaryPath, { force: true });
  const output = createWriteStream(temporaryPath, { flags: "wx", mode: 0o600 });
  let stderr = "";

  try {
    const child = spawn("git", ["-C", cwd, "--no-pager", ...args], {
      stdio: ["ignore", "pipe", "pipe"],
      env: { ...process.env, GIT_PAGER: "cat" },
    });
    child.stderr.setEncoding("utf8");
    child.stderr.on("data", (chunk) => {
      if (stderr.length < MAX_GIT_STDERR_BYTES) stderr += chunk.slice(0, MAX_GIT_STDERR_BYTES - stderr.length);
    });
    const exit = new Promise((resolvePromise, rejectPromise) => {
      child.on("error", rejectPromise);
      child.on("close", (code, signal) => {
        if (code === 0) resolvePromise();
        else rejectPromise(new Error(`git ${args[0]} failed (${signal ?? code}): ${stderr.trim()}`));
      });
    });
    await Promise.all([pipeline(child.stdout, output), exit]);
    await rename(temporaryPath, outputPath);
  } catch (error) {
    output.destroy();
    await rm(temporaryPath, { force: true });
    throw error;
  }
}

async function fileEvidence(path) {
  const hash = createHash("sha256");
  await new Promise((resolvePromise, rejectPromise) => {
    const input = createReadStream(path);
    input.on("data", (chunk) => hash.update(chunk));
    input.on("error", rejectPromise);
    input.on("end", resolvePromise);
  });
  const facts = await stat(path);
  return { path, bytes: facts.size, sha256: hash.digest("hex") };
}

export async function captureReviewMaterial(packet) {
  const normalized = normalizeReviewPacket(packet);
  await mkdir(normalized.materialDir, { recursive: true, mode: 0o700 });

  for (const [label, objectId] of [["base", normalized.target.base], ["head", normalized.target.head]]) {
    const resolvedCommit = await runGitText({ cwd: normalized.cwd, args: ["rev-parse", "--verify", `${objectId}^{commit}`] });
    if (resolvedCommit !== objectId) throw new Error(`target.${label} did not resolve to the exact supplied commit`);
  }

  const common = ["diff", "--no-ext-diff", "--no-textconv", "--find-renames", normalized.target.base, normalized.target.head, "--"];
  await runGitCapture({
    cwd: normalized.cwd,
    args: ["diff", "--no-ext-diff", "--no-textconv", "--find-renames", "--name-status", normalized.target.base, normalized.target.head, "--"],
    outputPath: normalized.materials.changedFilesPath,
  });
  await runGitCapture({
    cwd: normalized.cwd,
    args: ["diff", "--no-ext-diff", "--no-textconv", "--find-renames", "--stat", "--summary", normalized.target.base, normalized.target.head, "--"],
    outputPath: normalized.materials.diffStatPath,
  });
  await runGitCapture({
    cwd: normalized.cwd,
    args: [...common.slice(0, 4), "--find-copies", "--full-index", "--unified=80", ...common.slice(4)],
    outputPath: normalized.materials.diffPath,
  });

  const [changedFiles, diffStat, patch] = await Promise.all([
    fileEvidence(normalized.materials.changedFilesPath),
    fileEvidence(normalized.materials.diffStatPath),
    fileEvidence(normalized.materials.diffPath),
  ]);
  const manifest = {
    version: 1,
    capturedAt: new Date().toISOString(),
    repository: normalized.target.repository,
    cwd: normalized.cwd,
    base: normalized.target.base,
    head: normalized.target.head,
    files: { changedFiles, diffStat, patch },
  };
  await writeFile(normalized.materials.manifestPath, `${JSON.stringify(manifest, null, 2)}\n`, { mode: 0o600 });
  return { normalized, manifest };
}

export async function runCli(args = process.argv.slice(2)) {
  const packetPath = args[0];
  if (!packetPath) throw new Error("usage: review-wave.mjs <review-packet.json>");
  const packet = JSON.parse(await readFile(packetPath, "utf8"));
  const { normalized } = await captureReviewMaterial(packet);
  process.stdout.write(`${JSON.stringify(buildSubagentRequestFromNormalized(normalized), null, 2)}\n`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  runCli().catch((error) => {
    process.stderr.write(`${error.stack ?? error}\n`);
    process.exitCode = 1;
  });
}
