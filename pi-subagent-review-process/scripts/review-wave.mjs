#!/usr/bin/env node

import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { createReadStream, createWriteStream, realpathSync } from "node:fs";
import { copyFile, mkdir, readFile, rename, rm, stat, writeFile } from "node:fs/promises";
import { basename, dirname, isAbsolute, join, resolve } from "node:path";
import { pipeline } from "node:stream/promises";
import { fileURLToPath } from "node:url";

const KEY_PATTERN = /^[a-z0-9][a-z0-9._-]{0,63}$/;
const OBJECT_ID_PATTERN = /^(?:[0-9a-f]{40}|[0-9a-f]{64})$/;
const DEFAULT_TIMEOUT_MS = 7_200_000;
const MAX_GIT_STDERR_BYTES = 64 * 1024;

export const RECEIPT_SECTIONS = Object.freeze(["In-scope findings", "Out-of-scope findings", "Residual risks"]);

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
  if (target === undefined) return undefined;
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
    reviewFilesDirectory: join(materialDir, "review-files"),
    changedFilesPath: join(materialDir, "changed-files.txt"),
    diffStatPath: join(materialDir, "diff-stat.txt"),
    diffPath: join(materialDir, "review.patch"),
  };
}

function normalizeReviewFiles(value, cwd, materials) {
  if (value === undefined) return [];
  return requireStringArray(value, "reviewFiles").map((path, index) => {
    const sourcePath = resolve(cwd, path);
    return {
      sourcePath,
      snapshotPath: join(materials.reviewFilesDirectory, String(index + 1).padStart(3, "0"), basename(sourcePath)),
    };
  });
}

function buildLaneTask({ target, reviewFiles, cwd, constraints, materials, requiredSkills, lane }) {
  const [inScopeSection, outOfScopeSection, residualRisksSection] = RECEIPT_SECTIONS;
  const gitOnly = target !== undefined && reviewFiles.length === 0;
  const lines = ["Read-only review lane."];
  if (target) {
    lines.push(`Repository: ${target.repository}`);
  }
  lines.push(`Working directory: ${cwd}`);
  if (target) {
    lines.push(`Exact base: ${target.base}`, `Exact head: ${target.head}`);
  }
  lines.push(
    "",
    gitOnly
      ? "Read parent-captured material first; do not request a pasted diff:"
      : "Read parent-captured material first:",
    `- Material manifest: ${materials.manifestPath}`,
  );
  if (target) {
    lines.push(
      `- Changed files: ${materials.changedFilesPath}`,
      `- Diff summary: ${materials.diffStatPath}`,
      `- Full patch: ${materials.diffPath}`,
    );
  }
  for (const reviewFile of reviewFiles) {
    lines.push(`- Review file snapshot: ${reviewFile.snapshotPath} (source: ${reviewFile.sourcePath})`);
  }
  lines.push("- Use the read tool with offsets when an artifact is large.");
  if (target) {
    lines.push(
      "- The captured Git comparison is authoritative; do not run git diff, git show, or git log.",
    );
  }
  if (reviewFiles.length > 0) {
    lines.push(
      "- Continue truncated reads with offsets; truncation does not establish absence.",
      "- File snapshots define the target, not later live edits. Inspect needed repository context without substituting live files or expanding scope.",
    );
  }
  lines.push(
    gitOnly
      ? "- Unavailable/inconsistent material: return EVIDENCE_UNAVAILABLE, not a request for pasted diff."
      : "- Unavailable/inconsistent material: return EVIDENCE_UNAVAILABLE, not a request for pasted content.",
    "",
    "Required routed skills:",
    ...requiredSkills.map((skill) => `- ${skill}`),
    "- Before analysis, load and apply each routed SKILL.md; names alone do not suffice.",
    "",
    "Hard constraints:",
    ...constraints.map((constraint) => `- ${constraint}`),
    "- Never run recursive searches or enumerations from /, $HOME, ~, any home directory, or their broad parent directories, regardless of tool, depth, or output limit.",
    "- Do not expand the reviewed target into unrelated audits. Inspect surrounding context as needed to find and validate in-scope findings; report incidental pre-existing issues as out-of-scope findings without chasing them.",
    "- Keep the parent as the only final adjudicator.",
    "- Use supervisor/intercom only for a blocking decision or a meaningful progress checkpoint.",
    "",
    "Terminal report contract:",
    "Use exactly these three level-1 ATX headings in order, each on its own line; no document title or other level-1 headings.",
    `# ${inScopeSection}`,
    "Concrete evidence-backed findings within the overall change boundary, or NO FINDING; may affect approval. Lane focus does not narrow scope: include material cross-lane findings here and notify the parent.",
    `# ${outOfScopeSection}`,
    "Concrete evidence-backed pre-existing/other-boundary findings, or NO FINDING. Report them without approval effect.",
    `# ${residualRisksSection}`,
    "Verification limits only, not speculative findings.",
    "",
    `Decision lane: ${lane.task}`,
  );
  return lines.join("\n");
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
  const reviewFiles = normalizeReviewFiles(packet.reviewFiles, cwd, materials);
  if (!target && reviewFiles.length === 0) {
    throw new TypeError("review packet requires target, reviewFiles, or both");
  }
  const timeoutMs = packet.timeoutMs ?? DEFAULT_TIMEOUT_MS;
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
        reviewFiles,
        cwd,
        constraints,
        materials,
        requiredSkills,
        lane: { task: requireString(lane.task, `lanes[${index}].task`) },
      }),
      timeoutMs,
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
    ...(target === undefined ? {} : { target }),
    reviewFiles,
    constraints,
    reviewSkills,
    lanes,
    context: "fresh",
    timeoutMs,
    ...(packet.mission === undefined ? {} : { mission: packet.mission }),
    ...(packet.control === undefined ? {} : { control: packet.control }),
  };
}

