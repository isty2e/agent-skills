#!/usr/bin/env node

import { realpathSync } from "node:fs";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

import { normalizeReviewPacket, RECEIPT_SECTIONS, selectReviewLanes } from "./review-wave.mjs";

const DEFAULT_SETTLE_MS = 30_000;
const SUCCESS_STATES = new Set(["complete", "completed"]);

function resultKey(result) {
  return result?.workflowKey ?? result?.key;
}

function stepKey(step) {
  return resultKey(step) ?? step?.label;
}

function nonempty(value) {
  return typeof value === "string" && value.trim() !== "";
}

function receiptFailure(result) {
  if (result.outputReadError) return { code: "output_unavailable", message: result.outputReadError };
  if (!nonempty(result.output)) return { code: "output_unavailable", message: "missing terminal output" };
  // The sentinel is a status line, not a forbidden word in findings or quoted source.
  const unavailable = result.output.split(/\r?\n/).some((line) => {
    const marker = line.match(/^\s*(?:[-*]\s+)?EVIDENCE_UNAVAILABLE\b(.*)$/);
    return marker && !/^\s*:\s*none\.?\s*$/i.test(marker[1]);
  });
  if (unavailable) return { code: "evidence_unavailable", message: "review evidence is unavailable" };
  const sections = [...result.output.matchAll(/^# ([^\r\n]+?)[ \t]*\r?$/gm)].map((match) => match[1]);
  if (
    sections.length !== RECEIPT_SECTIONS.length ||
    sections.some((section, index) => section !== RECEIPT_SECTIONS[index])
  ) {
    return {
      code: "report_format",
      message: "terminal report must contain the three required level-1 sections in order",
    };
  }
  return null;
}

export async function materializeWorkflowResults(status) {
  const steps = Array.isArray(status?.steps) ? status.steps : [];
  const entries = status?.workflow?.value;
  if (!Array.isArray(entries)) return [];
  return Promise.all(
    entries.map(async (raw) => {
      const entry = raw && typeof raw === "object" ? raw : {};
      const matches = nonempty(entry.runId) ? steps.filter((step) => step?.runId === entry.runId) : [];
      const workflowKey = resultKey(entry) ?? (matches.length === 1 ? stepKey(matches[0]) : undefined);
      let output = entry.output;
      let outputReadError;
      const outputPath = nonempty(entry.outputReference)
        ? entry.outputReference
        : Array.isArray(entry.artifactPaths)
          ? entry.artifactPaths[0]
          : entry.artifactPaths?.outputPath;
      if (!nonempty(output) && nonempty(outputPath)) {
        try {
          output = await readFile(outputPath, "utf8");
        } catch (error) {
          outputReadError = `cannot read terminal artifact (${error.code ?? "I/O error"})`;
        }
      }
      return { ...entry, workflowKey, output, ...(outputReadError ? { outputReadError } : {}) };
    }),
  );
}

/** Inspect lanes independently; partial evidence never grants a complete review or final disposition. */
export function inspectReviewRun({
  packet,
  status,
  results,
  now = Date.now(),
  settleMs = DEFAULT_SETTLE_MS,
  laneKeys = [],
}) {
  const original = normalizeReviewPacket(packet);
  const normalized = selectReviewLanes(original, laneKeys);
  if (!Number.isFinite(now) || !Number.isFinite(settleMs) || settleMs < 0)
    throw new TypeError("invalid review clock or settling interval");
  const workflowFailures = [];
  if (!SUCCESS_STATES.has(status?.state))
    workflowFailures.push(`workflow status is ${status?.state ?? "missing"}, not completed`);
  if (status?.error) workflowFailures.push(`workflow recorded an error: ${status.error}`);
  if (!nonempty(status?.runId)) workflowFailures.push("status is missing runId");
  const steps = Array.isArray(status?.steps) ? status.steps : [];
  const entries = Array.isArray(results) ? results : [];
  const times = [
    status?.endedAt,
    status?.lastUpdate,
    ...entries.flatMap((entry) => [entry?.timestamp, entry?.completedAt]),
  ].filter((value) => value != null);
  const validTimes =
    times.some((value) => typeof value === "number" && value > 0) &&
    times.every((value) => typeof value === "number" && Number.isFinite(value) && value >= 0);
  const terminalAt = validTimes ? Math.max(...times) : null;
  if (terminalAt === null) workflowFailures.push("terminal timestamp is missing or invalid");
  else if (now - terminalAt < settleMs) workflowFailures.push("terminal event settling window has not elapsed");

  const expectedKeys = normalized.lanes.map(({ key }) => key);
  for (const [kind, items, keyOf] of [
    ["status step", steps, stepKey],
    ["terminal result", entries, resultKey],
  ]) {
    if (items.length !== expectedKeys.length)
      workflowFailures.push(`${kind} count ${items.length} does not match expected ${expectedKeys.length}`);
    for (const item of items) {
      const key = keyOf(item);
      if (!expectedKeys.includes(key))
        workflowFailures.push(`${kind} has unexpected or missing lane key: ${key ?? "missing"}`);
    }
  }
  const receipts = [];
  const laneResults = expectedKeys.map((key) => {
    const failures = [];
    const matchedSteps = steps.filter((step) => stepKey(step) === key);
    const matchedResults = entries.filter((entry) => resultKey(entry) === key);
    if (matchedSteps.length !== 1 || matchedResults.length !== 1) {
      failures.push({
        code: "identity",
        message: `expected one step and receipt; found ${matchedSteps.length}/${matchedResults.length}`,
      });
      return { key, ready: false, failures };
    }
    const step = matchedSteps[0];
    const entry = matchedResults[0];
    if (
      !nonempty(step.runId) ||
      step.runId !== entry.runId ||
      steps.filter((item) => item?.runId === step.runId).length !== 1 ||
      entries.filter((item) => item?.runId === entry.runId).length !== 1
    ) {
      failures.push({ code: "identity", message: "missing, duplicate, or mismatched child runId" });
    }
    if (step.status !== "completed" || !(entry.success === true || entry.ok === true)) {
      failures.push({ code: "execution", message: "child step/result has not completed successfully" });
    }
    const failure = receiptFailure(entry);
    if (failure) failures.push(failure);
    if (failures.length === 0)
      receipts.push({
        key,
        agent: entry.agent ?? step.agent,
        runId: entry.runId,
        output: entry.output,
        artifactPaths: entry.artifactPaths ?? {},
      });
    return { key, runId: entry.runId ?? null, ready: failures.length === 0, failures };
  });
  const machineGatePassed = workflowFailures.length === 0 && laneResults.every(({ ready }) => ready);
  return {
    schemaVersion: 1,
    machineGatePassed,
    finalDispositionAuthorized: false,
    runId: status?.runId ?? null,
    ...(normalized.target === undefined ? {} : { target: normalized.target }),
    ...(normalized.reviewFiles.length === 0
      ? {}
      : { reviewFiles: normalized.reviewFiles.map(({ sourcePath }) => sourcePath) }),
    terminalAt,
    settleMs,
    requiredLaneKeys: original.lanes.map(({ key }) => key),
    selectedLaneKeys: expectedKeys,
    reviewComplete: machineGatePassed && expectedKeys.length === original.lanes.length,
    workflowFailures,
    laneResults,
    receipts,
    remainingManualChecks: [
      normalized.target !== undefined && normalized.reviewFiles.length === 0
        ? "Reconfirm the exact base/head and worktree state."
        : "Reconfirm the exact reviewed material and worktree state.",
      "Confirm no active subagent fleet remains.",
      "Confirm subagent_supervisor and intercom pending queues are empty.",
      "Consume delayed completion/control notices; revalidate affected evidence and closure.",
      "Adjudicate, deduplicate, and scope-classify every candidate finding in the parent.",
      "Base disposition only on in-scope findings and report verified out-of-scope findings separately.",
      "Account for every original lane across validated rounds and record closure before final disposition.",
    ],
  };
}

export function validateReviewRun(input) {
  const report = inspectReviewRun(input);
  if (!report.machineGatePassed) {
    const messages = [
      ...report.workflowFailures,
      ...report.laneResults.flatMap(({ key, failures }) => failures.map(({ message }) => `${key}: ${message}`)),
    ];
    const error = new Error(`review run is not finalizable:\n- ${messages.join("\n- ")}`);
    error.report = report;
    throw error;
  }
  return report;
}

export async function runCli(args = process.argv.slice(2)) {
  const positional = [];
  const laneKeys = [];
  let settleMs = DEFAULT_SETTLE_MS;
  for (let index = 0; index < args.length; index += 1) {
    if (args[index] === "--settle-ms" && args[index + 1] !== undefined) settleMs = Number(args[++index]);
    else if (args[index] === "--lane" && args[index + 1] && !args[index + 1].startsWith("--"))
      laneKeys.push(args[++index]);
    else if (args[index].startsWith("--")) throw new Error(`invalid review-gate option: ${args[index]}`);
    else positional.push(args[index]);
  }
  if (positional.length !== 2 || !Number.isFinite(settleMs) || settleMs < 0) {
    throw new Error("usage: review-gate.mjs <packet.json> <status.json> [--settle-ms <ms>] [--lane <key>]...");
  }
  const [packet, status] = await Promise.all(positional.map(async (path) => JSON.parse(await readFile(path, "utf8"))));
  const results = await materializeWorkflowResults(status);
  const report = inspectReviewRun({ packet, status, results, settleMs, laneKeys });
  process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
  if (!report.machineGatePassed) process.exitCode = 1;
}

if (process.argv[1] && realpathSync(fileURLToPath(import.meta.url)) === realpathSync(process.argv[1])) {
  runCli().catch((error) => {
    process.stderr.write(`${error.stack ?? error}\n`);
    process.exitCode = 1;
  });
}
