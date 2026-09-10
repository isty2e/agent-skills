# Model Starting Points

Model catalog evidence last checked 2026-09-08; read-only routing revised 2026-09-11. Apply these conditional starts
under the skill's settings precedence and budget. Other approved models remain eligible; this is not a latest catalog.

## Representative Candidates

The read-only assignments below are workflow hypotheses using vendor-documented model identities/effort, not measured
quality parity or savings. Treat providers independently, not as equivalent tiers. IDs are examples, not portable launch
arguments. These entries authorize neither writing nor implementation: that requires the user's explicit request for
the task or scope under [the skill boundary](../SKILL.md#1-find-a-candidate-and-decide).

Stronger models may be initial choices; no cheaper-first sequence is required. Compare moderate effort on a stronger
model, deeper effort on a cheaper model, and direct parent execution, including expected checking/repair. Same-model
capability alone does not justify a child; identify its concrete delegation benefit.

### OpenAI

- **GPT-5.6 Luna** (`gpt-5.6-luna`): routine extraction, lookup, or specified checks. Trial `low` for mechanical work;
  `medium` for bounded tracing or source/version interpretation, as in the guide's documentation example. Do not extend
  this start to difficult synthesis merely because no files are edited; compare `high` or a stronger model if needed.
- **GPT-5.6 Terra** (`gpt-5.6-terra`): broader read-heavy scans and multi-file/source investigation. Trial `medium` for
  exploration; `high` for causal paths, conflicting evidence, or assumption checking. These are trial combinations.
- **GPT-5.6 Sol** (`gpt-5.6-sol`): demanding bounded diagnosis or adversarial review. Trial `high`; compare a stronger
  moderate-effort option and direct parent work without first exhausting cheaper attempts. The model page identifies
  the guide's `gpt-5.6` as a Sol alias.
- **GPT-6 Astra** (`gpt-6-astra`): difficult read-only diagnosis, cross-contract review, or scientific/mathematical
  reasoning with costly errors. Trial `high`; compare `medium` under unchanged acceptance. If Astra is already the
  parent, require a separate delegation benefit such as useful parallel investigation or context isolation.

Sources: [OpenAI subagent guide](https://learn.chatgpt.com/docs/agent-configuration/subagents),
[Sol identity](https://developers.openai.com/api/docs/models/gpt-5.6-sol),
[Astra capabilities and effort](https://developers.openai.com/api/docs/models/gpt-6-astra).

### Anthropic

- **Claude Haiku 4.5** (`claude-haiku-4-5-20251001`): simple extraction and short, bounded tasks. The cited docs do not
  support a native `effort` parameter for Haiku. Preserve supported local thinking configuration; invent no mapping.
- **Claude Sonnet 5** (`claude-sonnet-5`): bounded source investigation, semantic synthesis, or focused review. Trial
  `medium` for moderate reasoning; use the documented `high` default for complex paths or conflicting evidence. Keep
  acceptance unchanged when comparing effort.
- **Claude Opus 5** (`claude-opus-5`): difficult bounded diagnosis, hypothesis checking, or adversarial review. Start
  at the documented `high` default; compare `medium` where verification supports it. Failure does not mandate maximum
  effort; diagnose missing evidence, task scope, and capability first.
- **Claude Fable 5.1** (`claude-fable-5-1`): complex read-only research, source synthesis, or domain reasoning with a
  clear question. Start at `high`; compare `medium`/`low` only where quality holds. Confirm native effort support for the
  deployed version; keep Fable 5 observations separate. Reserve `xhigh`/`max` for justified, budgeted needs.

Sources: [Claude model roles](https://code.claude.com/docs/en/model-config),
[model IDs](https://platform.claude.com/docs/en/about-claude/models/overview),
[model-specific effort](https://platform.claude.com/docs/en/build-with-claude/effort),
[Fable 5.1 identity and scope](https://platform.claude.com/docs/en/release-notes/overview#september-1-2026).

The read-only policy is a conservative operating choice, not proof that implementation delegation always loses money
or that read-only work always saves it. Explicitly requested implementation needs a separate scope/verification and
model/effort decision; these reading-task starts do not automatically apply. Local trials remain allowed within the
read-only boundary; hard tasks need not fail on Luna medium before another profile is considered.

## Resolve And Refresh

- Before first use: check host availability, permissions, effort/thinking support, and budget. Resolve deployment
  aliases to exact identity/version where possible; record unresolved aliases honestly.
- Distinguish effort, thinking mode/token budget, service tier, and conversation context. Omit unsupported knobs;
  matching effort names imply neither equal compute nor equal quality.
- Material unresolved selection fact: check current primary documentation, not every launch. Recheck after relevant
  model/provider/alias/host/policy changes.
- Stale/unavailable/unaffordable entry: choose another evidenced authorized option or work directly. Do not silently
  switch providers, substitute newer models, or rewrite shared examples. Missing equivalents do not require catalog
  expansion.
- Keep working local profiles, including higher-effort inexpensive reviewers, as comparison candidates; do not replace
  them to match this list. Record selected entry/date or other selection basis. Promote useful results to scoped local
  hints under [tuning.md](tuning.md), never universal rankings.
