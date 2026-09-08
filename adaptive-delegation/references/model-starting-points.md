# Model Starting Points

Evidence checked 2026-09-08. Apply these conditional first-run candidates under the skill's settings precedence and
budget. Other approved models remain eligible.

## Representative Candidates

Vendor-documented roles/defaults; transfer to this workflow is a hypothesis, not measured quality parity or end-to-end
savings. Treat provider groups independently, never as capability-equivalent tiers. IDs are provider examples, not
portable launch arguments.

Stronger models may be initial choices; no cheaper-first sequence is required. Compare moderate effort on a stronger
model, deeper effort on a cheaper model, and direct parent execution, including expected checking/repair. Same-model
capability alone does not justify a child; identify its concrete delegation benefit.

### OpenAI

- **GPT-5.6 Luna** (`gpt-5.6-luna`): narrow extraction, specified tracing, or API/documentation checks. Start at
  `medium`; the official guide uses it for documentation and code-mapping agents. Trial `low` for straightforward,
  latency-sensitive work. Clear mechanical implementation remains a candidate only when decisions are settled and
  checking is cheap.
- **GPT-5.6 Terra** (`gpt-5.6-terra`): read-heavy scans, broader exploration, and supporting documents. Trial `medium`;
  use `high` for complex path/assumption checking. The task fit follows the guide.
- **GPT-5.6 Sol** (`gpt-5.6-sol`): demanding bounded reasoning or review. Trial `high`; compare with keeping the work in
  the parent. The guide names `gpt-5.6`, which the model page identifies as a Sol alias.
- **GPT-6 Astra** (`gpt-6-astra`): difficult bounded diagnosis, cross-contract implementation/review, or independent
  verification with costly errors. Trial `high` for these judgment-heavy tasks; compare `medium` under unchanged
  acceptance. The model page documents complex reasoning/coding/research and supports both levels.

Sources: [OpenAI subagent guide](https://learn.chatgpt.com/docs/agent-configuration/subagents),
[Sol identity](https://developers.openai.com/api/docs/models/gpt-5.6-sol),
[Astra capabilities and effort](https://developers.openai.com/api/docs/models/gpt-6-astra).

### Anthropic

- **Claude Haiku 4.5** (`claude-haiku-4-5-20251001`): simple extraction and short, bounded tasks. The cited docs do not
  support a native `effort` parameter for Haiku. Preserve supported local thinking configuration; invent no mapping.
- **Claude Sonnet 5** (`claude-sonnet-5`): bounded coding and routine implementation with settled contracts. Start at
  the documented `high` default; trial `medium` as a cost-saving alternative under unchanged acceptance criteria.
- **Claude Opus 5** (`claude-opus-5`): difficult bounded reasoning or implementation. Start at the documented `high`
  default; use deeper effort only for a justified task, not automatic escalation after any failure.
- **Claude Fable 5.1** (`claude-fable-5-1`): complex agentic coding, research, or knowledge work with a clear delegation
  boundary. Start at the documented `high`; trial `medium`/`low` with quality evaluated under unchanged acceptance.
  Reserve `xhigh`/`max` for justified, budgeted needs. Keep existing Fable 5 settings/observations version-specific.

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
