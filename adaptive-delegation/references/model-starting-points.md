# Model Starting Points

Model catalog evidence last checked 2026-09-08; routing revised 2026-09-19 from maintainer-reviewed task observations.
Apply these conditional defaults under the skill's settings precedence and budget. Other approved models remain
eligible; this is not a latest catalog.

## Representative Candidates

These task-specific starts combine vendor guidance and operator observations, not matched benchmarks or measured
savings. Task mix, review procedure, and parent checking differ between profiles. Treat providers independently, not as
equivalent tiers. IDs are examples, not portable launch arguments. Apply
[the skill's selection criteria](../SKILL.md#1-find-a-candidate-and-decide) before choosing a profile.

Stronger models may be initial choices; no cheaper-first sequence is required. Compare moderate effort on a stronger
model, deeper effort on a cheaper model, and direct parent execution, including expected checking/repair. Same-model
capability alone does not justify a child; identify its concrete delegation benefit.

### OpenAI

- **GPT-5.6 Luna** (`gpt-5.6-luna`):
  - `medium`: narrow lookup, extraction, bounded tracing, or specified checks. `low` remains a mechanical-work trial.
    Current multi-source synthesis is not routine lookup; compare `high` or Terra when substantial interpretation is
    needed.
  - `high`: start here for selecting and summarizing substantial existing material. Observed usefulness included local
    formatting/metadata repair, not fully verified semantic accuracy.
  - `xhigh`: start here for bounded deep review with a meaningful unresolved question. Useful review contributions
    survived poor whole-workflow outcomes; parent scope/severity checks still mattered. No demonstrated advantage
    justifies promoting `max` to the default.
- **GPT-5.6 Terra** (`gpt-5.6-terra`): start at `high` for multi-file causal paths, persisted-state contracts, or
  cross-service investigation; trial `medium` for broader shallow scans. Useful requested-profile observations support
  this candidate, but effective-model and cost evidence are incomplete.
- **GPT-5.6 Sol** (`gpt-5.6-sol`): retain `high` as a trial for demanding bounded diagnosis. Usable outcome evidence is
  limited; launch and acceptance failures do not establish model weakness. Compare stronger moderate-effort options and
  direct work. The model page identifies the guide's `gpt-5.6` as a Sol alias.
- **GPT-6 Astra** (`gpt-6-astra`): difficult read-only diagnosis, cross-contract review, or scientific/mathematical
  reasoning with costly errors. Trial `high`; compare `medium` under unchanged acceptance. If Astra is already the
  parent, require a separate delegation benefit such as useful parallel investigation or context isolation.

For already-verified follow-ups, prefer direct parent/tool work unless another review addresses remaining uncertainty.

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
