#!/usr/bin/env node

import { realpathSync } from "node:fs";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

function object(value, label) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new TypeError(`${label} must be an object`);
  }
  return value;
}

function optionalNumber(value, label, integer = false) {
  if (value === undefined || value === null) return undefined;
  if (typeof value !== "number" || !Number.isFinite(value) || value < 0 || (integer && !Number.isSafeInteger(value))) {
    throw new TypeError(`${label} must be a nonnegative ${integer ? "safe integer" : "finite number"}`);
  }
  return value;
}

function optionalString(value, label) {
  if (value === undefined || value === null) return undefined;
  if (typeof value !== "string" || value.trim() === "") {
    throw new TypeError(`${label} must be a nonempty string`);
  }
  return value;
}

function executionStatus(step) {
  // Native execution is distinct from acceptance; a completed read-only run may fail a writer gate.
  const execution = step.execution == null ? null : object(step.execution, "step.execution");
  const status = optionalString(execution ? execution.status : step.status, "execution status");
  if (status === "completed" || status === "failed" || status === "running") return status;
  if (status === "stopped" || status === "cancelled") return "cancelled";
  return "unknown";
}

/** Project one exactly identified Pi async status step into the recorder's flat record-run input. */
export function recordRunFromPiStatus(status, runId) {
  object(status, "status");
  if (typeof runId !== "string" || runId.trim() === "") throw new TypeError("a child run ID is required");
  if (!Array.isArray(status.steps)) throw new TypeError("status.steps must be an array");
  const matches = status.steps.filter((step) => step?.runId === runId);
  if (matches.length !== 1) throw new Error(`expected one status step for child ${runId}; found ${matches.length}`);
  const step = object(matches[0], "step");
  if (step.children != null && (!Array.isArray(step.children) || step.children.length > 0)) {
    throw new Error("nested child accounting requires manual attribution");
  }
  const tokens = step.tokens == null ? {} : object(step.tokens, "step.tokens");
  const cost = step.totalCost == null ? {} : object(step.totalCost, "step.totalCost");
  const record = {
    run_id: runId,
    execution_status: executionStatus(step),
    metrics_source: "pi-subagents async status step",
    missing_metrics_reason: "not_reported",
  };
  const model = optionalString(step.model, "step.model");
  const effort = optionalString(step.thinking, "step.thinking");
  const context = optionalString(step.context, "step.context");
  if (model !== undefined) record.child_model = model;
  if (effort !== undefined) record.child_effort = effort;
  if (context === "fresh" || context === "fork") record.context = context;
  const duration = optionalNumber(step.durationMs, "step.durationMs");
  if (duration !== undefined) record.elapsed_seconds = duration / 1000;
  for (const [nativeKey, key] of [
    ["input", "input_tokens"],
    ["output", "output_tokens"],
  ]) {
    const value = optionalNumber(tokens[nativeKey], `step.tokens.${nativeKey}`, true);
    if (value !== undefined) record[key] = value;
  }
  const amount = optionalNumber(cost.costUsd, "step.totalCost.costUsd");
  if (amount !== undefined) {
    record.cost_amount = amount;
    record.cost_currency = "USD";
    record.cost_basis = "host_estimate";
  }
  return record;
}

export async function runCli(args = process.argv.slice(2)) {
  if (args.length === 1 && (args[0] === "--help" || args[0] === "-h")) {
    process.stdout.write(
      "Usage: pi-status.mjs <status.json> --run-id <exact-child-run-id>\nEmits flat record-run JSON; reads no other files and makes no network calls.\n",
    );
    return;
  }
  if (args.length !== 3 || args[1] !== "--run-id") {
    throw new Error("usage: pi-status.mjs <status.json> --run-id <exact-child-run-id>");
  }
  const status = JSON.parse(await readFile(args[0], "utf8"));
  const record = recordRunFromPiStatus(status, args[2]);
  process.stdout.write(`${JSON.stringify(record)}\n`);
}

if (process.argv[1] && realpathSync(fileURLToPath(import.meta.url)) === realpathSync(process.argv[1])) {
  runCli().catch((error) => {
    process.stderr.write(`${JSON.stringify({ error: error.message })}\n`);
    process.exitCode = 2;
  });
}
