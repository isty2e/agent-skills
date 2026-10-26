# Scope and coverage

Modified for security-audit. See [NOTICE](../NOTICE) for licensing and
upstream attribution.

## Inventory (once, at start)

- File list: `scan-gate.py inventory <target> <scan-dir> [--scope PATH ...]
  [--exclude PREFIX ...]`. In a git work tree it lists tracked files (hidden
  ones included, regardless of ignore rules) plus untracked files that are not
  ignored; elsewhere it lists every file and symlink except `.git/`, ignoring
  `.ignore`/`.rgignore` files the target could use to hide content. Do not
  substitute `rg --files`: it skips hidden files.
- Git runs without filesystem-monitor hooks, executable content filters,
  external diff drivers or textconv. A checkout relying on those filters may
  no longer compare cleanly to a commit; do not re-enable them to pass the
  gate. If revision equivalence cannot be established without executing them,
  committed-diff review is unsupported for that checkout. Review the actual
  source as a scoped repository snapshot instead and state the limitation.
- `--exclude` removes whole prefixes from scope (for example `node_modules`)
  and is recorded; the report lists them. Use it for scope decisions, not to
  skip files that are in scope.
- `<scan-dir>` must be outside the target (the command refuses otherwise). A
  target inside `<scan-dir>` (for example `<scan-dir>/repo`) is recorded by
  relative path so the pair can move together.
- `scan-gate.py check` re-derives the inventory and its source snapshot.
  Changes to inventoried paths, file bytes, executable bits, or symlink text
  invalidate it. Files the scan itself wrote into the target (for example
  `__pycache__`) are a read-only violation: remove them and record it, do not
  inventory them.
- Entry enumeration: HTTP routes + methods, CLI commands + flags, jobs/queues,
  accepted file formats, env-var overrides.
- Sink enumeration: subprocess, network fetch, file writes, render sinks,
  deserializers, model calls, integrity primitives.

## Source identity and receipt reuse

`inventory.snapshot_digest` identifies the scoped file paths, node types,
regular-file bytes and executable bits, symlink target strings, and the
inventory's scope/mode/revision parameters. Links are not followed, including
when a requested path has a symlink parent; scope the link itself instead.
Special files such as sockets or FIFOs cannot be snapshotted and are refused.
Deleted diff entries are bound to the recorded revisions. Moving a scan and
its nested target together does not change this identity.

`coverage.snapshot_digest` attests to the snapshot its receipts describe.
After a change, rebuild inventory, revalidate affected review evidence, and
only then update that coverage attestation. Rebuilding inventory alone must
not make old coverage current. Unchanged evidence may be reused only when
its source and supporting assumptions are still applicable.

Keep source quiescent during inventory and verification, or use a frozen
disposable checkout. Snapshot verification is a point-in-time check, not a
lock or an atomic snapshot against concurrent edits. It covers the inventory,
not external deployment state or out-of-scope supporting files; recheck those
assumptions separately when reusing their evidence.

Older state files without snapshot identity are unsupported by the completion
gate. Do not invent a digest for historical receipts or rewrite retained old
scans to make them pass. Resume in a new scan directory with a fresh inventory
and revalidated evidence.

## Dispositions

Every inventoried file ends with exactly one receipt in `coverage.json`
(`references/receipts.md`):

- `reviewed`: read in full; the checklist items applied.
- `excluded`: one of the fixed reasons (generated, vendored, binary,
  test-only, documentation, static-asset) with how it was established.
  Exclusions are reviewable and do not imply safety.
- `deferred`: what remains and which pass owns it. Deferred items generate the
  next pass; a scan never ends with silent deferred work.

Supporting files outside a requested path may explain a finding, but the
affected entry, control, or operation must stay inside the scope.

## Convergence record

`scan-state.json` after every pass: the pass in `history`, gaps consumed and
produced, next lens. Quiescence (SKILL.md section 6) is checked against these
files, not memory. Open questions carry the exact evidence that would close
them.
