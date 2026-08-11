---
name: typst-author
description:
  Generate idiomatic Typst (.typ) code, edit and troubleshoot Typst documents and projects, and answer Typst
  syntax/reference questions. Use when working with .typ files or when the user asks for Typst document creation,
  editing, debugging, compilation, formatting, template work, or package usage.
---

# Typst authoring

Generate, edit, and validate Typst documents. Treat the installed compiler and current official Typst documentation as
the authority for version-sensitive syntax and behavior.

## Workflow

1. Check the installed compiler with `typst --version` when available.
2. Inspect the existing project structure, imports, fonts, and compiler options before editing.
3. Consult official Typst sources for unfamiliar or version-sensitive behavior. Match documentation to the installed
   compiler version when practical.
4. Generate or edit the `.typ` source while preserving the project's established style.
5. When `typstyle` is available, run `typstyle --check <changed-file>` on each changed Typst file. Inspect
   `typstyle --diff <changed-file>` before applying formatting, and do not reformat untouched code without approval.
6. Run `typst compile <input.typ> [output]` after editing when tool access is available. Use `typst eval '<expression>'`
   for small fileless probes that do not require document context.
7. Report changed files, validation performed, and any compiler, package, font, or network limitation.

## Official documentation

Do not rely on a vendored documentation snapshot. Retrieve current information from the sources that own it:

- Use <https://typst.app/docs/> for the complete rendered documentation, including the tutorial, guides, reference, and
  changelog.
- Use <https://github.com/typst/typst/tree/main/docs> when source-level search or local inspection is more useful.
  Hand-written documentation lives primarily under `docs/content` and is supplemented by Typst markup in Rust doc
  comments throughout the repository, so `docs/content` alone is not the complete API reference.
- For version-specific source inspection, check out the repository tag matching `typst --version` when one exists rather
  than assuming `main` matches the user's compiler.
- Use <https://typst.app/universe/> to verify package names and released versions instead of guessing them.

Prefer fetching or searching only the relevant official page or source path. If a local clone is useful, place it in a
temporary workspace outside the user's project and remove it afterward unless the user asks to keep it. Do not copy the
full upstream documentation into the user's repository unless the user explicitly requests an offline snapshot.

When official documentation is unavailable, use `typst help`, compiler diagnostics, `typst eval`, and minimal temporary
compile probes. Clearly label conclusions that could not be checked against the matching official version.

## Minimal document example

```typst
#set page(numbering: "1")
#set text(lang: "en")
#set par(justify: true)

= My Document

This is a paragraph in Typst.

== A second-level heading

#lorem(40)
```

## Syntax guardrails

### Values and blocks

- Arrays use parentheses: `(item1, item2)`. A one-item array requires a trailing comma: `(item,)`.
- Dictionaries also use parentheses, with named entries: `(key: value, other: value)`.
- Content blocks use square brackets: `[markup content]`.
- Code blocks use braces: `{ let x = 1; x + 1 }`.
- Typst has arrays, not a separate tuple type.
- Access array elements with methods such as `items.at(0)`, not `items[0]`.

### Markup and code mode

Use `#` to enter code from markup or a content block. Do not add another `#` when already inside code, such as an
argument list, code block, or function body.

```typst
// Markup mode: # enters code.
#figure(image("diagram.svg"), caption: [Architecture])

// Content block: # enters code for numbering(...).
#text()[Section #numbering("1.1", 2, 3)]

// Code block: no # before expressions.
#{
  let values = (1, 2, 3)
  values.map(value => value * 2)
}
```

### Set and show rules

- Use a `set` rule to configure optional parameters on an element within a scope.
- Use a show-set rule to apply settings only to selected elements.
- Use a show transformation when output must be structurally replaced or reshaped.

```typst
#set heading(numbering: "1.")
#set text(font: "New Computer Modern")

#show heading.where(level: 1): set text(fill: navy)
#show emph: it => underline(it.body)
```

## Packages and multi-file projects

- Split source with `#include "chapter.typ"` or import definitions with `#import "module.typ": name`.
- Use fully versioned Typst Universe imports such as `#import "@preview/package:1.2.3": item`.
- Universe packages are downloaded on demand and cached locally. Offline compilation works only when the required
  package version is already available locally or supplied through a configured package path.
- Remember that project and package file access is constrained by Typst roots. Inspect the relevant compiler options and
  project layout before changing paths.

## Troubleshooting

### Compiler diagnostics

Read the reported source span and identify the current language mode before changing syntax.

- For `unknown variable`, verify spelling, imports, scope, and namespace qualification.
- For content/expression errors, check whether code is missing `#` in markup or incorrectly contains `#` in code mode.
- For array or dictionary errors, verify parentheses, commas, and `key: value` entries.
- For version-dependent failures, compare `typst --version` with the matching official changelog or source tag.

### Fonts

Use `typst fonts` to inspect available families. Missing-font warnings can fall back and still compile, but fallback may
change metrics, line breaks, and pagination. Preserve an explicitly requested font when possible; otherwise choose an
available substitute or ask the user rather than silently deleting typography requirements.

### Packages

If a package import fails:

1. Verify the exact `@namespace/name:version` import against Typst Universe.
2. Confirm network access for the first download or ensure the package is already cached or provided locally.
3. Inspect configured package paths and the complete compiler diagnostic.
4. Do not invent package versions or assume that changing caches will fix a malformed import.

## Common mistakes to avoid

- Writing LaTeX commands such as `\\begin`, `\\section`, or `\\frac` in Typst markup.
- Inventing LaTeX-like environments such as `tabular`; use Typst's `table` element.
- Using `[]` for arrays or `arr[0]` for array access.
- Confusing content blocks `[]` with code blocks `{}`.
- Adding `#` inside code mode or omitting it when entering code from markup.
- Dropping a module or package namespace without explicitly importing the referenced item.
- Claiming validation when `typst compile` was not run.
