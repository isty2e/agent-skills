---
name: github-math-comment
description: Draft, validate, publish, or edit GitHub issue and pull request comments containing TeX. Use when display math must survive GFM parsing and the posted body and rendered structure need verification.
license: MIT
---

# GitHub Math Comment

Keep the source body in a temporary Markdown file outside the repository. Send it through a body-file or JSON input, not
expanding shell quoting.

## Draft Safely

- Use fenced `math` blocks for display equations. In a `$$` block, a line containing only `=` can become a Setext
  heading before math rendering and split the equation.
- Check balanced math fences and inline delimiters. Do not compare raw `\left` and `\right` substring counts because
  commands such as `\rightsquigarrow` produce false matches.
- Treat macro support as target-context behavior. An HTML math wrapper alone does not prove that the client renderer
  accepts every macro. When `\operatorname` is not verified, use `\mathrm` where its semantics fit or another
  target-verified equivalent.
- When the comment contains scholarly references, apply `scholarly-reference-integrity` separately; this skill does not
  verify citations.

## Verify And Publish

1. Render the complete source through GitHub's Markdown API in GFM mode with the target repository as context.
2. Require one rendered display-math node per fenced `math` block and rendered heading counts matching the intended
   source headings. GitHub currently marks display nodes with `js-display-math`; inspect current output rather than
   assuming the selector is permanent.
3. Inspect representative formulas inside math-renderer nodes. When macro behavior matters, also use the GitHub UI
   preview or another check that exercises the client renderer; a nonzero wrapper count is insufficient.
4. Confirm the issue or pull request is still open, then post or edit using the source file or JSON input.
5. Fetch the published comment including `body_html`. Require the returned body to match the source exactly and repeat
   the display-math, heading, and representative-formula checks.
6. Remove temporary drafts and responses and confirm the workflow introduced no repository files.

Do not publish when delimiter, macro, rendered-structure, target-state, or posted-body verification is unresolved.
