# Research forward-evaluation baseline

This receipt records one clean-context behavioral evaluation. It is historical evidence for the
reviewed source revision, not a normative contract, deterministic unit test, or claim that every
model will behave identically.

## Run metadata

- **Time:** 2026-08-11T13:11:25Z
- **Source revision:** `c8175f37b13a8ff2e19d8bd3d43f99749492dbf0`
- **Harness:** Pi fresh-context subagent workflow
- **Model:** `openai-codex/gpt-5.6-sol`
- **Run ID:** `d1ade38d`
- **Operation:** read-only; no candidates or vault files were created
- **Reviewer:** parent-agent rubric review
- **Human review:** pending at receipt creation

The agent read `SKILL.md`, the research and generic capture guides, the admission policy, the record
model, the knowledge-boundary explanation, and the routing examples before reading the fixture.

## Prompt

```text
Find what should be preserved as knowledge from this research.
```

The evaluation instruction bounded the operation to the fixture below, required scientific content
before methodology, required existing `knowledge_kind`, lifecycle, and evidence-state values, and
required distinct treatment of a proved theorem with changing wording and a genuinely unproved
proposition.

## Fixture

### Proved theorem with wording still under revision

[Fixture](fixtures/research-forward/01-theorem.md) — SHA-256
`6b43c78932b7e2bd2735abb1bc4a5ad3dc28e8c4736490b70e51333000a7dd72`

### Scoped zero-occurrence result

[Fixture](fixtures/research-forward/02-experiment.md) — SHA-256
`1c19f43da96ee2a846b272d1177a3e2c0a0aa86f11d9617e589664a8554803f9`

### Genuinely unproved proposition

[Fixture](fixtures/research-forward/03-conjecture.md) — SHA-256
`dc51bbe049f85f8cca8411a0ec8e18c397b2156e14be68ed33577523716abefd`

### Project status and generic workflow advice

[Fixture](fixtures/research-forward/04-status-and-method.md) — SHA-256
`a281b75c3fc0fe5f324b65d677ae48ecb2a34ec09ffd1e869bcdcb10d914f771`

## Observed routing

- **Closure-factorization theorem:** `mechanism`, `pending`, `source-backed`; preserve with
  A1–A3 and its finite-routing scope.
- **Zero activations in 4,096 decisions:** `distinction`, `pending`, `observed`; preserve the
  scoped result and the boundary between finite non-observation and impossibility.
- **Unproved branch-safety proposition:** `hypothesis`, `pending`, `unverified`; preserve with
  M(delta), S(epsilon), and its falsification condition.

The agent explicitly distinguished the two theorem-maturity cases:

- the proved theorem retained `mechanism`; manuscript wording changes did not turn it into a
  `hypothesis`;
- the genuinely unproved proposition used `hypothesis` because no complete proof was known;
- the finite zero-occurrence result used `distinction`, not `constraint`, because its reusable role is
  the inferential boundary between non-observation and impossibility.

The agent routed these materials away from the vault proposition owner:

- exact Lean declaration, proof term, toolchain version, and source path → repository and proof
  system;
- raw experiment JSON, reproduction job, and replication plan → experiment owner;
- active proof sketch, failed lemmas, and issue identity → repository and issue tracker;
- file counts, pull-request status, manuscript schedule, and module rename → project owners;
- generic workflow advice → project or organization guidance rather than central scientific
  knowledge.

Substantive scientific propositions were reported before workflow methodology. The agent admitted no
independent methodology candidate from the generic advice.

## Verdict

**Pass by parent-agent rubric review.** No routing, ontology, maturity, scope, or ordering deviations
were observed for this fixture. Human review had not yet occurred when this receipt was written, so
no human-correction count is claimed.

## Limits

This receipt covers one model, one clean-context run, one bounded fixture, and read-only extraction.
It does not prove behavior for other models, automatic candidate creation, curation, or arbitrary
research corpora. Repeat the evaluation when research-routing policy changes or when a target model
shows materially different behavior.
