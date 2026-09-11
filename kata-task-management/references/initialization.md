# Initialize Without Unrelated Repository Changes

Use this procedure only when Kata is missing or the intended workspace needs setup. Initialization is not a prerequisite
for answering a simple question or inspecting a repository.

## Confirm The Target

1. Identify the installed CLI with `kata --version` and `kata --help`. If it is absent, consult the
   [official installation guide](https://www.katatracker.com/docs/get-started/install/); follow the environment's software
   installation policy. Do not assume a package manager, install location, or privilege escalation is available.
2. Confirm the intended workspace/project, applicable repository instructions, and effective daemon selection. Check
   explicit selectors, existing `.kata.toml`/`.kata.local.toml` configuration, and inherited configuration or environment
   overrides without exposing credentials. Workspace discovery and Git root are not necessarily the same boundary.
3. Check whether that workspace already resolves to the intended project using an installed, documented read command.
   Reuse valid bindings. A missing file alone does not prove that no project or alias exists. A connection or permission
   error is not evidence that initialization is needed; do not create a replacement local project to bypass it.
4. Run `kata init --help`. Installed help governs flags and defaults; the website may describe a newer version.
   Resolve an ambiguous project choice before writing, and do not use replacement or reassignment flags to force a fit.

## Initialize Only What Is Needed

Before initialization, record the existing tracked, staged, unstaged, and untracked state of the files it may touch,
including `.gitignore`, `AGENTS.md`, `CLAUDE.md`, and Kata configuration. Preserve their original contents; a status listing
alone cannot distinguish pre-existing edits from new additions.

Initialize from the confirmed workspace with the needed project selection and no optional integrations. Do not add
agent-guidance or hook-installation options unless separately requested. For example, v0.16.0 help documents:

- `.kata.toml` as a workspace/project binding intended for committing;
- an automatic `.kata.local.toml` addition to `.gitignore`;
- `--with-agents` as opt-in modification of AGENTS.md/CLAUDE.md, with separate hook options.

Do not generalize these defaults to every version. Inspect actual changes even when optional integrations were omitted.
If initialization reports an error, inspect its file and binding effects before retrying; do not assume it was atomic.

## Keep Local Setup Local

This skill defaults to local-only setup, rather than Kata's suggested committed binding. Preserve an established
repository policy or intentionally tracked configuration; do not silently convert it to local-only storage.

For a new local setup in a Git worktree:

1. Compare changes with the recorded baseline. Remove only newly introduced Kata guidance in AGENTS.md/CLAUDE.md and
   initialization-added ignore entries. Preserve existing guidance, unrelated edits, and staging. Do not blanket-remove
   every Kata block or use `git restore` on files containing unrelated changes.
2. Keep the configuration needed for the binding and daemon connection; do not delete it to make Git status clean.
   Exclude the newly local configuration through Git's local exclude file instead of a shared `.gitignore`.
3. Resolve that file from the relevant Git worktree rather than assuming `.git` is a directory:

   ```sh
   git rev-parse --git-path info/exclude
   ```

   Preserve existing entries and append only missing rules for the actual configuration paths. For configuration at the
   repository root, the rules are:

   ```gitignore
   /.kata.toml
   /.kata.local.toml
   ```

   Adjust paths for a nested workspace; do not ignore every TOML file. Linked worktrees may share this exclude file.
   For a workspace outside Git, no exclude file is needed; do not create a fake `.git` directory.
4. Excludes do not affect tracked files. Do not run `git rm --cached`, delete tracked configuration, or rewrite history
   to enforce this default. If existing policy and requested setup conflict, resolve that choice with the operator.

## Verify The Result

- Read back the binding and run a non-mutating Kata command against the intended project/daemon. Merely producing a
  configuration file does not prove the connection or project selection works.
- Use `git check-ignore -v` on the actual local configuration paths and inspect staged and unstaged diffs plus untracked
  files. Confirm no unrelated changes, unwanted guidance, hooks, or shared ignore edits were left by initialization.
- Run `kata quickstart` if it has not already been read for this session/environment, then return to task registration.
  Do not create a sample issue as a setup test; the next issue should represent real work.
