# Knowledge admission policy

This policy defines what may enter the central knowledge base. A vault-local
`_durable-knowledge/POLICY.md`, when present, may override admission and routing rules within the fixed record
model. It cannot add or rename `knowledge_kind` values.

## Contents

- [Accepted knowledge kinds](#accepted-knowledge-kinds)
- [Required admission test](#required-admission-test)
- [Routing table](#routing-table)
- [Default exclusions](#default-exclusions)
- [Capture and selection rules](#capture-and-selection-rules)
- [Promotion threshold](#promotion-threshold)

## Accepted knowledge kinds

Every candidate and canonical entry must use one of these values:

- `mechanism`: why a phenomenon occurs;
- `constraint`: what must remain true under a stated class of changes;
- `method`: a reusable procedure with rationale and applicability;
- `decision-rule`: what to choose under stated conditions and trade-offs;
- `distinction`: a boundary that prevents recurring category errors;
- `synthesis`: an evidence-linked relation across sources or observations;
- `hypothesis`: a genuinely unproved, falsifiable proposition with explicit scope and assumptions.

## Required admission test

An agent-initiated candidate must satisfy every condition:

1. **Propositional:** state a claim, mechanism, constraint, method, distinction, or trade-off rather
   than an event log.
2. **Decision-relevant:** likely to alter future reasoning, design, diagnosis, or method selection.
3. **Nontrivial:** not ordinary background knowledge and costly enough to rediscover.
4. **Scoped:** domain, assumptions, target quantity, and invalidation conditions can be stated.
5. **Stable enough:** remains meaningful across likely file moves, refactors, renames, and temporary
   project states.
6. **Not cheaply reconstructible:** cannot be recovered more reliably as a scoped, decision-relevant
   proposition with a quick code search, test, or direct source lookup. Finding an exact proof or
   experiment artifact does not replace semantic extraction when its assumptions, significance, or
   relation to other results remains costly to reconstruct.
7. **Origin-separated:** meaning does not rely on the incidental user, session, working tree, file
   layout, ticket state, organization, or machine where the claim was discovered. A named research
   program, study, system, dataset, or protocol may remain when it is the semantic subject or scope.

Domain, technology, version, time period, data distribution, research program, and operating
conditions may remain as explicit scope. Reuse in future work within the same research program is
sufficient; admission does not require universality or value to unrelated projects.

Use this model qualitatively; do not assign numeric scores:

```text
value ≈ reuse probability × rediscovery cost × decision impact × stability
        − maintenance cost − retrieval noise
```

## Routing table

| Material | Authoritative owner |
|---|---|
| Cross-context mechanism, method, constraint, or distinction | Central knowledge |
| User preference, standing instruction, or personal context | Native user memory or user-owned instructions |
| Session intent, state, or decision | Session state, task plan, or issue |
| Project semantic invariant governing implementation | Repository architecture docs, ADR, tests, or AGENTS.md |
| Project-originated self-contained theorem | Candidate; repository owns exact proof artifact |
| Scoped empirical result with portable support | Candidate; paper note only for paper or preprint source |
| Evolving theorem inventory, declaration or claim IDs, and proof status | Repository |
| Scientific synthesis connecting several project results | Central synthesis |
| Unpublished conjecture with explicit scope and falsification conditions | Pending `hypothesis` candidate |
| Current implementation structure | Code and tests |
| Active defect, branch state, or migration task | Issue tracker or project plan |
| Organization policy or convention | Organization-owned policy or documentation |
| Machine or environment fact | Environment-scoped memory or configuration |
| Claim reported by one paper | Paper note |
| Cross-paper or cross-project synthesis | Central knowledge |
| Unvalidated abstraction from a local observation | Pending candidate |
| Raw transcript or long source excerpt | Source system |

A project-originated finding may seed central knowledge when its proposition is semantically
self-contained, decision-relevant for future work within its documented scope, and supported by a
self-contained evidence capsule or replica-resolvable source reference. A scientific claim does not
become context-bound merely because its only current proof or evidence lives in one project. Require
semantic self-containment and portable evidence, not multiple originating projects.

Do not equate artifact authority with semantic ownership. The repository or manuscript remains
canonical for exact proof source, declaration names, proof status, experiment artifacts, and wording.
The vault may own the extracted theorem, mechanism, scoped result, distinction, or synthesis. A local
path, bare filename, ticket name, session ID, or machine-scoped artifact label does not provide
portable support.

## Default exclusions

Do not agent-initiate central capture for:

- transient task status, test counts, current branch state, or pending work;
- filenames, function names, package layouts, and short-lived commands;
- ordinary bugs already owned by a test or issue;
- implementation and operational facts directly and cheaply readable from code or documentation;
- generic advice that does not constrain a future choice;
- conversational summaries, meeting chronology, or exploratory dead ends;
- unsupported universal claims inferred from one local success or failure; preserve a decision-relevant
  scoped observation or hypothesis instead when its protocol and limits are explicit;
- credentials, private keys, tokens, raw secrets, or unnecessary personal data.

## Capture and selection rules

- Zero agent-initiated candidates is normal.
- Candidate creation has no session, task, source, or backlog quota.
- Every candidate must independently pass the admission test.
- Before capture, inspect semantically similar deferred or rejected candidates and their
  `review_reason`. Do not recreate one unless materially changed scope, evidence, mechanism, or reuse
  value addresses the recorded reason.
- Finish the primary task before marginal capture unless delay would lose the only source locator.
- When reviewing a research corpus, inventory substantive definitions, theorem families, mechanisms,
  empirical results, scoped negative results, and conjectures before extracting workflow methodology.
  Bound the inventory to the user-named or minimally relevant corpus.
- Never ingest an entire session or repository automatically.
- Capture creates `status: pending`, `canonical_id: null`, and `review_reason: null`.
- Capture must never mark its own output `ready`.
- When a user explicitly names a non-applied candidate and requests integration, first transition it
  to `ready` in the same operation; canonical curation still processes only `ready` candidates.
- A request to remember something requires preservation at the correct owner; it does not override
  routing, evidence state, or central admission.

## Promotion threshold

A candidate may become canonical when it has:

- a clear semantic owner and no unresolved near-duplicate identity;
- explicit scope and assumptions;
- a mechanism or rationale adequate for its intended use;
- a self-contained evidence summary plus portable source locators when available;
- explicit invalidation conditions or known limits;
- lifecycle and evidence state that do not overstate certainty;
- `status: ready`.

Cross-source synthesis normally requires at least two materially independent sources or one complete
formal argument plus a clearly marked inference. An explicit exception remains provisional.
