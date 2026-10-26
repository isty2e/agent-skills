# Convergence and exhaustiveness

Modified for security-audit. See [NOTICE](../NOTICE) for licensing and
upstream attribution.

The scan ends when the evidence says so, not when a pass count says so.
`scripts/scan-gate.py check` enforces the mechanical parts.

## State

`scan-state.json` (`schemas/scan-state.schema.json`), rewritten after every
pass:

- `history[]`: one entry per completed pass, numbered from 1, each with one
  `lens`, `new_findings`, `new_rejections`, `new_questions`, `consumed_gaps`,
  and a `note`. Two lenses means two passes.
  `new_questions` counts newly opened work (questions, deferred surfaces, or
  rejection rechecks), including work resolved during that same pass; an
  empty final gap list does not turn that count into zero.
- `gaps[]`: open work, each with `id`, `kind`
  (`question|deferred|surface|rejection-recheck`), `what`, `closes_when`, and
  `owner_pass`.
- `next_lens`: the lens the next pass will apply.
- `status` and `time_allowance_minutes`: `references/status-and-time.md`.

Stable IDs across passes: findings `sink-rule`, gaps `q-NNN` / `surface:<path>`
/ `recheck:<finding-id>`. Re-reporting an existing ID is not new.

## One pass

1. Consume every gap owned by this pass. Each ends as: finding, rejection
   (reason + evidence), or a new gap with a narrower `closes_when`. Gaps may
   split; they may not silently vanish.
2. Apply this pass's lens to the surfaces it covers (see Lenses).
3. Append the pass to `history` with its counts.
4. Regenerate the gap list from: open questions, deferred items, unreviewed
   files from coverage, and re-examination of rejections whose counterevidence
   was not a decisive control check.

## Lenses (rotate, never repeat consecutively)

- `forward`: attacker input → sinks.
- `backward`: sensitive sink → every caller, including siblings.
- `authorization`: each entry × anonymous/caller; compare sibling guards.
- `inverted-assumption`: "suppose control X is broken — what second barrier
  remains, and is it enforced?" Kills single-layer assumptions.
- `data-representation`: aliases, encodings, normalized vs raw forms, copies
  of security state, parser variants, validation-to-use transitions.
- `lifecycle`: retries, cancellation, crash recovery, partial writes,
  restart, migration, concurrent access.

## Quiescence (all must hold to stop)

1. No pass added findings after the last `inverted-assumption` and
   `data-representation` passes: both lenses ran, as separate passes, after the
   last pass with `new_findings > 0`, so every finding faced them.
2. `gaps` is empty: every question closed or recorded in
   `coverage.unresolvable` with the proof that closed it as untestable.
3. Every inventoried file has a final receipt in `coverage.reviewed_files`
   (`reviewed` or `excluded` with a reason). No `deferred` left.
4. Every candidate has its three receipts; a deferred candidate is named by a
   `coverage.unresolvable` record.
5. The final full pass has both `new_findings: 0` and `new_questions: 0`.
   A quiet earlier pass cannot close work discovered by a later pass.

An unavailable surface is never "covered": it is `excluded` with the reason, or
`unresolvable` with the exact missing evidence.

## Anti-quiescence rules (prevent fake convergence)

- A pass that only re-reads the same files with the same lens does not count.
- "No new findings" with an unresolved gap is not quiescence.
- A rejection reopened by new evidence is a new gap, not a new finding, until
  validated.
- Resource caps apply per pass (files, minutes); there is no pass cap. If a
  session must stop early, the state file makes the next session resume — the
  scan is incomplete, and that is recorded, not glossed.
