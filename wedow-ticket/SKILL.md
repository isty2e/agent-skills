---
name: wedow-ticket
description: Operate wedow/ticket safely through tk or ticket. Load and apply when creating, inspecting, querying, relating, or editing .tickets Markdown; first identify the CLI, then preserve repository scope, shell literals, full IDs, dependency direction, JSONL parsing, and noninteractive note/edit behavior.
---

# wedow/ticket

## Identify And Scope

Never infer the implementation from the executable name.

```bash
command -v tk
tk help
```

Treat it as wedow/ticket only when help matches at least two markers such as `minimal ticket system with dependency tracking`, `Tickets stored as markdown files in .tickets/`, `super <cmd>`, `dep tree`, `dep cycle`, `ready`, `blocked`, `add-note`, or `tk-<cmd>`/`ticket-<cmd>` plugins. If `tk` is absent, apply the same test to `ticket`. Otherwise stop this workflow and inspect that CLI's help/source.

Use installed help as authoritative; `ls`, `list`, `query`, and `edit` may be plugins. Before writing:

```bash
echo "${TICKETS_DIR:-}"
```

`TICKETS_DIR` overrides parent `.tickets/` discovery. Confirm the intended repository/task set and its policy for tracking `.tickets/`.

wedow/ticket has no `tk init`. The first successful `create` initializes `.tickets/` locally when no parent directory exists. If the user asked only to inspect and none exists, report that; do not create one.

## Command Contracts

- Quote every multi-word title as one argument. `tk create Three Words` creates a ticket titled `Words`.
- Prefer statuses `open`, `in_progress`, `closed` and types `bug`, `feature`, `task`, `epic`, `chore`, unless repository convention overrides them.
- There is no generic `tk update`; use `start`, `close`, `reopen`, `status`, `dep`, `undep`, `link`, `unlink`, `add-note`, or deliberately patch the Markdown file.
- Use full IDs in scripts, batch creation, relationship edits, and final reports. Partial IDs are interactive substring matches and may become ambiguous.
- `tk dep <id> <dep-id>` means the second ticket blocks the first. `--parent` adds hierarchy without blocking; `link` is symmetric context without ordering.
- `tk query` emits JSONL, not one JSON document.

## Safe Creation

```bash
id=$(tk create "Clarify query JSONL handling" -t task -p 2) || {
  echo "tk create failed" >&2
  exit 1
}
[[ -n "$id" ]] || {
  echo "tk create returned an empty ID" >&2
  exit 1
}
tk show "$id" >/dev/null
```

Treat output as an ID only after success and a non-empty check. If it is not one ID, inspect plugin shadowing; use `tk super create ...` only when core behavior is specifically required.

Keep titles short. Put Markdown, code, backticks, `$vars`, quotes, checklists, and multiline text in descriptions, acceptance text, or notes. Never put backticks in double-quoted shell arguments:

```bash
# Bad: shell expansion can run or alter content.
tk create "Fix `foo` handling" -d "Handle `bar` and $BAZ"

# Safe for short literal text without single quotes.
tk create 'Fix `foo` handling' -d 'Handle `bar` and $BAZ literally'
```

Use a quoted heredoc for multiline payloads:

```bash
description=$(cat <<'EOF'
Goals:
- Preserve `tk query` JSONL behavior.
- Avoid interpreting $VARS, `backticks`, or \n.
- Keep shell quoting boring.
EOF
)

id=$(tk create "Harden ticket creation workflow" -t task -p 2 -d "$description")
```

Do not use `echo -e`; use `printf` or quoted heredocs. Prefer named ID variables over ad hoc arrays; zsh arrays are 1-indexed. For tables, fenced code, or many acceptance criteria, create simple metadata first, then deliberately patch `.tickets/<id>.md`.

## Notes And Deterministic Edits

Never run bare `tk add-note <id>` in an agent shell; non-TTY stdin can append an empty timestamped note. Provide text or stdin:

```bash
tk add-note "$id" <<'EOF'
Observed issue:
- Shell quoting can reinterpret backticks, $(), $, backslashes, and newlines.
EOF
```

Use an argument only for short literal notes. Treat `tk edit` as plugin-gated and interactive; in non-TTY mode it may only print `Edit ticket file: <path>`. Resolve the file via `show` or `edit`, patch `.tickets/<id>.md` deliberately, then rerun `tk show <id>`.

## Relationships, Queries, And Plugins

Add dependencies only for real execution blockers, never merely because a task belongs to an epic. Verify relationship changes:

```bash
tk dep cycle
tk ready
tk blocked
tk show <id>
```

Parse queries line by line or slurp explicitly:

```bash
tk query '.status == "open"'
tk query | jq -s 'map(select(.status == "open"))'
```

Use `query` for frontmatter. Read `.tickets/*.md` for exact prose, unusual quoting, or complex body analysis.

Bare commands may be shadowed by `tk-<cmd>` or `ticket-<cmd>` executables. Use normal `tk <cmd>` by default; inspect help and use `tk super <cmd>` only when shadowing is suspected or core behavior is required.

## Common Failures

- `Unknown command: init`: no init command; create only when a new ticket set is intended.
- `Unknown command: query`: query plugin is unavailable.
- `Edit ticket file: <path>`: noninteractive edit did not modify the file.
- `no .tickets directory found`: check working directory/`TICKETS_DIR`; create only on request.
- `ambiguous ID` or `ticket '<id>' not found`: verify `TICKETS_DIR` and use the full ID.

## Bulk Workflow

1. Identify the CLI and ticket root.
2. Confirm repository tracking policy.
3. Create root epics and capture checked full IDs.
4. Create children with `--parent`.
5. Add only true blockers with `dep`; add context with `link`.
6. Run `dep cycle`, `ready`, `blocked`, and representative `show` checks.
7. Run `git status` before staging or reporting ticket changes.
