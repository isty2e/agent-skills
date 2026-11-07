# jj Command Reference

Native jj 0.47.1 examples complement [the skill](../SKILL.md). Replace angle-bracket placeholders before executing;
other versions: consult installed help.

## Inspect And Select

```sh
jj status
jj --no-pager log
jj --no-pager log -r 'trunk()..@'
jj --no-pager diff --git
jj --no-pager show <change>
jj show --no-patch -r @ -T 'change_id'
```

Shell-quote revsets. `X-`/`X+`: parents/children; `::X`/`X::`: ancestors/descendants including X; `X..Y`: ancestors of Y
minus ancestors of X; `X::Y`: X-to-Y paths, inclusive. `mutable()`: mutable changes; `conflicts()`: conflicted changes.
Help: `jj help -k revsets`. Default `jj log` is filtered; `-r '::@'` shows ancestry. `trunk()` is repository-configured;
built-in fallback can be `root()`, so `trunk()..@` then includes all history.

## Files And Changes

```sh
jj file track path/to/new-file
jj file untrack <path>
jj file list
jj describe -m 'Describe the current change'
jj commit -m 'Describe and advance to a new change'
jj new <base>
jj edit <change>
jj split path/to/component -m 'Describe the selected part'
jj squash --into <destination> --use-destination-message path/to/component
jj absorb
jj restore <path>
jj abandon <change>
```

`file track` skips ignored paths; confirm with `jj status`. Do not use `--include-ignored` to import private files.
Under `none()`, `file untrack` keeps disk files without auto-retracking. `restore`: reset selected file contents;
`abandon`: remove change and rebase descendants. Inspect selected-operation results/remainders.
`squash`: normally abandons emptied source, may replace `@` with a new empty commit; do not assume `@`
still names the source. `absorb`: can leave unassignable changes in `@`.

## Stacked Review Fixes

```sh
jj new <review-target>
# Make the fix, track new paths, inspect and check it.
jj squash --into <review-target> --use-destination-message
jj new <saved-stack-tip>
jj status
```

Advancing base: `jj rebase -b <stack-tip> -o <new-base>`. Distinct from ancestor amendments.

Immutability: `immutable_heads()`, not push alone. Do not bypass an immutable boundary to make an example work.

## Bookmarks And Remotes

```sh
jj bookmark list
jj bookmark create <pr-name> -r <pr-tip>
jj bookmark move <pr-name> --to <pr-tip>
jj bookmark track <name> --remote <remote>
jj git fetch
jj git push --bookmark <pr-name>
jj git push --bookmark <a> --bookmark <b> --dry-run
```

Remote-tracking state differs from local bookmarks. Track intended remote bookmarks when required by the workflow;
do not guess the remote or move all bookmarks. Publish each PR boundary that should reflect ancestor rewrites.
Conflicted bookmark: inspect versions, move to intended target.

## Workspaces And Recovery

```sh
jj workspace list
jj workspace add ../another-workspace -r <base>
jj workspace update-stale
jj op log
jj evolog -r <change>
jj undo
jj op revert <operation>
jj op restore <operation>
```

Stale workspace: inspect pending work; follow installed `jj help workspace update-stale`. Choose the intended recovery
operation; references and other workspace state can change. `jj workspace forget` leaves files; `jj workspace remove`
deletes them. `jj undo` refuses another workspace's operation; still inspect the intended one. Undoing push leaves the
remote update intact and may cause conflicted bookmarks.

## Official Documentation

- [Working copy and tracking](https://docs.jj-vcs.dev/latest/working-copy/)
- [Bookmarks](https://docs.jj-vcs.dev/latest/bookmarks/)
- [Configuration](https://docs.jj-vcs.dev/latest/config/)
- [Resuming an earlier change](https://docs.jj-vcs.dev/latest/FAQ/#how-do-i-resume-working-on-an-existing-change)
- [Git compatibility](https://docs.jj-vcs.dev/latest/git-compatibility/)

Snapshot/temporary-index approach: informed by
[Carbon's adapter](https://github.com/carbon-language/carbon-lang/blob/80a4a4d0052e4cc2e8b2fd99d28cd1d2793d8758/scripts/jj_prek.sh).
