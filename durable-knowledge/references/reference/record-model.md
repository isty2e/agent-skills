# Record model reference

This document defines record types, controlled values, and lifecycle relationships. Templates under
`assets/templates/` define the full note bodies; `scripts/validate.py` enforces the managed
frontmatter subset defined by the vault contract.

## Contents

- [Record types](#record-types)
- [Knowledge kinds](#knowledge-kinds)
- [Candidate status](#candidate-status)
- [Evidence state](#evidence-state)
- [Canonical lifecycle](#canonical-lifecycle)
- [Candidate lifecycle relationships](#candidate-lifecycle-relationships)
- [Claim shape](#claim-shape)
- [Paper identity](#paper-identity)
- [Proposal decisions](#proposal-decisions)
- [Conflict representation](#conflict-representation)

## Record types

| `record_type` | Location | Purpose |
|---|---|---|
| `candidate` | `Knowledge/Candidates/` | Atomic proposed knowledge plus review state |
| `paper` | `Knowledge/Papers/` | Source-grounded note for one academic paper |
| `canonical` | `Knowledge/Canonical/` | Current semantic owner for one durable topic |
| `proposal` | `.llm-wiki/Proposals/` | Optional preview or delayed/high-risk change artifact |

The synthesis template is a specialized `canonical` record with `knowledge_kind: synthesis`.

## Knowledge kinds

Allowed values:

```text
mechanism
constraint
method
decision-rule
distinction
synthesis
hypothesis
```

This is a closed controlled set shared by every vault and compatible agent. A vault policy may
refine admission or routing for these kinds, but it must not add or rename them. User-, session-,
repository-, project-, organization-, and machine-owned categories do not belong in the central
model.

## Candidate status

| Status | Meaning | `canonical_id` |
|---|---|---|
| `pending` | Captured but not selected | `null` |
| `ready` | Selected for semantic integration | `null` |
| `deferred` | Retained for later evidence, scope, or ownership review | `null` |
| `rejected` | Excluded from active integration | `null` |
| `integrated` | Incorporated into the referenced canonical owner | Existing canonical ID |
| `contested` | Preserved as conflicting evidence in the referenced canonical owner | Existing canonical ID |

Humans may move among `pending`, `ready`, `deferred`, and `rejected` by editing `status`. Capture may
create only `pending`. An explicit user request to integrate a named non-applied candidate is recorded
as a transition to `ready` before canonical curation. Set `integrated` or `contested` only after the
canonical write succeeds.

Authorized review or curation may update only these candidate fields:

```text
status
canonical_id
updated
```

The original body, observation, source references, and evidence qualifiers remain provenance.

## Evidence state

| State | Meaning |
|---|---|
| `unverified` | Preserved by request or inference without a recorded direct check |
| `observed` | Seen in a local experiment, runtime, derivation attempt, or session artifact |
| `source-backed` | Supported by one identifiable external source or a complete formal derivation |
| `corroborated` | Supported by materially independent sources or replicated evidence |
| `contested` | Materially conflicting evidence or incompatible scoped claims remain |

Evidence state is not a scalar probability. It describes support, not scope, truth, or review
maturity.

## Canonical lifecycle

| Lifecycle | Meaning |
|---|---|
| `provisional` | Useful owner under active validation or incomplete synthesis |
| `reviewed` | Scope, sources, and wording received an explicit review pass |
| `stable` | Repeatedly useful and not currently disputed within documented scope |
| `contested` | Intentionally preserves unresolved competing claims |
| `retired` | No longer active; names a successor or explains withdrawal |

Lifecycle records curation maturity. Do not infer `stable` from age, backlinks, or fluent prose.

## Candidate lifecycle relationships

```text
pending  → ready | deferred | rejected
ready    → integrated | contested | deferred | rejected
deferred → ready
rejected → ready
```

`integrated` and `contested` are terminal descriptions of an applied canonical effect. Reconsidering
the underlying knowledge occurs through new evidence and curation, not by rewriting candidate
provenance. `rejected` is excluded from the active queue but remains reviewable; it is not a terminal
provenance state. Naming a non-applied candidate for integration never bypasses this graph: the same
operation first records the applicable transition to `ready`.

## Claim shape

A durable claim is represented as:

```text
claim = (
  statement,
  scope,
  assumptions,
  mechanism_or_rationale,
  evidence_state,
  source_locators,
  invalidation_conditions,
)
```

Missing components require a provisional canonical note or a candidate rather than an overstated
stable claim.

## Paper identity

Resolve paper identity in this order:

```text
DOI → arXiv ID → PMID → stable citation key → source-file SHA-256 prefix
```

A paper note uses `status: source`; paper status is not candidate lifecycle state.

## Proposal decisions

Allowed `decision` values:

```text
create
merge
conflict
reject
defer
retire
```

A proposal records a possible action. It does not authorize application and does not change candidate
status while under review.

## Conflict representation

Before marking a conflict, compare scope, assumptions, definitions, time, and target quantity. A
candidate with `status: contested` must reference a canonical note with either:

```yaml
lifecycle: contested
```

or:

```yaml
evidence_state: contested
```

Use explicit prose labels in paper and canonical notes when needed:

- **Source claim** — directly stated or demonstrated by a source;
- **Interpretation** — an agent's explanation or connection;
- **Inference** — derived but not directly stated;
- **Open question** — unresolved or unsupported extension.
