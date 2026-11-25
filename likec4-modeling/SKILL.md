---
name: likec4-modeling
description: >-
  Author, organize, validate, format, preview, and export LikeC4 models. Use for `.c4`/`.likec4` files or LikeC4 DSL,
  CLI, and diagram export requests.
license: MIT
---

# LikeC4 Modeling

Model accepted architecture. Keep behavior requirements and change rationale in their owning records; link when useful.
For model or view syntax, read the [DSL reference](references/dsl.md).

## Edit The Model

- Follow existing model roots, configuration, and file conventions. Default new models to `architecture/` with
  `specification.c4`, `model/<boundary>.c4`, and `views/<boundary>.c4`. Add deployment files only when modeling
  deployments, and configuration only for needed options or separate LikeC4 projects.
- Split files by responsibility, not PR. Reuse element and relationship kinds unless the model needs a new distinction.
  Keep IDs stable. If an ID, parent, kind, or relationship changes, check references and affected views across files.
  Validation does not catch valid but unintended changes to what a view shows.
- Edit the current model for Git review. Use `diff` blocks only when an unapplied model proposal is useful.

## Use The CLI

Use the project's LikeC4 version and launcher. Examples assume `likec4` on `PATH`, run from the repository root.

- Format touched files: `likec4 format architecture --files architecture/model/jobs.c4`; add `--check` to avoid writes.
- After editing, validate the affected model: `likec4 validate architecture`. Omit `--file` to see broken references in
  untouched files. Validation checks the model and stale manual layouts, not the implementation.
- Browser preview: `likec4 start architecture` runs a local server until stopped.
- Mermaid export: `likec4 gen mmd -o <output-dir> architecture`. Use scratch or CI output unless the repository tracks
  generated diagrams.
- List declared `diff` blocks: `likec4 diff list architecture`. Compare branches with Git.
- Inspect removal without edits: `likec4 safe-delete jobs.recovery --dry-run architecture`.

Check installed `--help` for version-specific flags and the [CLI reference](https://likec4.dev/tooling/cli/) for other
commands. If the CLI is unavailable, report which checks or outputs were not run.

LikeC4 renders `variant sequence` as a sequence; `gen mmd` still exports a flowchart. Write native Mermaid
[`sequenceDiagram`](https://mermaid.js.org/syntax/sequenceDiagram.html) or
[`stateDiagram-v2`](https://mermaid.js.org/syntax/stateDiagram.html) directly.
