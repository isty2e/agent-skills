# Record Model Reference

Templates define full note bodies; `scripts/validate.py` enforces managed frontmatter from the vault contract.

## Record Types

| `record_type` | Location                        | Purpose                                    |
| ------------- | ------------------------------- | ------------------------------------------ |
| `candidate`   | `Knowledge/Candidates/`         | Atomic proposed knowledge and review state |
| `paper`       | `Knowledge/Papers/`             | One source-grounded academic note          |
| `canonical`   | `Knowledge/Canonical/`          | Current owner for one durable topic        |
| `proposal`    | `_durable-knowledge/Proposals/` | Optional preview/delayed/high-risk action  |

Synthesis is canonical with `knowledge_kind: synthesis`. Content-addressed artifacts are immutable evidence payloads,
not records; the referencing record owns their semantic role.

## Titles And Topics

New records require non-empty `title` exactly matching first H1. `id` and filename remain stable identity. Pending
candidate titles may change only for the same proposition; after pending they freeze with the reviewed claim. Authorized
curation may rename canonical owners without changing ID and should preserve useful former names in `aliases`. Paper
titles identify sources; proposal titles conventionally start `Proposal:`. Legacy missing titles warn and fall back to
filename; migration may copy existing H1 but cannot rewrite claims.

Candidate, paper, and canonical `tags` are optional flat sequences of deduplicated
`topic/<lowercase-kebab-case>`. Search before adding equivalent open-vocabulary topics. Multiple topics are valid; order,
primary topic, location, and ownership carry no tag semantics. Keep kind, review state, lifecycle, and evidence in typed
fields. Tags are mutable curation metadata and need not copy mechanically during promotion. Legacy unnamespaced or
duplicate tags warn; new/modified records must normalize them.

## Knowledge Kinds

```text
mechanism
constraint
method
decision-rule
distinction
synthesis
hypothesis
```

This set is closed across vaults. Theorem/formal-proof/empirical-result/experiment describe statement or evidence form,
not semantic role. A theorem may encode constraint, mechanism, distinction, or method; empirical evidence may support
any kind. Zero occurrence is not automatically a constraint: use distinction for non-observation versus impossibility,
or hypothesis for an unproved explanation, with direct support `evidence_state: observed`. Source artifacts retain their
authority separately from extracted propositions.

## Candidate Status

| Status       | Meaning                          | `canonical_id`        | `review_reason` |
| ------------ | -------------------------------- | --------------------- | --------------- |
| `pending`    | Editable, unselected draft       | `null`                | Optional        |
| `ready`      | Selected frozen revision         | `null`                | Optional        |
| `deferred`   | Retained for later review        | `null`                | Required        |
| `rejected`   | Excluded from active integration | `null`                | Required        |
| `integrated` | Incorporated into owner          | Existing canonical ID | Optional        |
| `contested`  | Preserved as owner conflict      | Existing canonical ID | Optional        |

Capture creates only pending. Explicit named integration transitions to ready before curation. Set integrated/contested
only after canonical success.

Pending editors may refine the same proposition while preserving `id`, `record_type`, `created`, and filename and
updating `updated`; materially changed proposition, owner, or split requires a new candidate. Leaving pending freezes
`title`, kind, evidence state, scope, assumptions, invalidation conditions, source refs, and body. Return ready/deferred/
rejected to pending before claim edits and review again. Integrated/contested records are immutable provenance.

Authorized review may update status, canonical ID, review reason, tags, and timestamp without redefining the claim.
`review_reason` is one substantive disposition scalar, required for defer/reject; clear or revise stale reasons after
state change.

## Evidence State

| State           | Meaning                                                        |
| --------------- | -------------------------------------------------------------- |
| `unverified`    | Requested/inferred without recorded direct check               |
| `observed`      | Direct result with portable material setup and result          |
| `source-backed` | One identifiable external source or complete formal derivation |
| `corroborated`  | Independent sources/derivations/replications agree             |
| `contested`     | Material conflict under compatible scope                       |

Evidence state describes support, not probability, scope, truth, or maturity. Partial derivation/computation is observed;
a complete formal derivation can be source-backed while evolving proof source remains repository-owned, provided the
record preserves statement, assumptions, proof/derivation capsule, and material verification conditions.

## Canonical Lifecycle

| Lifecycle     | Meaning                                                   |
| ------------- | --------------------------------------------------------- |
| `provisional` | Useful owner under active validation/incomplete synthesis |
| `reviewed`    | Scope, sources, and wording explicitly reviewed           |
| `stable`      | Repeatedly useful and undisputed within scope             |
| `contested`   | Preserves unresolved competing claims                     |
| `retired`     | Inactive; names successor or withdrawal reason            |

Lifecycle is curation maturity; age, backlinks, and fluency do not imply stable.

## Lifecycle Graph

```text
pending  -> ready | deferred | rejected
ready    -> pending | integrated | contested | deferred | rejected
deferred -> pending | ready
rejected -> pending | ready
```

Defer/reject sets reason and `updated`; property-by-property editors save reason before status. Persist pending before
claim edits so replicas never see revised content under stale authorization. Returning ready should clear/revise stale
rationale. Integrated/contested are terminal applied effects; reconsider through new evidence/curation. Rejected may
return to pending for revision or directly to ready for unchanged reconsideration. Named integration still follows the
ready edge.

## Claim Shape And Notation

```text
claim = (
  statement, scope, assumptions, mechanism_or_rationale,
  evidence_state, evidence_summary, portable_source_refs,
  invalidation_conditions,
)
```

Missing parts require candidate/provisional status, not overstated stable knowledge. Evidence summary must stand alone
on replicas; refs improve audit/retrieval but cannot carry meaning. Artifacts preserve bytes, while records own
interpretation and conditions. Local paths, filenames, tickets/issues, sessions, and machine labels are not portable.

Use standard Markdown/Obsidian-compatible notation when it improves precision/falsifiability. Define symbols, domains,
indices, units, and assumptions nearby and explain the regime in prose. Avoid decorative equations and plugin-local
macros unless policy standardizes them.

## Paper Identity And Proposals

```text
DOI -> arXiv ID -> PMID -> stable citation key -> source-file SHA-256 prefix
```

Paper notes use `status: source`; source hash gives identity/integrity, not portable location, and originating path is
never stored.

Proposal decisions are `create`, `merge`, `conflict`, `reject`, `defer`, and `retire`. A proposal neither authorizes
application nor changes candidate status during review.

## Conflict

Compare scope, assumptions, definitions, time, and target before conflict. A contested candidate must reference a
canonical note with `lifecycle: contested` or `evidence_state: contested`. Label prose when useful as **Source claim**,
**Interpretation**, **Inference**, or **Open question**.
