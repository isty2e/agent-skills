# Knowledge Admission Policy

This defines central admission. Vault-local `_durable-knowledge/POLICY.md` may refine admission/routing within the fixed
record model but cannot add or rename `knowledge_kind` values.

## Knowledge Kinds

- `mechanism`: why a phenomenon occurs;
- `constraint`: what must remain true under stated changes;
- `method`: reusable procedure with rationale and applicability;
- `decision-rule`: what to choose under stated conditions/tradeoffs;
- `distinction`: boundary preventing recurring category errors;
- `synthesis`: evidence-linked relation across sources/observations;
- `hypothesis`: genuinely unproved, falsifiable proposition with explicit scope/assumptions.

## Admission Test

An agent-initiated candidate must satisfy every condition:

1. **Propositional:** claim, mechanism, constraint, method, distinction, or tradeoff, not event log.
2. **Decision-relevant:** likely to change future reasoning, design, diagnosis, or method selection.
3. **Nontrivial:** beyond ordinary background and costly enough to rediscover.
4. **Scoped:** domain, assumptions, target, and invalidation conditions are expressible.
5. **Stable enough:** meaningful across likely moves, refactors, renames, and temporary states.
6. **Not cheaply reconstructible:** no quick search/test/source lookup recovers the same scoped proposition more
   reliably. Easy artifact lookup does not replace costly semantic extraction of assumptions, significance, or
   relations.
7. **Origin-separated:** meaning does not depend on incidental user, session, tree, layout, ticket, organization, or
   machine. Keep a named program, study, system, dataset, or protocol when it is subject or scope.

Domain, technology, version, period, distribution, program, and regime may remain. Reuse within one named research
program suffices; universality is not required. Judge qualitatively, never by numeric score:

```text
value ~= reuse probability * rediscovery cost * decision impact * stability
         - maintenance cost - retrieval noise
```

## Routing

| Material                                                 | Owner                                           |
| -------------------------------------------------------- | ----------------------------------------------- |
| Cross-context mechanism, method, constraint, distinction | Central knowledge                               |
| User preference/instruction/personal context             | User memory or instructions                     |
| Session intent/state/decision                            | Session state, plan, or issue                   |
| Project semantic invariant                               | Repository docs, ADR, tests, or `AGENTS.md`     |
| Self-contained project theorem                           | Candidate; repository owns exact proof          |
| Scoped empirical result with portable support            | Candidate; paper note if paper/preprint sourced |
| Theorem inventory, declarations/claim IDs, proof status  | Repository                                      |
| Cross-result scientific synthesis                        | Central synthesis                               |
| Scoped falsifiable unpublished conjecture                | Pending `hypothesis`                            |
| Current implementation                                   | Code/tests                                      |
| Defect, branch, migration work                           | Tracker/plan                                    |
| Organization policy                                      | Organization docs                               |
| Machine/environment fact                                 | Environment memory/config                       |
| One-paper claim                                          | Paper note                                      |
| Cross-paper/project synthesis                            | Central knowledge                               |
| Unvalidated local abstraction                            | Pending candidate                               |
| Transcript or long excerpt                               | Source system                                   |

One project can seed central knowledge when the proposition is self-contained, decision-relevant in scope, and supported
by an embedded capsule or replica-resolvable locator. Multiple origin projects are unnecessary. Artifact authority
remains with source proof, declaration, status, experiment, and wording; semantic ownership may belong to the vault.
Local paths, filenames, tickets, sessions, and machine labels are not portable support.

## Exclusions

Do not agent-initiate capture for transient task/test/branch state; filenames, package layouts, and short-lived commands;
ordinary test/issue-owned bugs; cheaply readable implementation/operations; unconstraining generic advice; chronology,
summaries, or dead ends; unsupported universals from one local outcome; or credentials, secrets, and unnecessary personal
data. A scoped observation/hypothesis may qualify when protocol and limits are explicit.

## Capture And Selection

- Zero candidates is normal; no quota exists, and each must pass independently.
- Search related deferred/rejected candidates and reasons before capture; require new scope, evidence, mechanism, or
  reuse value to recreate.
- Finish primary work before marginal capture unless delay loses the only locator.
- For research, inventory definitions, theorems, mechanisms, results, scoped negatives, and conjectures before workflow
  methodology, within bounded corpus scope.
- Never ingest a whole session/repository automatically.
- Capture creates `pending`, `canonical_id: null`, `review_reason: null`, never `ready`.
- Explicit integration of a named non-applied candidate first records `ready`; curation still processes only ready.
- “Remember” requires preservation at the correct owner, not automatic central admission.

## Promotion

Canonical promotion requires a clear owner without unresolved duplicate identity; explicit scope/assumptions; adequate
mechanism/rationale; self-contained evidence and portable locators when available; invalidation conditions/limits;
non-overstated lifecycle/evidence; and `status: ready`. Cross-source synthesis normally needs two materially independent
sources or one complete formal argument plus marked inference; exceptions remain provisional.
