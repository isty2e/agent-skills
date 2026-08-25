#!/usr/bin/env node

import { readFile } from "node:fs/promises";
import { pathToFileURL } from "node:url";

import { normalizeReviewPacket, RECEIPT_SECTIONS } from "./review-wave.mjs";

const DEFAULT_SETTLE_MS = 30_000;
const SUCCESS_STATES = new Set(["complete", "completed"]);

function resultKey(result) {
  return result?.workflowKey ?? result?.key;
}

function resultSucceeded(result) {
  return result?.success === true || result?.ok === true;
}

function parseReceiptSections(output) {
  return [...output.matchAll(/^# ([^\r\n]+?)[ \t]*\r?$/gm)].map((match) => match[1]);
}

function requireTerminalOutput(result, key) {
  if (typeof result?.output !== "string" || result.output.trim() === "") {
    throw new Error(`${key}: missing terminal output`);
  }
  const sections = parseReceiptSections(result.output);
  if (sections.length !== RECEIPT_SECTIONS.length
    || sections.some((section, index) => section !== RECEIPT_SECTIONS[index])) {
    throw new Error(`${key}: terminal report must contain exactly the required level-1 sections in order`);
  }
  if (/\bEVIDENCE_UNAVAILABLE\b/.test(result.output)) {
    throw new Error(`${key}: review evidence is unavailable`);
  }
}

function terminalTimestamp(status, result) {
  return Math.max(
    Number(status?.endedAt ?? 0),
    Number(status?.lastUpdate ?? 0),
    Number(result?.timestamp ?? 0),
    Number(result?.completedAt ?? 0),
  );
}

export async function materializeWorkflowResults(status) {
  const steps = Array.isArray(status?.steps) ? status.steps : [];
  const entries = status?.workflow?.value;
  if (!Array.isArray(entries)) {
    throw new TypeError("status.workflow.value must contain the directly awaited runs.all receipts");
  }
  const results = await Promise.all(entries.map(async (entry, index) => {
    let output = entry.output;
    const outputPath = Array.isArray(entry?.artifactPaths)
      ? entry.artifactPaths[0]
      : entry?.artifactPaths?.outputPath;
    if ((typeof output !== "string" || output.trim() === "") && typeof outputPath === "string" && outputPath !== "") {
      output = await readFile(outputPath, "utf8");
    }
    return {
      ...entry,
      workflowKey: resultKey(entry) ?? steps[index]?.workflowKey ?? steps[index]?.key ?? steps[index]?.label,
      output,
    };
  }));
  return results;
}

export function validateReviewRun({
  packet,
  status,
  results,
  now = Date.now(),
  settleMs = DEFAULT_SETTLE_MS,
}) {
  const normalized = normalizeReviewPacket(packet);
  const failures = [];

  if (!SUCCESS_STATES.has(status?.state)) {
    failures.push(`workflow status is ${status?.state ?? "missing"}, not completed`);
  }
  if (status?.error) {
    failures.push(`workflow recorded an error: ${status.error}`);
  }
  if (typeof status?.runId !== "string" || status.runId === "") {
    failures.push("status is missing runId");
  }

  const settledAt = terminalTimestamp(status);
  if (settledAt <= 0) {
    failures.push("terminal timestamp is missing");
  } else if (now - settledAt < settleMs) {
    failures.push(`terminal event settling window has not elapsed; retry after ${settleMs - (now - settledAt)} ms`);
  }

  const expectedKeys = normalized.lanes.map(({ key }) => key);
  const steps = Array.isArray(status?.steps) ? status.steps : [];
  const stepKeys = steps.map((step) => step.workflowKey ?? step.key ?? step.label);
  const resultKeys = results.map((entry) => resultKey(entry));
  const stepByKey = new Map(steps.map((step, index) => [stepKeys[index], step]));
  const resultByKey = new Map(results.map((entry, index) => [resultKeys[index], entry]));
  if (steps.length !== expectedKeys.length) failures.push(`status step count ${steps.length} does not match expected ${expectedKeys.length}`);
  if (results.length !== expectedKeys.length) failures.push(`result count ${results.length} does not match expected ${expectedKeys.length}`);
  if (stepByKey.size !== steps.length) failures.push("status contains duplicate or missing lane keys");
  if (resultByKey.size !== results.length) failures.push("result contains duplicate or missing lane keys");

  for (const key of expectedKeys) {
    const step = stepByKey.get(key);
    const entry = resultByKey.get(key);
    if (!step) {
      failures.push(`${key}: missing status step`);
      continue;
    }
    if (step.status !== "completed") failures.push(`${key}: step status is ${step.status ?? "missing"}`);
    if (typeof step.runId !== "string" || step.runId === "") failures.push(`${key}: missing child runId`);
    if (!entry) {
      failures.push(`${key}: missing terminal result`);
      continue;
    }
    if (!resultSucceeded(entry)) failures.push(`${key}: child result failed`);
    if (typeof entry.runId !== "string" || entry.runId === "") failures.push(`${key}: result missing child runId`);
    if (step.runId && entry.runId && step.runId !== entry.runId) failures.push(`${key}: status/result child runId mismatch`);
    try {
      requireTerminalOutput(entry, key);
    } catch (error) {
      failures.push(error.message);
    }
  }

  for (const step of steps) {
    const key = step.workflowKey ?? step.key ?? step.label;
    if (!key) failures.push("status step is missing a lane key");
    else if (!expectedKeys.includes(key)) failures.push(`${key}: unexpected status step`);
  }
  for (const entry of results) {
    const key = resultKey(entry);
    if (!key) failures.push("terminal result is missing a lane key");
    else if (!expectedKeys.includes(key)) failures.push(`${key}: unexpected terminal result`);
  }

  if (failures.length > 0) {
    throw new Error(`review run is not finalizable:\n- ${failures.join("\n- ")}`);
  }

  return {
    schemaVersion: 1,
    machineGatePassed: true,
    finalDispositionAuthorized: false,
    runId: status.runId,
    ...(normalized.target === undefined ? {} : { target: normalized.target }),
    ...(normalized.reviewFiles.length === 0
      ? {}
      : { reviewFiles: normalized.reviewFiles.map(({ sourcePath }) => sourcePath) }),
    terminalAt: settledAt,
    settleMs,
    receipts: expectedKeys.map((key) => {
      const step = stepByKey.get(key);
      const entry = resultByKey.get(key);
      return {
        key,
        agent: entry.agent ?? step.agent,
        runId: entry.runId,
        output: entry.output,
        artifactPaths: entry.artifactPaths ?? {},
      };
    }),
    remainingManualChecks: [
      normalized.target !== undefined && normalized.reviewFiles.length === 0
        ? "Reconfirm the exact base/head and worktree state."
        : "Reconfirm the exact reviewed material and worktree state.",
      "Confirm no active subagent fleet remains.",
      "Confirm subagent_supervisor and intercom pending queues are empty.",
      "Consume delayed completion/control notices; any new notice resets the closure pass.",
      "Adjudicate, deduplicate, and scope-classify every candidate finding in the parent.",
      "Base disposition only on in-scope findings and report verified out-of-scope findings separately.",
      "Record the closure evidence in the review ledger before the one final disposition.",
    ],
  };
}

function parseArgs(args) {
  const positional = [];
  let settleMs = DEFAULT_SETTLE_MS;
  for (let index = 0; index < args.length; index += 1) {
    if (args[index] === "--settle-ms") {
      settleMs = Number(args[index + 1]);
      index += 1;
      continue;
    }
    positional.push(args[index]);
  }
  if (positional.length !== 2 || !Number.isFinite(settleMs) || settleMs < 0) {
    throw new Error("usage: review-gate.mjs <packet.json> <status.json> [--settle-ms <ms>]");
  }
  return { packetPath: positional[0], statusPath: positional[1], settleMs };
}

export async function runCli(args = process.argv.slice(2)) {
  const { packetPath, statusPath, settleMs } = parseArgs(args);
  const [packet, status] = await Promise.all(
    [packetPath, statusPath].map(async (path) => JSON.parse(await readFile(path, "utf8"))),
  );
  const results = await materializeWorkflowResults(status);
  process.stdout.write(`${JSON.stringify(validateReviewRun({ packet, status, results, settleMs }), null, 2)}\n`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  runCli().catch((error) => {
    process.stderr.write(`${error.stack ?? error}\n`);
    process.exitCode = 1;
  });
}
