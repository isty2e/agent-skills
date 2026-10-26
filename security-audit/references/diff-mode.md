# Diff mode

Modified for security-audit. See [NOTICE](../NOTICE) for licensing and
upstream attribution.

Git diff modes refuse index entries marked `assume-unchanged` or
`skip-worktree`: they prevent Git from establishing source cleanliness or
reliably enumerating current changes. Committed-diff mode checks the entire
target, including supporting files; working-tree mode checks its requested
scope. Do not clear flags or refresh the read-only target's index. Use a clean
disposable checkout, or snapshot the actual source in repository mode without
either diff option, retaining the requested scope.

In working-tree mode, a path removed from the index but still present on disk
is current source: its bytes or symlink text enter the snapshot. Only actual
filesystem absence counts as a working-tree deletion. Committed-diff
deletions remain facts about the recorded revisions.

For a change under review (working tree, commit range, patch file). The changed
code is the primary surface; supporting code only as far as the change reaches.

## Inventory

- Commit range: `scan-gate.py inventory <target> <scan-dir> --diff <base>
  <head>` (changed files of `<base>...<head>`, commits resolved and recorded).
  The target must be a clean checkout of that head, including supporting code
  and non-ignored untracked files. Otherwise use a clean disposable checkout;
  do not inspect the current checkout as if it represented another revision.
- Working tree: `scan-gate.py inventory <target> <scan-dir> --working-tree`
  (staged and unstaged changes against `HEAD`, plus untracked files that are
  not ignored).
- Deleted files are in the inventory and in scope: classify from `HEAD` in
  working-tree mode, or the merge base of the recorded commits for a
  `<base>...<head>` diff. Renames appear as a deletion plus an addition.
- For a patch file, apply it to a disposable checkout outside the target and
  inventory that checkout with `--working-tree`.
- For each changed file, record: change kind (added/modified/deleted), the
  changed hunks, and the symbols those hunks belong to.
- Source and coverage snapshot binding follows `references/scope.md` in both
  modes. Working-tree identity also includes its current `HEAD` as the diff
  base; committing or changing that base requires revalidation.

## Reach

For each changed symbol, find direct callers (`rg` on the name), the entry
points that reach it, and the sinks it can now influence. A change to a shared
helper, guard, template, or sink wrapper is never reviewed alone: enumerate the
sibling call sites and check each one against the changed behavior.

Do not drift into unrelated repository scanning. Unchanged siblings are context
or negative controls unless the diff newly reaches them or weakens a control
they depend on. Record the supporting files you read in
`coverage.supporting_files` with why.

## Candidates

Prefer: authorization bypass, confused deputy, SSRF, traversal, injection with
a real sink, cross-tenant exposure, unsafe state change, sandbox escape,
newly-reachable dangerous sink. Keep independently reachable instances as
separate candidates keyed by `family:file:line`. Do not split one root cause
into cosmetic variants.

Include in each candidate: `entrypoint/wrapper`, `root_control`, `sink`, and
`concrete_implementation` locations when distinct; attacker source; broken
control and why it is absent/bypassed/mis-scoped; plausibility argument;
`relevant_lines` limited to lines overlapping the diff.

## Review rules

- Trust the code path over the commit message.
- A candidate is plausible, not validated — severity belongs to validation.
- Every changed file is accounted for in coverage (`reviewed`, or `excluded`
  with a reason). A deleted file's removal is checked for what it stopped
  enforcing.
- Finish only when every changed file and every candidate has a disposition.

## Quiescence

Same as `references/convergence.md`, scoped to the diff: no new candidates from
a full pass over the changed files, no open gaps, and every changed file
dispositioned. Because the surface is small, require both the
`inverted-assumption` and `data-representation` lenses before stopping.
