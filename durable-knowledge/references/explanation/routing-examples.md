# Understanding knowledge routing through examples

The difficult part of capture is often not wording the claim but identifying its owner. These
examples show how origin, scope, and reuse determine the destination.

## Contents

- [Repository-local implementation trivia](#repository-local-implementation-trivia)
- [Project semantic invariant](#project-semantic-invariant)
- [Project-originated theorem](#project-originated-theorem)
- [Scoped negative result](#scoped-negative-result)
- [Repository proof status](#repository-proof-status)
- [Scientific synthesis from one project](#scientific-synthesis-from-one-project)
- [Durable recovery mechanism](#durable-recovery-mechanism)
- [Local experiment motivating a hypothesis](#local-experiment-motivating-a-hypothesis)
- [Paper-specific result](#paper-specific-result)
- [User preference](#user-preference)
- [Version-scoped portable knowledge](#version-scoped-portable-knowledge)
- [Apparent contradiction caused by scope](#apparent-contradiction-caused-by-scope)
- [Genuine conflict](#genuine-conflict)

## Repository-local implementation trivia

Observation:

```text
Moving foo.go under package render creates an import cycle in this repository.
```

This belongs in code, a test, an issue, or repository architecture documentation. The fact is tied to
the current import graph, likely to change after refactoring, and cheap to rediscover.

## Project semantic invariant

Claim:

```text
The planner must derive decisions from canonical desired state rather than presentation-oriented
projections.
```

The repository owns this invariant because its architecture relies on it. A central abstraction may
be possible:

```text
Decision layers should consume canonical semantic representations rather than partial observations
or presentation projections, unless currentness is explicitly part of the decision semantics.
```

That abstraction still needs a mechanism, scope, and invalidation conditions. Removing repository
names is not enough to establish semantic value.

## Project-originated theorem

A repository contains a machine-checked closure factorization theorem. The exact Lean declaration,
imports, proof term, claim ID, and current verification status belong to the repository. The
mathematical proposition may still become a central candidate when the note preserves:

- definitions of the closure and factorization objects;
- complete assumptions and quantified domains;
- the theorem conclusion and mathematical significance;
- a proof capsule or complete formal derivation;
- verification conditions and invalidation criteria.

The theorem does not need a second project or external publication before capture. Its discovery
location is not its semantic owner.

## Scoped negative result

Observation:

```text
A witness activated zero times across 4,096 evaluated routing decisions at checkpoint C under
protocol P.
```

This can become an `observed` candidate when the denominator, checkpoint, protocol, data regime,
witness definition, and decision relevance are preserved. It supports a scoped negative result such
as “no activations were observed under these conditions”; it does not prove that activation is
impossible. If the count is merely the latest run status with no durable scientific consequence, the
experiment log remains its owner.

## Repository proof status

```text
The current Lean tree has 127 passing files.
```

This is repository status. It changes with the tree, is cheaply recomputed, and does not state a
mathematical proposition. Keep it in CI, a project report, or the theorem inventory rather than the
knowledge vault.

## Scientific synthesis from one project

Several proved project results jointly show that a routing guarantee decomposes into selection,
branch-validity, and fallback obligations. A synthesis relating those propositions may be central
knowledge even if every proof currently lives in one repository. The repository owns the exact proof
artifacts; the vault owns the self-contained scientific relation and its documented scope.

## Durable recovery mechanism

```text
In crash-recoverable workflows whose external side effects are not transactionally coupled to local
state, durable intent must precede externally visible mutation; otherwise recovery cannot distinguish
“not applied” from “applied but not recorded.”
```

This is a plausible central candidate because the mechanism survives the originating implementation.
Its scope must retain exceptions such as idempotent effects, authoritative external ledgers, or an
atomic cross-domain commit.

## Local experiment motivating a hypothesis

Observation:

```text
A flexible PIT adapter was unstable with a very small residual calibration set.
```

The universal statement “PIT adapters do not work for small datasets” erases the experiment's model,
sample regime, and alternatives. A better candidate is:

```text
Flexible monotone post-hoc calibrators can become variance-limited in small residual samples;
low-dimensional recenter-and-scale models may be preferable until sample size supports the additional
capacity.
```

This is a `hypothesis` because the explanatory proposition remains genuinely unproved, not because
the record is young or provisional. `observed` describes its current evidence; candidate status and
canonical lifecycle describe review and maturity. Additional evidence may change support or justify
integration without changing `knowledge_kind` unless the proposition's semantic role changes.

## Paper-specific result

```text
Paper A improves metric X on benchmark Y under protocol Z.
```

The paper note owns this result. It becomes central only when it supports a reusable mechanism,
method, distinction, or cross-source synthesis.

## User preference

```text
Do not use scaffold split as the default evaluation split in my projects.
```

The user is the authority, so native user memory owns the statement. Central capture would wrongly
turn a personal instruction into a general methodological claim.

## Version-scoped portable knowledge

```text
Ruff versions supporting a particular safe fix can apply it through `ruff check --fix`; remaining
diagnostics still require review.
```

This may be central when the supported version range and fix-safety conditions are explicit. The
claim depends on Ruff's behavior, not on the identity of the user or repository where it was learned.

## Apparent contradiction caused by scope

```text
Method M is calibrated under exchangeability.
Method M fails under covariate shift.
```

These statements may describe different regimes. Compare assumptions, definitions, time, and target
quantity before declaring a conflict.

## Genuine conflict

When independent sources estimate the same target under compatible conditions and reach materially
incompatible conclusions, preserve both source-linked claims. Record likely methodological causes
and mark the canonical entry contested rather than choosing one by recency or fluency.

Use the [admission policy](../reference/admission-policy.md) for the normative gate, the
[research extraction guide](../how-to/capture-research-knowledge.md) for bounded scientific review,
and the [capture guide](../how-to/capture-knowledge.md) for record creation.
