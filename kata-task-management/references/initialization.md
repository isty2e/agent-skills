# Initialize Without Unrelated Repository Changes

Use only for a missing CLI or workspace setup, not simple questions or repository inspection.

## Confirm The Target

1. Check `kata --version` and `kata --help`. If absent, consult the
   [official installation guide](https://www.katatracker.com/docs/get-started/install/) under software-installation policy;
   assume no package manager, install location, or privilege escalation.
2. Confirm workspace/project, repository instructions, and effective daemon. Check explicit selectors,
   `.kata.toml`/`.kata.local.toml`, and inherited configuration/environment without exposing credentials. Workspace and
   Git-root boundaries may differ.
3. Use an installed, documented read command to resolve the project; reuse valid bindings. A missing file does not prove
   no project/alias exists. Connection/permission errors do not justify initialization or a replacement local project.
4. Read `kata init --help`: installed flags/defaults govern, not a possibly newer website. Resolve ambiguous project
   selection before writing; do not force a fit with replacement/reassignment flags.

## Initialize And Keep Setup Local

Before initialization, preserve contents and tracked/staged/unstaged/untracked state of potentially affected files,
including `.gitignore`, `AGENTS.md`, `CLAUDE.md`, and Kata configuration. Status alone cannot distinguish existing edits.

Initialize in the confirmed workspace with the needed project selection and no optional integrations. Agent-guidance
and hook installation require separate requests. Inspect actual file/binding effects even with integrations omitted or
initialization errors; defaults vary by version and failure need not be atomic. Inspect before retrying.

Default to local-only setup, but preserve established repository policy and intentionally tracked configuration rather
than silently converting them. For a new local setup in Git:

1. Compare against the baseline. Remove only initialization-added Kata guidance and ignore entries; preserve existing
   guidance, unrelated edits, and staging. No blanket Kata-block removal or `git restore` over unrelated changes.
2. Retain configuration needed for binding/daemon access; do not delete it merely to clean status. Exclude newly local
   configuration through Git's local exclude file, not shared `.gitignore`. Resolve it from the relevant worktree:

   ```sh
   git rev-parse --git-path info/exclude
   ```

   Preserve entries and append only missing rules for actual paths. At the repository root:

   ```gitignore
   /.kata.toml
   /.kata.local.toml
   ```

   Adjust for nested workspaces; never ignore all TOML files. Linked worktrees may share this file. Outside Git, skip
   excludes; never create a fake `.git` directory.
3. Excludes do not affect tracked files. Do not `git rm --cached`, delete tracked configuration, or rewrite history to
   enforce this default. Resolve policy/setup conflicts with the operator.

## Verify

- Read back the binding and run a non-mutating command against the intended project/daemon; a config file proves neither
  connection nor project selection.
- Run `git check-ignore -v` on actual local config paths and inspect staged/unstaged diffs and untracked files. Confirm no
  unrelated changes, unwanted guidance/hooks, or shared ignore edits remain.
- Run `kata quickstart` unless already read for this session/environment, then return to registration. No sample issue
  for setup testing: the next issue must represent real work.
