---
name: pi-subagent-review-process
description: Run gated code-review-vector fanout with parent-captured diffs, routed lane skills, active supervision, complete receipts, scope-separated findings, and one quiescence-checked report.
compatibility: Requires Pi with pi-subagents workflowScript, Node.js, Git, and subagent status, supervisor, and intercom tools.
---

# Pi Subagent Review Process

## Procedure

1. Fix target. Copy `assets/review-ledger.md`; record the absolute repository `cwd`, distinct full base/head IDs, worktree state, user constraints, forbidden actions, and required current-head checks.
2. Define lanes from `assets/review-wave.example.json`. Give each stable key one distinct correctness decision. Include `code-review-vector` in `reviewSkills`, apply its routing, and record the selected names in each lane's `routedSkills`. The parent owns uncovered vectors.
3. Verify reviewers with `subagent({ action: "list" })`; use only executable, enabled agents. Confirm the effective runtime model and thinking.
4. Give the wave an unused absolute `materialDir`, then generate immutable review material and the launch request:

   ```bash
   node scripts/review-wave.mjs review-packet.json > review-request.json
   ```

   Treat generator rejection as blocking. Do not hand-edit its `workflowScript`. Reviewers read the captured material and must not run or request `git diff`, `git show`, or `git log`.
5. Launch the returned `workflowScript` once as an async fresh-context fanout. Record wrapper, mission, child, async, status, model, and thinking evidence.
6. Continue the parent review while supervising meaningful checkpoints. Answer blocking supervisor/intercom requests, share cross-lane evidence, and steer drift or repetition. Do not continuously poll or launch a duplicate wave because notification is delayed.
7. Collect the wrapper result. For run-to-completion use `subagent_wait({ id: "<wrapper-run-id>" })`; timeout is not completion.
8. Gate the durable status after wrapper success:

   ```bash
   node scripts/review-gate.mjs review-packet.json status.json
   ```

   The scripts own the packet, workflow, material, and receipt validation contract. Gate failure leaves the review incomplete, and `finalDispositionAuthorized` remains `false` even after success.
9. Close only after reconfirming target, worktree, checks, candidate dispositions, and quiescence. Drain supervisor, intercom, completion, and control notices; any later notice reopens closure.
10. Report once. Base disposition only on parent-verified in-scope findings. Report verified out-of-scope or pre-existing findings separately with no approval effect. Include verification and residual risks.

## Receipt semantics

The generator gives every reviewer the required three-section Markdown contract. Interpret it as follows:

- In-scope findings: evidence-backed findings inside the reviewed change boundary, or `NO FINDING`; may affect disposition. Lane focus organizes work, not scope.
- Out-of-scope findings: concrete pre-existing or other-boundary findings, or `NO FINDING`; never affect disposition.
- Residual risks: verification limits only, not speculative findings.

`EVIDENCE_UNAVAILABLE` is terminal but incomplete. Child output is candidate evidence; only the parent decides scope, validity, root-cause ownership, severity, and disposition.

## Recovery

- Timeout: keep the wave active; wait or inspect later.
- Wrapper or gate failure: diagnose and replace the orchestration; never salvage child files or assurances into approval.
- Missing or unusable lane: replace it or explicitly resolve the gap.
- Changed head: create a new target record.
- User decision: mark `needs-decision`; reviewers must not decide it.
- Notice after closure: retract the disposition and repeat closure.

Fleet emptiness, quiet time, green CI, or wrapper-independent child completion never replaces the gate and closure pass.

## Boundaries

- The parent alone adjudicates; reviewers must not merge, publish, close issues, or make product decisions.
- Keep concrete out-of-scope findings for reporting, but exclude them from disposition.
- Do not modify `pi-subagents` while using this skill.
