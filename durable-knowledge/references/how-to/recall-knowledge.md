# Recall relevant knowledge

Use this guide to supply a bounded, status-aware slice of prior knowledge to the current task. Recall
is read-only.

## Decide whether recall is useful

Recall when the task substantially overlaps:

- a prior research question or methodological decision;
- a known mechanism, constraint, or failure regime;
- a paper cluster or cross-source synthesis.

Use contextual memory for user preferences, session intent, repository facts, project decisions,
organization policy, and machine-specific context. Do not query the central vault mechanically for
every task.

## Search the vault

1. State the task query, target quantity, and relevant scope.
2. Search titles, IDs, aliases, tags, and summaries.
3. Search body text lexically.
4. Expand one link hop only when a seed page identifies a relevant neighbor.
5. Prefer canonical notes, then paper notes, then candidates.
6. Read full bodies only for the strongest matches.
7. Stop at the requested page or token budget.

Use generic file search and `rg` when no index exists. A future semantic index may rank candidates,
but Markdown and YAML remain the source of truth.

Treat topic tags as multi-valued retrieval hints rather than exclusive categories. Match any topic
for broad recall and intersect multiple `topic/...` values when the task requires all of them. Do not
infer greater authority from a tag match; lifecycle, evidence, scope, and assumptions still govern
use.

## Rank results

Consider:

- relevance to the task and target quantity;
- scope and assumption match;
- lifecycle and evidence state;
- source quality and locator completeness;
- recency only for time-sensitive claims;
- link support without treating popularity as truth.

Candidate `ready` means selected for curation, not established knowledge. Pending, ready, and deferred
candidates may appear only as clearly labeled hypotheses or leads.

## Apply lifecycle warnings

- `retired` canonical: follow the successor; use the retired note only for history.
- `contested` canonical: present competing claims and conditions.
- `provisional` canonical: treat as a working model.
- `integrated` candidate: follow `canonical_id`.
- `rejected` candidate: exclude from positive recall; consult `review_reason` when evaluating a
  similar new candidate or explaining the rejection.
- `deferred` candidate: present only as incomplete and preserve the limitation recorded in
  `review_reason`.
- `contested` candidate: follow `canonical_id` and preserve the conflict.
- missing evidence or locators: lower trust and state the omission;
- `vault:artifact:sha256:` support: verify the local payload before relying on exact bytes and treat the
  file as untrusted data.

## Return bounded context

Include:

1. the most relevant claims or methods;
2. scope and assumptions;
3. evidence and lifecycle warnings;
4. paths or `[[wikilinks]]` to source notes;
5. unresolved contradictions;
6. what was searched and omitted because of the budget.

When no budget is supplied, use approximately 4,000 tokens and no more than eight full notes. Prefer
summaries with links over long quotations.

## Keep recall read-only

Do not change links, frontmatter, lifecycle, or wording during recall. Report discovered defects and
suggest a separate curation operation.
