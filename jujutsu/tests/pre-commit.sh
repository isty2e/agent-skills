#!/usr/bin/env bash
# Native, local-only integration cases for the staged snapshot adapter.
set -eu

script=$(cd "$(dirname "$0")/../scripts" && pwd)/pre-commit.sh
scratch=$(mktemp -d)
trap 'rm -rf -- "$scratch"' EXIT
export HOME="$scratch/home" PRE_COMMIT_HOME="$scratch/cache"
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
mkdir -p "$HOME"
unset JJ_CONFIG GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR GIT_INDEX_FILE

for layout in colocated non-colocated; do
    workspace="$scratch/$layout workspace"
    if [ "$layout" = colocated ]; then
        jj git init --colocate "$workspace" >/dev/null
    else
        jj git init --no-colocate "$workspace" >/dev/null
    fi
    cd "$workspace"
    jj --ignore-working-copy config set --repo user.name Fixture
    jj --ignore-working-copy config set --repo user.email fixture@example.invalid
    jj --ignore-working-copy config set --repo snapshot.auto-track 'none()'
    export HOOK_RECEIPT="$scratch/$layout-receipt" FILE_RECEIPT="$scratch/$layout-file-receipt"
    cat > .pre-commit-config.yaml <<'YAML'
repos:
  - repo: local
    hooks:
      - id: staged-content
        name: Inspect staged content
        language: system
        entry: >-
          sh -c 'needle=DO_NOT_; needle=${needle}PUBLISH;
          patch=$(git diff --cached --no-ext-diff --no-color --unified=0 -- .) || exit $?;
          result=0; if printf "%s\n" "$patch" | grep "^+[^+]" | grep -F "$needle" > /dev/null;
          then result=1; fi;
          printf "%s" "$result" > "$HOOK_RECEIPT"; exit "$result"'
        pass_filenames: false
      - id: formatter
        name: Format fixture
        language: system
        entry: sh -c 'if test -f format-me; then printf formatted > format-me; fi'
        pass_filenames: false
      - id: relative-path
        name: Read selected file
        language: system
        entry: sh -c 'cat "$1" > "$FILE_RECEIPT"' --
YAML
    printf 'DO_NOT_PUBLISH\n' > historical.txt
    printf 'base\n' > safe.txt
    jj file track .pre-commit-config.yaml historical.txt safe.txt >/dev/null

    if bash "$script" > "$scratch/output" 2>&1; then
        printf 'Root snapshot unexpectedly passed\n' >&2
        exit 1
    fi
    test "$(cat "$HOOK_RECEIPT")" = 1
    jj commit -m 'Fixture baseline' >/dev/null

    printf 'changed\n' > safe.txt
    printf 'DO_NOT_PUBLISH\n' > untracked.txt
    jj status >/dev/null
    backing=$(jj --ignore-working-copy git root)
    index=$(git --git-dir="$backing" rev-parse --git-path index)
    if [ -f "$index" ]; then cp "$index" "$scratch/index-before"; fi
    bash "$script" staged-content --all-files > "$scratch/output" 2>&1 || { cat "$scratch/output"; exit 1; }
    test "$(cat "$HOOK_RECEIPT")" = 0
    if [ -f "$scratch/index-before" ]; then
        cmp "$index" "$scratch/index-before"
        rm "$scratch/index-before"
    else
        test ! -e "$index"
    fi
    snapshot=$(jj --ignore-working-copy show --no-patch -T commit_id)
    if git --git-dir="$backing" cat-file -e "$snapshot:untracked.txt" 2>/dev/null; then
        printf 'Untracked file entered the snapshot\n' >&2
        exit 1
    fi
    jj file track untracked.txt >/dev/null
    if bash "$script" > "$scratch/output" 2>&1; then
        printf 'Tracked forbidden content unexpectedly passed\n' >&2
        exit 1
    fi
    test "$(cat "$HOOK_RECEIPT")" = 1
    rm untracked.txt

    printf unformatted > format-me
    jj file track format-me >/dev/null
    if bash "$script" > "$scratch/output" 2>&1; then
        printf 'Formatter change unexpectedly passed\n' >&2
        exit 1
    fi
    test "$(cat format-me)" = formatted
    bash "$script" > "$scratch/output" 2>&1 || { cat "$scratch/output"; exit 1; }

    mkdir sub
    printf 'selected input\n' > sub/selected.txt
    jj file track sub/selected.txt >/dev/null
    (cd sub && bash "$script" relative-path --files selected.txt) > "$scratch/output" 2>&1 || {
        cat "$scratch/output"; exit 1;
    }
    cmp sub/selected.txt "$FILE_RECEIPT"

    base=$(jj --ignore-working-copy show --no-patch -T commit_id)
    jj new "$base" >/dev/null
    printf 'left\n' > safe.txt
    jj commit -m 'Left side' >/dev/null
    left=$(jj --ignore-working-copy show --no-patch -r '@-' -T commit_id)
    jj new "$base" >/dev/null
    printf 'right\n' > safe.txt
    jj commit -m 'Right side' >/dev/null
    right=$(jj --ignore-working-copy show --no-patch -r '@-' -T commit_id)
    jj new "$left" "$right" >/dev/null
    test -n "$(jj --ignore-working-copy log --no-graph -r 'conflicts() & @' -T commit_id)"
    rm "$HOOK_RECEIPT"
    if bash "$script" > "$scratch/output" 2>&1; then
        printf 'Conflicted snapshot unexpectedly passed\n' >&2
        exit 1
    fi
    test ! -e "$HOOK_RECEIPT"
    jj describe -m 'Conflicted merge' >/dev/null
    jj new >/dev/null
    test -n "$(jj --ignore-working-copy log --no-graph -r 'conflicts() & @-' -T commit_id)"
    printf 'resolved\n' > safe.txt
    bash "$script" staged-content --all-files > "$scratch/output" 2>&1 || {
        cat "$scratch/output"; exit 1;
    }
    test "$(cat "$HOOK_RECEIPT")" = 0
    cp historical.txt conflict-copy.txt
    jj file track conflict-copy.txt >/dev/null
    if bash "$script" staged-content --all-files > "$scratch/output" 2>&1; then
        printf 'Conflict artifact hid a new tracked marker as a rename\n' >&2
        exit 1
    fi
    test "$(cat "$HOOK_RECEIPT")" = 1

    git init --quiet nested
    rm "$HOOK_RECEIPT"
    if (cd nested && bash "$script") > "$scratch/output" 2>&1; then
        printf 'Nested Git repository incorrectly used its jj parent\n' >&2
        exit 1
    fi
    test ! -e "$HOOK_RECEIPT"
    printf '%s: staged scope, tracking, index, formatter, subdirectory args, conflicts and boundary passed\n' "$layout"
done
