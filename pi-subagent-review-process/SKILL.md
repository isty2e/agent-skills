---
name: pi-subagent-review-process
description: Run gated code-review-vector fanout with parent-captured review material, routed lane skills, active supervision, complete receipts, scope-separated findings, and one quiescence-checked report.
compatibility: Requires Pi with pi-subagents workflowScript, Node.js, subagent status, supervisor, and intercom tools; Git is required for commit-range reviews.
---

# Pi Subagent Review Process

## Procedure

1. Fix the target in `assets/review-ledger.md`: absolute `cwd`, review kind, worktree state, constraints, and Git
   `base`/`head`, `reviewFiles`, or both. Git IDs must be distinct full commits; ancestry is irrelevant. Files may be
   plans, specs, RFCs, saved full tool output, or other non-diff material.
2. Define lanes from `assets/review-wave.example.json`: one correctness decision per stable key, not one lane per
   checklist item. Include `code-review-vector` in `reviewSkills`, apply its routing, and list each lane's `routedSkills`.
   The parent covers remaining vectors; follow-ups target changed decisions or unresolved uncertainty.
3. Verify reviewers with `subagent({ action: "list", capabilities: true })`: executable, enabled, with required effective
   model/thinking. External CLI runners must be available.
4. Choose an unused absolute `materialDir` and generate the request:

   ```bash
   node scripts/review-wave.mjs review-packet.json > review-request.json
   ```

   `reviewFiles` are regular-file paths, absolute or relative to `cwd`; omit `target` for file-only reviews. Snapshots
   define the target. Reviewers may inspect needed repository context, not substitute live files or expand scope.
   For Git ranges, prohibit `git diff`, `git show`, and `git log`. Generator rejection blocks launch; execute its
   `workflowScript` unchanged, including `return runs.all(lanes)`.
5. Launch once, async with fresh context. Retain wrapper/mission/child IDs, async/status paths, and effective settings.
6. Stay available for users and children. Continue parent review, answer supervisor/intercom requests, share evidence,
   and steer drift, then yield for Pi wake notifications. Do not block on `subagent_wait()`, poll for delayed notices,
   or launch a duplicate wave. On wake collect the wrapper result from the notice or durable status; timeout is not completion.
7. Inspect status, including failed waves:

   ```bash
   node scripts/review-gate.mjs review-packet.json status.json
   ```

   Failure emits per-lane diagnostics and usable receipts with a nonzero exit. `machineGatePassed` covers the selected
   round; `reviewComplete` also requires the original lanes. `finalDispositionAuthorized` is always `false`.
8. Before one final report, reconfirm target, worktree, checks, candidate dispositions, and quiescence. Drain supervisor,
   intercom, completion, and control notices; later notices reopen closure. Only parent-verified in-scope findings affect
   disposition. Report verified out-of-scope/pre-existing findings separately, with verification and residual risks.

## Receipt Semantics

The generator owns the three-section report format:

- In-scope findings: evidence-backed findings within the overall change boundary, or `NO FINDING`; may affect approval.
  Lane focus organizes work, not scope.
- Out-of-scope findings: concrete pre-existing/other-boundary findings, or `NO FINDING`; report without approval effect.
- Residual risks: verification limits, not speculative findings.

`EVIDENCE_UNAVAILABLE` as a status line is terminal but incomplete; `EVIDENCE_UNAVAILABLE:none` is not missing evidence.
Child output remains candidate evidence; the parent owns validity, scope, root-cause ownership, severity, and disposition.

## Recovery

Use `laneResults` to distinguish identity/execution errors, unavailable evidence/output, and report-format errors. Repair
only affected reports/lanes; retain ready receipts only while their captured target and evidence remain applicable.
Relabeling does not repair missing evidence. Diagnose wrapper failures and resolve shared-state/target effects before
closure. Follow governing stop, approval, and retry rules; this skill authorizes no runtime switch or weakened review.

For the same packet, generate an affected-lane request without recapturing live files:

```bash
node scripts/review-wave.mjs review-packet.json --reuse-material --lane affected > recovery-request.json
```

After its native-harness launch completes, inspect with
`node scripts/review-gate.mjs review-packet.json recovery-status.json --lane affected`.
Repeat `--lane` for multiple gaps. Reuse verifies the original packet and captured hashes; changed targets or legacy
manifests without hashes need a fresh directory. Failed initial capture also needs a fresh directory, not overwrite.

Keep round/run IDs in the coverage ledger. Subset success is not original-review completion: cover every original
decision with a ready receipt or explicit parent review allowed by governing requirements. Replacing required independent
review needs authorization, not merely a parent checkbox. Retain active runs on timeout; new post-closure notices reopen
affected evidence and closure, not automatically the whole fanout. User decisions stay with the parent.

Local check: `node --test tests/*.test.mjs` (fixtures, not live Pi execution).

## Boundaries

Reviewers must not merge, publish, close issues, or make product decisions. Keep out-of-scope findings reportable but
disposition-neutral. Do not modify `pi-subagents` while using this skill.
