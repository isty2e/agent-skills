## Durable knowledge

A shared Agent Skill named `durable-knowledge` is available to Codex, Pi, and other compatible
agents. Use the same skill package and vault policy in every harness.

During substantive work, consider invoking the skill only after the primary task has produced a
clear durable mechanism, scoped invariant or constraint, reusable method, conditional decision rule,
important distinction, or cross-source synthesis. Zero agent-initiated captures is normal. Candidate
creation has no numeric quota, but every candidate must independently satisfy the full admission
policy.

Do not capture repository-local implementation trivia, transient status, ordinary bug reports, raw
chat summaries, generic advice, or facts cheaply recoverable from code. Project-specific semantic
invariants normally belong in repository architecture documentation. A local observation may become
only a provisional candidate unless its scope, rationale, evidence, and invalidation conditions are
explicit. Make that evidence self-contained in the record or reference it through a synced-vault ID
or stable external URI. Never use a local path, bare filename, local ticket or issue name, session ID,
or machine-scoped artifact label as claim support.

For every new candidate, paper, canonical, or proposal record, use `title` as the concise
human-readable label and mirror it exactly in the first H1. Keep machine identity in `id`; never
derive a new ID from a title change.

When the user explicitly asks to remember or save something, first identify the context that owns
its meaning. Route user preferences and other user-, session-, repository-, project-, organization-,
or machine-bound facts to native memory or owner-specific documentation. Invoke this skill only for
origin-independent propositions, preserving honest scope and evidence state. When a task materially
overlaps prior research or a known design mechanism, consider a bounded read-only recall before
redoing expensive work.

Never let background capture interrupt the primary task. Background capture creates only `pending`
candidates and must never set `ready` or mutate canonical knowledge. Curate only `ready` candidates.
When a user explicitly names a non-applied candidate and requests integration, record that selection
by setting it to `ready` in the same operation before canonical curation.
