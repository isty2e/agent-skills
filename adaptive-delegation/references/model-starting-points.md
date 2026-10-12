# Model Starting Points

These conditional starts combine linked provider guidance and scoped operator choices, not matched benchmarks, verified
semantic parity, or savings. Distinguish task roles, original quality, and parent repair rather than pooling model/effort
rates. Missing parent-cost measurements do not invalidate observed usefulness, but prevent measured-savings claims.
Keep model versions separate; old results do not establish a newer version's behavior. Other approved models remain
eligible; this is not a current catalog or a ranking of equivalent provider tiers.

Apply [the skill's selection criteria](../SKILL.md#1-find-a-candidate-and-decide), settings precedence, and budget. IDs
are examples, not portable launch arguments. Stronger models may be first: compare moderate effort on a stronger model,
deeper effort on a cheaper model, and direct work, including parent checking/repair. Same-model capability alone is no
delegation benefit. Already-verified follow-ups usually belong with the parent/tools unless review addresses uncertainty.

## Representative Candidates

### OpenAI

Choose by role before choosing effort:

| Task role | Starting candidate |
| --- | --- |
| Mechanical extraction or already verified facts | Tools/direct work first; a lower-effort child only when delegation helps |
| Bounded source, API, or version-support interpretation | Luna `high` |
| Reproduce specified calculations or check implementation outputs against a reference | Luna `xhigh`; retain `max` as a task-specific alternative |
| Trace calls, state changes, and producer/consumer contracts across components | GPT-6.1 Sol directly; no failed Luna trial required |
| Open review | The explicit reviewer profile takes precedence; otherwise use the review candidates below |

These are reversible starts, not automatic assignments. A short document or read-only scope does not make interpretation
mechanical. Reproduction checks and open review need different checks; favorable usefulness does not imply little repair.
The role-specific effort choices are operator starting hypotheses, not provider guarantees or a comparative benchmark.
Mixing task roles can change pooled usefulness rates without a model effect; retain explicit pins and recheck choices on
the next comparable task rather than promoting or demoting an effort level from that pool.

- **GPT-6 Luna** (`gpt-6-luna`):
  - `low`/`medium`: provider-guided trials for mechanical extraction or already specified facts where a child helps.
    Do not extend these to source/version interpretation merely because the input is short.
  - `high`: bounded source/API/version investigation or selecting substantial existing material. Check semantic accuracy
    separately from formatting or metadata repair.
  - `xhigh`: specified reproduction checks or bounded deep review with a meaningful unresolved question. Parent
    scope/severity checks remain necessary.
  - `max`: retain for a justified task or an already-approved reviewer profile. Do not demote it from a pooled rate mixing
    review, investigation, and reproduction checks, or promote it to every task from a few favorable checks. Allow
    sufficient resources for the approved scope; incomplete review is not approval evidence.
- **GPT-6.1 Sol** (`gpt-6.1-sol`): a starting candidate for multi-file causal paths, persisted-state contracts,
  cross-service investigation, and tracing how calls, state changes, and downstream consumers interact. Use an applicable
  approved profile or verify current host-supported effort/defaults. Model-only experience does not establish a preferred
  effort; do not transfer an older Sol version's `high` setting or results to 6.1. Older Sol versions are not starting or
  fallback candidates in this guidance; historical records remain historical evidence.
- **GPT-6 Astra** (`gpt-6-astra`): difficult read-only diagnosis, cross-contract review, scientific/mathematical reasoning
  with costly errors. Trial `high`; compare `medium` under unchanged acceptance. If already the parent, require a separate
  benefit such as parallel investigation or context isolation.

Sources: [OpenAI subagent guide](https://learn.chatgpt.com/docs/agent-configuration/subagents),
[Luna model](https://developers.openai.com/api/docs/models/gpt-6-luna),
[Sol model](https://developers.openai.com/api/docs/models/gpt-6.1-sol),
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

- Reuse a confirmed approved profile while its conditions remain applicable. Before using an unresolved profile or after
  material changes, check host availability, permissions, effort/thinking support, and budget. Resolve exact identity/version
  behind deployment aliases where possible; leave unresolved identity unknown in any requested measurements.
- Effort, thinking mode/token budget, service tier, and conversation context are distinct. Omit unsupported knobs;
  matching effort labels establish neither equal compute nor quality.
- Check current primary docs for material unresolved selection facts, not every launch. Recheck after relevant
  model/provider/alias/host/policy changes.
- Stale, unavailable, or unaffordable entry: choose an evidenced authorized alternative or direct work. Do not silently
  switch providers, substitute newer models, rewrite shared examples, or expand the catalog merely to fill a gap.
- Preserve working local profiles—including higher-effort inexpensive reviewers—as comparison candidates. Use
  [tuning.md](tuning.md) when revising scoped hints, not before every launch. Model changes do not activate statistics collection.
