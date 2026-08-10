## Durable knowledge

A shared Agent Skill named `durable-knowledge` is available to Codex, Pi, and other compatible
agents. Use the same skill package and vault policy in every harness.

At natural decision points during substantive work, consider invoking the skill without waiting for
an explicit request. Before redoing expensive research or reasoning, use bounded read-only recall
when the task materially overlaps prior research or a known design mechanism. After the primary task
has produced a clear durable mechanism, scoped invariant or constraint, reusable method, conditional
decision rule, important distinction, or cross-source synthesis, consider selective capture. Zero
retrieved records and zero agent-initiated captures are normal. Candidate creation has no numeric
quota, but every candidate must independently satisfy the full admission policy.

These are relevance-triggered reminders, not completion gates. Do not delay or block the primary
task, report no-op checks, or create weak candidates merely to demonstrate that the skill was
considered.

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
origin-independent propositions, preserving honest scope and evidence state.

Never let background capture interrupt the primary task. Background capture creates only `pending`
candidates and must never set `ready` or mutate canonical knowledge. Curate only `ready` candidates.
When a user explicitly names a non-applied candidate and requests integration, record that selection
by setting it to `ready` in the same operation before canonical curation.
