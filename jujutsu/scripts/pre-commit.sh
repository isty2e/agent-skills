#!/usr/bin/env bash
# Run existing pre-commit hooks against the current jj snapshot.
set -eu

for executable in jj git pre-commit; do
    if ! command -v "$executable" >/dev/null 2>&1; then
        printf 'Required executable not found: %s\n' "$executable" >&2
        exit 127
    fi
done

# Resolve this invocation's repository, not a caller's inherited Git context.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR
unset GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES

root=$(jj --ignore-working-copy workspace root)
root=$(cd "$root" && pwd -P)
nearest_git=$(git rev-parse --show-toplevel 2>/dev/null || true)
if [ -n "$nearest_git" ]; then
    nearest_git=$(cd "$nearest_git" && pwd -P)
    case "$nearest_git/" in
        "$root/"*)
            if [ "$nearest_git" != "$root" ]; then
                printf 'Current directory belongs to a nested Git repository, not the enclosing jj workspace\n' >&2
                exit 1
            fi
            ;;
    esac
fi

snapshot=$(jj --no-pager --color never --config 'snapshot.auto-track="none()"' \
    show --no-patch -r @ -T 'commit_id')
conflicted=$(jj --no-pager --color never --ignore-working-copy log --no-graph \
    -r "conflicts() & $snapshot" -T 'commit_id')
if [ -n "$conflicted" ]; then
    printf 'Resolve conflicts in the current jj change before running pre-commit\n' >&2
    exit 1
fi
backing=$(jj --ignore-working-copy git root)
common=$(git --git-dir="$backing" rev-parse --path-format=absolute --git-common-dir)
ancestry=$(git --git-dir="$backing" rev-list --parents -n 1 "$snapshot")
read -r _ parent_id _ <<< "$ancestry"
parent_conflicted=
if [ -n "$parent_id" ]; then
    parent_conflicted=$(jj --no-pager --color never --ignore-working-copy log --no-graph \
        -r "conflicts() & $parent_id" -T 'commit_id')
fi

temporary=$(mktemp -d)
trap 'rm -rf -- "$temporary"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
mkdir "$temporary/git"
printf '%s\n' "$common" > "$temporary/git/commondir"
if [ -n "$parent_id" ]; then
    printf '%s\n' "$parent_id" > "$temporary/git/HEAD"
else
    # refs/worktree is private to this Git directory, including for an unborn HEAD.
    printf 'ref: refs/worktree/pre-commit-root\n' > "$temporary/git/HEAD"
fi

export GIT_DIR="$temporary/git"
export GIT_COMMON_DIR="$common"
export GIT_WORK_TREE="$root"
export GIT_INDEX_FILE="$temporary/index"
git read-tree "$snapshot"

if [ -n "$parent_conflicted" ]; then
    # Conflict artifacts must not become rename sources that hide new-file additions.
    slot=$((10#${GIT_CONFIG_COUNT:-0}))
    export "GIT_CONFIG_KEY_$slot=diff.renames" "GIT_CONFIG_VALUE_$slot=false"
    export GIT_CONFIG_COUNT=$((slot + 1))
fi

if [ "$#" -eq 0 ]; then
    set -- --all-files
fi
status=0
pre-commit run "$@" || status=$?
exit "$status"