export function selectReviewLanes(normalized, keys = []) {
  if (keys.length === 0) return normalized;
  if (new Set(keys).size !== keys.length) throw new Error("duplicate selected lane key");
  const known = new Set(normalized.lanes.map(({ key }) => key));
  for (const key of keys) {
    if (!known.has(key)) throw new Error(`unknown selected lane: ${key}`);
  }
  return { ...normalized, lanes: normalized.lanes.filter(({ key }) => keys.includes(key)) };
}

function packetDigest(normalized) {
  return createHash("sha256").update(JSON.stringify(normalized)).digest("hex");
}

function buildWorkflowFromNormalized(normalized) {
  return [`const lanes = ${JSON.stringify(normalized.lanes)};`, "return runs.all(lanes);"].join("\n");
}

function buildSubagentRequestFromNormalized(normalized) {
  return {
    workflowScript: buildWorkflowFromNormalized(normalized),
    async: true,
    context: normalized.context,
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

export function buildSubagentRequest(packet, laneKeys = []) {
  return buildSubagentRequestFromNormalized(selectReviewLanes(normalizeReviewPacket(packet), laneKeys));
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
      if (stdout.length > maximumBytes)
        rejectPromise(new Error(`git ${args[0]} output exceeded ${maximumBytes} bytes`));
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
  await mkdir(dirname(normalized.materialDir), { recursive: true, mode: 0o700 });
  await mkdir(normalized.materialDir, { mode: 0o700 });

  let gitFiles;
  if (normalized.target) {
    for (const [label, objectId] of [
      ["base", normalized.target.base],
      ["head", normalized.target.head],
    ]) {
      const resolvedCommit = await runGitText({
        cwd: normalized.cwd,
        args: ["rev-parse", "--verify", `${objectId}^{commit}`],
      });
      if (resolvedCommit !== objectId) throw new Error(`target.${label} did not resolve to the exact supplied commit`);
    }

    const common = [
      "diff",
      "--no-ext-diff",
      "--no-textconv",
      "--find-renames",
      normalized.target.base,
      normalized.target.head,
      "--",
    ];
    await runGitCapture({
      cwd: normalized.cwd,
      args: [
        "diff",
        "--no-ext-diff",
        "--no-textconv",
        "--find-renames",
        "--name-status",
        normalized.target.base,
        normalized.target.head,
        "--",
      ],
      outputPath: normalized.materials.changedFilesPath,
    });
    await runGitCapture({
      cwd: normalized.cwd,
      args: [
        "diff",
        "--no-ext-diff",
        "--no-textconv",
        "--find-renames",
        "--stat",
        "--summary",
        normalized.target.base,
        normalized.target.head,
        "--",
      ],
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
    gitFiles = { changedFiles, diffStat, patch };
  }

  let capturedReviewFiles = [];
  if (normalized.reviewFiles.length > 0) {
    await mkdir(normalized.materials.reviewFilesDirectory, { recursive: true, mode: 0o700 });
    capturedReviewFiles = await Promise.all(
      normalized.reviewFiles.map(async ({ sourcePath, snapshotPath }) => {
        const source = await stat(sourcePath);
        if (!source.isFile()) throw new TypeError(`reviewFiles source must be a regular file: ${sourcePath}`);
        await mkdir(dirname(snapshotPath), { recursive: true, mode: 0o700 });
        await copyFile(sourcePath, snapshotPath);
        return { sourcePath, ...(await fileEvidence(snapshotPath)) };
      }),
    );
  }

  const manifest = {
    version: 2,
    packetDigest: packetDigest(normalized),
    capturedAt: new Date().toISOString(),
    cwd: normalized.cwd,
    ...(normalized.target === undefined
      ? {}
      : {
          repository: normalized.target.repository,
          base: normalized.target.base,
          head: normalized.target.head,
        }),
    files: {
      ...(gitFiles === undefined ? {} : gitFiles),
      ...(capturedReviewFiles.length === 0 ? {} : { reviewFiles: capturedReviewFiles }),
    },
  };
  await writeFile(normalized.materials.manifestPath, `${JSON.stringify(manifest, null, 2)}\n`, { mode: 0o600 });
  return { normalized, manifest };
}

/** Verify the original packet and captured bytes before selecting a recovery subset. */
export async function verifyReviewMaterial(packet) {
  const normalized = normalizeReviewPacket(packet);
  const manifest = JSON.parse(await readFile(normalized.materials.manifestPath, "utf8"));
  if (manifest.version !== 2 || manifest.packetDigest !== packetDigest(normalized)) {
    throw new Error("review material does not match the original packet; capture a new target in a new directory");
  }
  const expected = [];
  if (normalized.target) {
    expected.push(
      [normalized.materials.changedFilesPath, manifest.files?.changedFiles],
      [normalized.materials.diffStatPath, manifest.files?.diffStat],
      [normalized.materials.diffPath, manifest.files?.patch],
    );
  }
  for (const [index, file] of normalized.reviewFiles.entries()) {
    const saved = manifest.files?.reviewFiles?.[index];
    if (saved?.sourcePath !== file.sourcePath) throw new Error("review source identity changed");
    expected.push([file.snapshotPath, saved]);
  }
  for (const [path, saved] of expected) {
    const current = await fileEvidence(path);
    if (saved?.path !== path || saved.bytes !== current.bytes || saved.sha256 !== current.sha256) {
      throw new Error(`captured review material changed: ${path}`);
    }
  }
  return normalized;
}

export async function runCli(args = process.argv.slice(2)) {
  const [packetPath, ...options] = args;
  if (!packetPath || packetPath.startsWith("--"))
    throw new Error("usage: review-wave.mjs <packet.json> [--reuse-material] [--lane <key>]...");
  const laneKeys = [];
  let reuseMaterial = false;
  for (let index = 0; index < options.length; index += 1) {
    if (options[index] === "--reuse-material" && !reuseMaterial) reuseMaterial = true;
    else if (options[index] === "--lane" && options[index + 1] && !options[index + 1].startsWith("--"))
      laneKeys.push(options[++index]);
    else throw new Error(`invalid review-wave option: ${options[index]}`);
  }
  const packet = JSON.parse(await readFile(packetPath, "utf8"));
  // Validate selection before capturing anything; retain the unfiltered packet as material identity.
  selectReviewLanes(normalizeReviewPacket(packet), laneKeys);
  const normalized = reuseMaterial
    ? await verifyReviewMaterial(packet)
    : (await captureReviewMaterial(packet)).normalized;
  const selected = selectReviewLanes(normalized, laneKeys);
  process.stdout.write(`${JSON.stringify(buildSubagentRequestFromNormalized(selected), null, 2)}\n`);
}

if (process.argv[1] && realpathSync(fileURLToPath(import.meta.url)) === realpathSync(process.argv[1])) {
  runCli().catch((error) => {
    process.stderr.write(`${error.stack ?? error}\n`);
    process.exitCode = 1;
  });
}
