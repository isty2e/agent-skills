---
name: jujutsu
description: >-
  Use Jujutsu (jj) for version-control work in jj-managed repositories, including colocated Git repositories.
  Apply for status, explicit new-file tracking, commits, stacked changes, review fixes, bookmarks, push/fetch,
  conflicts, recovery, and running existing pre-commit hooks from jj.
license: MIT
---

# Jujutsu

Use jj for VCS work in jj-managed workspaces; do not fall back to familiar Git mutations. Git-backed tools and the
pre-commit adapter may use Git internally. Do not initialize jj in an ordinary Git repository merely because this skill
is available.

## Locate And Track

Start without snapshotting:

```sh
jj --ignore-working-copy workspace root
jj --ignore-working-copy config get snapshot.auto-track
```

Resolve the actual workspace from subdirectories too. Do not operate on the enclosing jj workspace when the task
targets a nested ordinary Git repo.

Before snapshotting, establish explicit new-file tracking at repo scope, unless authoritative project instructions
specify otherwise:

```sh
jj --ignore-working-copy config set --repo snapshot.auto-track 'none()'
jj status
jj file track path/to/new-file
```

Do not change global config. Inspect untracked paths and select intended files individually; do not use argument-free
or whole-repo `jj file track`. After a filesystem rename/move, track the destination or only the deletion is recorded. Ignored
paths are silently skipped: confirm tracking with `jj status`. Tracked edits still snapshot; untracked files have no
jj snapshot or operation-history protection.

## Read The jj State

- `@` is the working-copy commit. Most commands first snapshot tracked disk changes; there is no continuous save.
  `--ignore-working-copy` deliberately reads potentially stale state.
- There is no staging area. `jj file track` tracks a new path, not selected edits.
- Prefer change IDs, which survive ordinary rewrites. Commit hashes identify exact versions and change on rewrites,
  including content, parent or description changes. If a change ID diverges, inspect its versions rather than guess.
- `@-` selects parent revision(s), not necessarily completed work. Inspect the graph before selecting targets.
- There is no current/checked-out bookmark. Local bookmarks follow rewrites, not the working copy. Inspect and explicitly
  move the intended PR bookmark; do not assume a personal alias or configuration advances it.

Inspect with `jj --no-pager log`, `jj --no-pager diff --git`, `jj show`, and `jj status`. Supply `-m` messages,
paths/filesets for non-interactive selection, and explicit revisions when defaults could select other work. Read
installed `jj help <command>` for unfamiliar/version-sensitive options; do not invoke an interactive editor instead.
More examples: [command reference](references/commands.md).

## Work And Review Fixes

Ordinary work: `jj commit -m ...` describes the change and advances to a new working-copy commit. Describe-first is also
valid: `jj describe -m ...`, then `jj new` when starting the next change. Neither style permanently finishes a change or
makes it immutable.

Keep dependent changes connected. A PR may contain multiple commits; name bookmarks at PR boundaries, not every small
commit. To fix an earlier change:

1. Identify the target and save the actual tip's change ID/bookmark. Empty, undescribed `@` may be abandoned on leaving:
   save its parent/PR tip instead. To resume unfinished work, snapshot intended files and save that change. Inspect
   remaining untracked paths before moving.
2. `jj new <target-change>`; make the fix there and explicitly track new paths.
3. Inspect and run applicable checks before folding the fix.
4. `jj squash --into <target-change> --use-destination-message` preserves the destination description. Descendants
   rebase; their local bookmarks follow the rewritten versions.
5. Inspect earliest descendant conflicts with `jj log -r 'roots(conflicts() & <target-change>::)'`. Resolve this task's
   affected changes earliest first: use
   `jj new <conflicted-change>`, resolve markers, check the resolved child, then
   `jj squash --into <conflicted-change> --use-destination-message`. Repeat until the changes you will resume/publish
   are conflict-free; prefer this to editing conflicted revisions directly.
6. For new work, `jj new <tip-change>`; to resume preserved, conflict-free work, `jj edit <in-progress-change>`.
   Inspect needed code changes: automatic rebasing does not repair API incompatibilities.

Direct `jj edit <target>` amendments are an alternative, but mix original and new changes in the diff. `jj absorb` can
distribute fixes to mutable ancestors; inspect destinations and the remainder in `@`. Neither replaces identifying
where a fix belongs.

## Existing pre-commit

Git hooks do not automatically run for jj operations. Resolve `scripts/pre-commit.sh` from this skill, not the project;
invoke its actual absolute path from the target workspace:

```sh
bash /path/to/jujutsu/scripts/pre-commit.sh
# Optional pre-commit arguments, such as a particular hook:
bash /path/to/jujutsu/scripts/pre-commit.sh gitleaks --all-files
```

Default: `pre-commit run --all-files`. The adapter snapshots tracked `@` without auto-tracking and refuses unresolved
conflicts, whose Git trees contain jj's conflict metadata. It uses a temporary index/private HEAD and the actual
worktree, keeping formatter edits visible. Hook failures remain failures; inspect formatter edits and rerun. Check the
intended work while it is still in `@`, before `jj commit`, `jj new`, or `jj squash` moves it away. Relative arguments
such as `--files` retain the caller's directory context.

Private HEAD is `@`'s first Git parent, or unborn at a root commit. For a conflicted parent, the temporary Git view disables
Git's default rename detection so internal conflict artifacts do not hide new-file additions; hooks that force `-M`
are not covered. Staged hooks such as Gitleaks remain
independent of backing HEAD. `--all-files` selects runner inputs; it does not widen staged hooks to whole-tree/history
scanning or check every commit a push could publish.

Requires Bash, Git, Git-backed jj, and existing `pre-commit` executable/configuration; supports colocated and
non-colocated workspaces. Hooks retain project authority and may change files; this is not a sandbox.

## Publish And Recover

Inspect `jj bookmark list`; select actual PR boundaries, not automatically `@`/`@-`. Create/move the intended bookmarks.
An ancestor fix can move several PR boundaries: `jj git push --bookmark <a> --bookmark <b> --dry-run` previews the
selected updates; remove `--dry-run` to publish the same list. Local rewrites are not auto-pushed. GitHub PR creation,
base changes and merges are outside jj's bookmark model.

For conflicts, use the scoped child-resolution workflow above. Before rollback, inspect `jj op log` and
`jj evolog -r <change>`; `jj undo` is not universally safe in shared state. Workspaces separate working
directories but share history and an operation log. See the reference for workspace/recovery commands.

Resolve technical disagreements with installed help and [official documentation](references/commands.md#official-documentation).
