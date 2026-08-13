# Why Knowledge Is Separate From Contextual Memory

Durable knowledge and native memory solve different retrieval problems. Combining them strips contextual facts of
their owner and buries reusable claims in local history.

## Context Owns Contextual Facts

A user preference is authoritative because that user stated it; a repository convention because that codebase relies
on it; a machine path only within one environment. Keep these facts with their owners:

- user preferences and standing instructions in user memory;
- session intent in session state or a task plan;
- repository invariants in tests, ADRs, or architecture docs;
- organization policy in organization-owned docs;
- machine facts in environment-scoped memory or configuration.

Durable propositions remain intelligible after incidental coordinates such as working tree, file layout, ticket,
current task, and machine disappear. Semantically essential scientific scope remains.

## Origin Does Not Determine Ownership

Ask separately:

1. Where was the result discovered?
2. What program, study, system, domain, or regime gives it meaning?
3. What source owns its exact proof, artifact, wording, or current status?

A repository can host a theorem proof or experiment without owning the proposition's meaning. The repository,
manuscript, or experiment system owns exact declarations, IDs, artifacts, wording, and status; the vault may own the
self-contained theorem, mechanism, scoped result, distinction, or synthesis. Preserve scope, evidence state, and
invalidation conditions without pretending the extraction replaces its source.

Portable does not mean universal. Keep real conditions such as named program, system, model family, distribution,
version, period, checkpoint, regime, assumptions, and target quantity. Reuse within the same research program is
enough. Ask whether a reader can evaluate the proposition without reconstructing incidental discovery context, not
whether unrelated projects will reuse it.

## The Vault Is A Slow Semantic Layer

Optimize for future reasoning, not capture volume. Retain expensive-to-rediscover mechanisms, constraints, methods,
decision rules, distinctions, theorems, and syntheses likely to change a future decision. Task completion, test counts,
filenames, and raw conversation may be evidence but are not automatically knowledge; their source owns the evidence,
while the vault stores a justified proposition and a portable locator.

## Candidates Separate Capture From Belief

```text
observation -> pending candidate -> selection -> canonical integration
```

Capture creates `pending`, an editable draft of one proposition, without claiming settled scope, support, or ownership.
A human, explicit integration request, or policy selects one exact revision as `ready`. That revision freezes until
returned to `pending`, revised, validated, and selected again. Curation then creates, merges, preserves conflict,
defers, or rejects. This prevents opportunistic capture from silently changing shared knowledge.

## Canonical Does Not Mean Final Truth

A canonical note is the current semantic owner for one topic, reconciling evidence, qualifications, counterexamples,
and revisions. Its lifecycle records curation maturity, not certainty. Keep queue status, evidence state, and canonical
lifecycle separate: they respectively answer where a claim is in review, how it is supported, and how mature the
synthesis is.

## Obsidian Is A Projection

Markdown and YAML are authoritative. Obsidian Properties, Bases, plugins, and sync clients provide review and transport
surfaces without owning semantics. Agents and servers may operate directly on replicated files; no knowledge operation
depends on a running Obsidian process.
