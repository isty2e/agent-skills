---
name: github-math-comment
description: Draft, validate, publish, or edit GitHub issue and pull request comments with TeX. Use when GFM parsing, rendered display math, and posted-body equality must be verified.
license: MIT
---

# GitHub Math Comment

Draft in a temporary Markdown file outside the repository. Pass it with a body-file or JSON input, never through
expanding shell quoting.

## Guardrails

- **Display math:** use fenced `math`. In `$$`, a line containing only `=` can become a Setext heading and split the
  equation before math rendering.
- **Delimiters:** balance fences and inline delimiters. Do not compare raw `\left`/`\right` substrings; commands such
  as `\rightsquigarrow` create false matches.
- **Macros:** support is target-context behavior; an HTML wrapper does not prove client renderer acceptance. When
  `\operatorname` is unverified, use `\mathrm` where its semantics fit or another target-verified equivalent.
- **References:** if the comment contains scholarly references, apply `scholarly-reference-integrity` separately; this
  skill does not verify citations.

## Publish Only After

1. Render the complete source through GitHub's Markdown API in GFM mode with the target repository as context.
2. Require one display node per fenced `math` block; rendered heading counts must match the intended source headings.
   Current display nodes use `js-display-math`; inspect current output because the selector may change.
3. Inspect representative formulas in math-renderer nodes. Macro-sensitive content also needs GitHub's UI preview or
   another client-renderer check; a nonzero wrapper count is insufficient.
4. Confirm the issue or pull request remains open; post or edit from the source file or JSON input.
5. Fetch the published comment with `body_html`; require exact source/body equality and repeat the display, heading, and
   representative-formula checks.
6. Delete temporary drafts and responses; confirm the workflow added no repository files.

Unresolved delimiter, macro, rendering, target-state, or posted-body verification blocks publication.
