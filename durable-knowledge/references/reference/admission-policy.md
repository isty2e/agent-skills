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
- `hypothesis`: a potentially reusable claim that remains provisional.

## Required admission test

An agent-initiated candidate must satisfy every condition:

1. **Propositional:** state a claim, mechanism, constraint, method, distinction, or trade-off rather
   than an event log.
2. **Decision-relevant:** likely to alter future reasoning, design, diagnosis, or method selection.
3. **Nontrivial:** not ordinary background knowledge and costly enough to rediscover.
4. **Scoped:** domain, assumptions, target quantity, and invalidation conditions can be stated.
5. **Stable enough:** remains meaningful across likely file moves, refactors, renames, and temporary
   project states.
6. **Not cheaply reconstructible:** cannot be recovered more reliably with a quick code search, test,
   or direct source lookup.
7. **Origin-independent:** meaning and reuse do not depend on a particular user, session, repository,
   project, organization, or machine.

Domain, technology, version, time period, data distribution, and operating conditions may remain as
explicit scope. Origin independence does not require universality.

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
| Project semantic invariant | Repository architecture docs, ADR, tests, or AGENTS.md |
| Current implementation structure | Code and tests |
| Active defect, branch state, or migration task | Issue tracker or project plan |
| Organization policy or convention | Organization-owned policy or documentation |
| Machine or environment fact | Environment-scoped memory or configuration |
| Claim reported by one paper | Paper note |
| Cross-paper or cross-project synthesis | Central knowledge |
| Unvalidated abstraction from a local observation | Pending candidate |
| Raw transcript or long source excerpt | Source system |

A project-local finding may seed central knowledge only when the abstraction has a credible mechanism,
clear scope, value outside the originating repository, and a self-contained evidence capsule or
replica-resolvable source reference. A local path, bare filename, ticket name, session ID, or
machine-scoped artifact label does not satisfy this requirement.

## Default exclusions

Do not agent-initiate central capture for:

- transient task status, test counts, current branch state, or pending work;
- filenames, function names, package layouts, and short-lived commands;
- ordinary bugs already owned by a test or issue;
- facts directly and cheaply readable from code or documentation;
- generic advice that does not constrain a future choice;
- conversational summaries, meeting chronology, or exploratory dead ends;
- unsupported universal claims inferred from one local success or failure;
- credentials, private keys, tokens, raw secrets, or unnecessary personal data.

## Capture and selection rules

- Zero agent-initiated candidates is normal.
- Candidate creation has no session, task, source, or backlog quota.
- Every candidate must independently pass the admission test.
- Before capture, inspect semantically similar deferred or rejected candidates and their
  `review_reason`. Do not recreate one unless materially changed scope, evidence, mechanism, or reuse
  value addresses the recorded reason.
- Finish the primary task before marginal capture unless delay would lose the only source locator.
- Never ingest an entire session automatically.
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
