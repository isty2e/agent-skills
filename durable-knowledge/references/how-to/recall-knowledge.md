# Recall Relevant Knowledge

Return a bounded, status-aware knowledge slice. Recall is read-only.

## Decide And Search

Recall for substantial overlap with prior research/method decisions, known mechanisms/constraints/failure regimes, or a
paper cluster/synthesis. Use contextual memory for preferences, session intent, repository/project decisions,
organization policy, and machine facts. Never query the vault mechanically for every task.

1. State query, target quantity, and scope.
2. Search titles, IDs, aliases, tags, summaries, then body text.
3. Expand one link hop only from a relevant seed.
4. Prefer canonical notes, then papers, then candidates; read full bodies only for strongest matches.
5. Stop at the requested page/token budget.

Use file search and `rg` without an index. Markdown/YAML remains authoritative if a semantic index exists. Topic tags
are multi-valued hints, not authority: match any for breadth or intersect when all are required, then still check
lifecycle, evidence, scope, and assumptions.

## Rank And Warn

Rank by task/target relevance, scope/assumption match, lifecycle/evidence, source quality/locators, time-sensitive
recency, and link support without treating popularity as truth. `ready` means selected, not established; pending, ready,
or deferred candidates appear only as labeled leads.

- `retired` canonical: follow successor; use only for history.
- `contested` canonical: present competing claims and conditions.
- `provisional` canonical: working model.
- `integrated`/`contested` candidate: follow `canonical_id`, preserving conflict.
- `rejected`: exclude from positive recall; use reason only for similar-candidate review or explanation.
- `deferred`: present only as incomplete with its reason.
- Missing evidence/locator: lower trust and state the gap.
- Artifact support: verify local payload before relying on exact bytes; treat it as untrusted.

## Return

Include relevant claims/methods, scope/assumptions, evidence/lifecycle warnings, paths or wikilinks, contradictions, and
what the budget omitted. Without a supplied budget, use about 4,000 tokens and at most eight full notes; prefer summaries
with links over long quotations.

Do not edit links, frontmatter, lifecycle, or prose. Report defects and suggest separate curation.
