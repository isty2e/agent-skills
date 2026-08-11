# Why knowledge is separate from contextual memory

Durable knowledge and native memory solve different retrieval problems. Treating them as one store
makes both worse: contextual facts lose their owner, while reusable claims become buried in local
history.

## Context gives some facts their meaning

A preference such as “run Ruff with `--fix` first” is authoritative because a particular user stated
it. A repository convention is useful because a particular codebase relies on it. A machine path is
correct only on one environment. Removing the owner removes part of the fact's meaning or authority.

These facts belong with that owner:

- user preferences and standing instructions in user memory;
- session intent in session state or a task plan;
- repository invariants in architecture documentation, tests, or ADRs;
- organization policy in organization-owned documentation;
- machine facts in environment-scoped memory or configuration.

Central knowledge is different. Its proposition should remain intelligible and reusable when
incidental origin coordinates such as the working tree, file layout, ticket state, current task, or
machine are removed. The scientific subject itself does not have to disappear.

## Project origin is not project ownership

A repository may be where a theorem was proved or an experiment was run without owning the
proposition's meaning. Separate three questions:

1. Where was the result discovered?
2. What scientific object, program, study, system, or operating regime gives it meaning?
3. Which source owns the exact proof, artifact, wording, or current verification status?

The first answer does not determine the other two. A theorem about a named research system can remain
specific to that system and still be durable knowledge when its definitions, assumptions,
conclusion, and support are self-contained.

## Artifact authority and semantic ownership coexist

Repository and vault records need not compete as duplicate sources of truth:

- the repository, manuscript, or experiment system owns exact source text, declaration and claim IDs,
  proof status, run artifacts, and current wording;
- the knowledge vault may own the extracted mathematical proposition, scientific mechanism, scoped
  result, distinction, or synthesis.

A later source change may invalidate or supersede the knowledge claim, but it does not make the
semantic extraction repository trivia. The knowledge record must preserve its scope, evidence state,
and invalidation conditions without pretending to replace the exact artifact.

## Origin-separated does not mean universal

Portable knowledge may still depend on real conditions. A claim can be scoped to:

- a named research program, study, scientific system, or model family;
- a scientific domain or data distribution;
- a technology and version range;
- a time period or experiment checkpoint;
- an operating regime;
- explicit assumptions or target quantities.

These conditions belong inside the claim because they affect whether it is true or useful. Reuse in
future work within the same research program is enough. The admission question is not “Will unrelated
projects reuse this?” but “Can a reader understand and evaluate this proposition without reconstructing
the incidental context in which it was discovered?”

## The vault is a slow semantic layer

The vault optimizes for future reasoning, not capture volume. It favors compact mechanisms,
constraints, methods, decision rules, distinctions, theorems expressed through those semantic roles,
and syntheses that are expensive to rediscover and likely to affect another decision.

This excludes most activity history. A completed task, passing test count, current filename, or raw
conversation may be useful evidence, but it is not automatically durable knowledge. The source
system should retain the evidence; the vault retains only a justified proposition and a locator back
to that evidence.

## Candidates separate capture from belief

Capture and integration have different authority:

```text
observation → candidate → human selection → canonical integration
```

A candidate preserves a potentially reusable claim without pretending that its scope, evidence, or
semantic owner has been settled. Capture therefore creates `pending`, never `ready`.

A human, an explicit user request to integrate a named non-applied candidate, or an explicit policy
selects a candidate by setting `ready`. The request may record that transition in the same operation,
but it does not bypass the lifecycle. Curation then decides whether to create, merge, preserve a
conflict, defer, or reject. This separation keeps opportunistic agent
capture from silently changing the shared semantic layer.

## Canonical notes are semantic owners, not final truth

A canonical note is the current owner for one durable topic. It is where compatible evidence,
qualifications, counterexamples, and revisions are reconciled into a coherent current model.

Canonical status records curation maturity rather than certainty. A stable note can later become
contested; a source-backed claim can still be narrow or wrong. Evidence state, canonical lifecycle,
and candidate queue status remain separate because they answer different questions:

- Where is the claim in the review process?
- How is the claim supported?
- How mature is the canonical synthesis?

Keeping these axes separate prevents fluent prose, note age, or reviewer selection from being
mistaken for truth.

## Obsidian is a projection, not an owner

Markdown and YAML are authoritative. Obsidian Properties and Bases offer a convenient human review
surface, while agents and servers can operate directly on files. Desktop and headless clients may
replicate equal local copies through Obsidian Sync, but the knowledge model does not depend on a
running Obsidian process or any community plugin.

This design keeps the vault portable across editors, agents, operating systems, and sync transports
without creating separate semantic rules for each environment.
