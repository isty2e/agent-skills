# Model Starting Points

Catalog evidence checked 2026-09-08; routing revised 2026-09-19 from maintainer-reviewed observations. These conditional
starts combine vendor guidance and operator experience, not matched benchmarks, verified semantic parity, or savings.
Task mix, review procedure, and parent checking differ; effective-model/cost evidence is incomplete. Other approved
models remain eligible; this is not a current catalog or a ranking of equivalent provider tiers.

Apply [the skill's selection criteria](../SKILL.md#1-find-a-candidate-and-decide), settings precedence, and budget. IDs
are examples, not portable launch arguments. Stronger models may be first: compare moderate effort on a stronger model,
deeper effort on a cheaper model, and direct work, including parent checking/repair. Same-model capability alone is no
delegation benefit. Already-verified follow-ups usually belong with the parent/tools unless review addresses uncertainty.

## Representative Candidates

### OpenAI

- **GPT-5.6 Luna** (`gpt-5.6-luna`):
  - `medium`: narrow lookup/extraction, bounded tracing, specified checks; `low` remains a mechanical-work trial.
    Substantial multi-source interpretation is not routine lookup: compare `high` or Terra.
  - `high`: selecting/summarizing substantial existing material. Allow for local formatting/metadata repair; observed
    usefulness does not establish fully verified semantic accuracy.
  - `xhigh`: bounded deep review with a meaningful unresolved question; parent scope/severity checks remain necessary.
    Useful contributions may coexist with workflow failures. No demonstrated advantage makes `max` the default.
- **GPT-5.6 Terra** (`gpt-5.6-terra`): `high` for multi-file causal paths, persisted-state contracts, cross-service
  investigation; trial `medium` for broad shallow scans. Requested-profile observations do not establish effective-model
  identity or cost.
- **GPT-5.6 Sol** (`gpt-5.6-sol`): trial `high` for demanding bounded diagnosis; outcome evidence is limited. Launch or
  acceptance failures do not prove model weakness. Compare stronger moderate-effort options and direct work. The guide's
  `gpt-5.6` is a Sol alias.
- **GPT-6 Astra** (`gpt-6-astra`): difficult read-only diagnosis, cross-contract review, scientific/mathematical reasoning
  with costly errors. Trial `high`; compare `medium` under unchanged acceptance. If already the parent, require a separate
  benefit such as parallel investigation or context isolation.

Sources: [OpenAI subagent guide](https://learn.chatgpt.com/docs/agent-configuration/subagents),
[Sol identity](https://developers.openai.com/api/docs/models/gpt-5.6-sol),
[Astra capabilities and effort](https://developers.openai.com/api/docs/models/gpt-6-astra).

### Anthropic

- **Claude Haiku 4.5** (`claude-haiku-4-5-20251001`): simple extraction/short bounded tasks. Cited docs do not support
  native `effort`; preserve supported local thinking settings without inventing a mapping.
- **Claude Sonnet 5** (`claude-sonnet-5`): bounded source investigation, semantic synthesis, focused review. Trial `medium`
  for moderate reasoning; documented `high` default for complex paths/conflicting evidence. Compare without weakening acceptance.
- **Claude Opus 5** (`claude-opus-5`): difficult bounded diagnosis, hypothesis checks, adversarial review. Start at the
  documented `high` default; compare `medium` where verification supports it. Diagnose evidence, scope, and capability
  before treating failure as a reason for maximum effort.
- **Claude Fable 5.1** (`claude-fable-5-1`): complex read-only research, source synthesis, domain reasoning with a clear
  question. Start `high`; compare `medium`/`low` only where quality holds. Verify deployed-version effort support; keep
  Fable 5 observations separate. Reserve `xhigh`/`max` for justified, budgeted needs.

Sources: [Claude model roles](https://code.claude.com/docs/en/model-config),
[model IDs](https://platform.claude.com/docs/en/about-claude/models/overview),
[model-specific effort](https://platform.claude.com/docs/en/build-with-claude/effort),
[Fable 5.1 identity and scope](https://platform.claude.com/docs/en/release-notes/overview#september-1-2026).

## Resolve And Refresh

- Before first use, check host availability, permissions, effort/thinking support, and budget. Resolve exact identity/version
  behind deployment aliases where possible; record unresolved aliases honestly.
- Effort, thinking mode/token budget, service tier, and conversation context are distinct. Omit unsupported knobs;
  matching effort labels establish neither equal compute nor quality.
- Check current primary docs for material unresolved selection facts, not every launch. Recheck after relevant
  model/provider/alias/host/policy changes.
- Stale, unavailable, or unaffordable entry: choose an evidenced authorized alternative or direct work. Do not silently
  switch providers, substitute newer models, rewrite shared examples, or expand the catalog merely to fill a gap.
- Preserve working local profiles—including higher-effort inexpensive reviewers—as comparison candidates. Record the
  selected entry/date or other basis. Use [tuning.md](tuning.md) for scoped local hints, not universal rankings.
