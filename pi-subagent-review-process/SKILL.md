---
name: pi-subagent-review-process
description: Run gated code-review-vector fanout with parent-captured diffs, routed lane skills, active supervision, complete receipts, scope-separated findings, and one quiescence-checked report.
compatibility: Requires Pi with pi-subagents workflowScript, Node.js, and subagent status, supervisor, and intercom tools.
---

# Pi Subagent Review Process

## Procedure

1. Fix target. Copy `assets/review-ledger.md`; record absolute repository `cwd`, distinct full base/head IDs, worktree state, user constraints, forbidden actions, and required current-head checks.
2. Define lanes. Start from `assets/review-wave.example.json`. Assign each stable key one distinct correctness decision. Include `code-review-vector` in `reviewSkills`; apply its routing and record returned names in each lane's `routedSkills`. Parent owns uncovered vectors.
3. Verify reviewer. Run `subagent({ action: "list" })`; use only executable, enabled agents. Confirm runtime model/thinking, not prompt wording.
4. Capture material. Assign an absolute `materialDir` unused by earlier or concurrent waves, then run:

   ```bash
   node scripts/review-wave.mjs review-packet.json > review-request.json
   ```

   The generator verifies both commits, captures `changed-files.txt`, `diff-stat.txt`, `review.patch`, and SHA-256 `review-material.json`, and injects paths plus routed skills. Reviewers page them with `read`; they do not run or request `git diff`, `git show`, or `git log`.
5. Launch once. Require one `return await runs.all(lanes)` and no `runs.run`; launch async. Record wrapper/mission/async IDs, expected keys, child IDs, and observed model/thinking.
6. Supervise. Continue parent review. At meaningful checkpoints inspect status/transcripts, answer blocking supervisor/intercom requests, share cross-lane evidence, and steer drift or repetition. Do not continuously poll or duplicate a wave for notification failure.
7. Collect. A lane completes only with a successful structured receipt. Replace or explicitly resolve missing, failed, empty, or `EVIDENCE_UNAVAILABLE` output. For run-to-completion use `subagent_wait({ id: "<wrapper-run-id>" })`; timeout is not completion.
8. Gate after wrapper success:

   ```bash
   node scripts/review-gate.mjs review-packet.json status.json
   ```

   The gate validates durable `status.json.workflow.value`: successful wrapper, elapsed settling interval, exact unique lane coverage, matching child IDs, successful non-empty structured outputs, and available evidence. It may load omitted inline output from durable artifacts; no transient result/replay is needed. `finalDispositionAuthorized` remains `false`.
9. Close. Reconfirm base/head, worktree, and checks; ensure no active work; drain supervisor, intercom, completion, and control notices; parent verifies, deduplicates, and scope-classifies every candidate. Any later notice resets closure.
10. Report once. Base approval only on verified in-scope findings. Report verified out-of-scope/pre-existing findings separately without approval effect. Include verification and residual risks, then deliver exactly one final report.

## Lane report

Return exactly:

```markdown
## In-scope findings

## Out-of-scope findings

## Residual risks
```

- In-scope: detailed evidence-backed findings inside the overall reviewed change boundary, or `NO FINDING`; may affect approval. Lane focus organizes work, not scope.
- Out-of-scope: concrete pre-existing or other-boundary findings, or `NO FINDING`; approval relevance `no`.
- Residual risks: verification limits only, never speculative findings.

Missing or inconsistent material: return terminal `EVIDENCE_UNAVAILABLE`; the lane stays incomplete. Child output is candidate evidence; only the parent decides scope, validity, root-cause ownership, severity, and disposition.

## Fail closed

- Wait timeout: keep active; wait or inspect later.
- Failed/stopped/detached/`unawaited runs.run` wrapper: block delivery; diagnose and replace orchestration.
- Missing/failed/empty/`EVIDENCE_UNAVAILABLE` lane: keep incomplete; replace or resolve.
- Missing/mismatched child ID: reject receipt.
- Changed head: start a new target record.
- User decision: mark `needs-decision`; reviewer must not decide.
- Notice after closure: retract disposition; repeat closure.

Fleet emptiness, quiet time, child files, green CI, or wrapper-independent child completion never replaces the complete gate.

## Packet

Required top level: absolute `cwd`; wave-unique absolute `materialDir`; explicit `model`; `target.repository`; distinct full 40/64-hex `target.base` and `target.head`; non-empty `reviewSkills` containing `code-review-vector`; shared `constraints`; non-empty `lanes`.

Each lane requires stable `key`, executable `agent`, non-empty `routedSkills`, and `task`; `output` and `outputMode` are optional. Do not set `skill`: the generator derives `reviewSkills + routedSkills`. Optional lane `cwd` must equal packet `cwd`; context is always `fresh`.

## Boundaries

- Parent alone adjudicates; reviewers must not merge, publish, close issues, or make product decisions.
- Never salvage failed wrappers with assurances or individually completed child files.
- Report concrete out-of-scope findings, but exclude them from approval.
- Do not modify `pi-subagents` while using this skill.
