# Understanding knowledge routing through examples

The difficult part of capture is often not wording the claim but identifying its owner. These
examples show how origin, scope, and reuse determine the destination.

## Contents

- [Repository-local implementation trivia](#repository-local-implementation-trivia)
- [Project semantic invariant](#project-semantic-invariant)
- [Durable recovery mechanism](#durable-recovery-mechanism)
- [Local experiment becoming a hypothesis](#local-experiment-becoming-a-hypothesis)
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

That abstraction still needs evidence across contexts, a mechanism, scope, and invalidation
conditions. Removing repository names is not enough to establish portability.

## Durable recovery mechanism

```text
In crash-recoverable workflows whose external side effects are not transactionally coupled to local
state, durable intent must precede externally visible mutation; otherwise recovery cannot distinguish
“not applied” from “applied but not recorded.”
```

This is a plausible central candidate because the mechanism survives the originating implementation.
Its scope must retain exceptions such as idempotent effects, authoritative external ledgers, or an
atomic cross-domain commit.

## Local experiment becoming a hypothesis

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

This remains an observed hypothesis until stronger evidence supports broader promotion.

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

Use the [admission policy](../reference/admission-policy.md) for the normative gate and the
[capture guide](../how-to/capture-knowledge.md) for the procedure.
