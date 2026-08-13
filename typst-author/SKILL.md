---
name: typst-author
description: >-
  Generate idiomatic Typst (.typ), edit and troubleshoot Typst documents or projects, and answer syntax or reference
  questions. Use for Typst creation, compilation, formatting, templates, packages, fonts, or debugging.
---

# Typst Authoring

Generate, edit, and validate Typst. Treat the installed compiler and current official documentation as authority for
version-sensitive behavior.

## Workflow

1. Run `typst --version` when available.
2. Inspect project structure, imports, fonts, and compiler options before editing.
3. Check unfamiliar or version-sensitive behavior against official sources matching the installed version when
   practical.
4. Edit `.typ` while preserving project style.
5. If available, run `typstyle --check <changed-file>` for each changed file and inspect
   `typstyle --diff <changed-file>` before formatting. Do not reformat untouched code without approval.
6. Compile with `typst compile <input.typ> [output]` when possible. Use `typst eval '<expression>'` for small probes that
   need no document context.
7. Report changed files, checks, and compiler, package, font, or network limitations.

## Official Sources

- <https://typst.app/docs/>: rendered tutorial, guides, reference, and changelog.
- <https://github.com/typst/typst/tree/main/docs>: source-level search. Handwritten `docs/content` is supplemented by
  Typst markup in Rust doc comments, so it is not the complete API reference.
- A repository tag matching `typst --version`: version-specific source inspection; do not assume `main` matches.
- <https://typst.app/universe/>: released package names and versions.

Fetch only relevant official pages or paths. Put any useful clone in a temporary workspace outside the project and
remove it afterward unless asked to retain it. Never copy the full documentation into the repository without an
explicit offline-snapshot request.

If official sources are unavailable, use `typst help`, diagnostics, `typst eval`, and minimal temporary compile probes;
label conclusions not checked against the matching version.

## Syntax Guardrails

- Arrays use `(a, b)`; one item requires `(a,)`. Dictionaries use `(key: value)`. Typst has no separate tuple type.
- Content blocks use `[markup]`; code blocks use `{ let x = 1; x + 1 }`.
- Access arrays with methods such as `items.at(0)`, not `items[0]`.
- Use `#` to enter code from markup or content. Do not add `#` inside argument lists, code blocks, or function bodies.
- Use `set` for optional element parameters, show-set for selected elements, and show transformations for structural
  replacement.

```typst
#set heading(numbering: "1.")
#show heading.where(level: 1): set text(fill: navy)
#show emph: it => underline(it.body)

#figure(image("diagram.svg"), caption: [Architecture])
#text()[Section #numbering("1.1", 2, 3)]
#{
  let values = (1, 2, 3)
  values.map(value => value * 2)
}
```

## Projects And Packages

- Split source with `#include "chapter.typ"`; import definitions with `#import "module.typ": name`.
- Use fully versioned Universe imports such as `#import "@preview/package:1.2.3": item`.
- Universe packages download on demand and cache locally. Offline builds require the exact version in cache or a
  configured package path.
- Typst roots constrain project and package file access; inspect compiler options and layout before changing paths.

## Troubleshooting

Read the diagnostic source span and identify the current language mode before changing syntax.

- `unknown variable`: check spelling, imports, scope, and namespace.
- Content/expression error: check for missing `#` in markup or extra `#` in code.
- Array/dictionary error: check parentheses, commas, and `key: value` entries.
- Version failure: compare `typst --version` with the matching changelog or source tag.
- Missing font: inspect `typst fonts`. Fallback may compile but alter metrics, line breaks, and pagination; preserve an
  explicitly requested font, otherwise choose an available substitute or ask rather than silently dropping it.
- Package import failure: verify exact `@namespace/name:version` in Universe, first-download network access or local
  availability, configured package paths, and the full diagnostic. Do not invent versions or assume cache changes fix a
  malformed import.

Do not write LaTeX `\begin`, `\section`, or `\frac`, or invent `tabular`; use Typst elements such as `table`. Also avoid
`[]` arrays or `arr[0]`, content/code block confusion, misplaced `#`, and dropping a namespace without importing its
item. Never claim validation unless the reported command ran.
