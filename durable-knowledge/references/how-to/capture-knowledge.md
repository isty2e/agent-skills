# Capture A Durable Knowledge Candidate

Preserve one reusable claim without changing canonical knowledge.

## Prepare

1. Resolve the vault.
2. Read vault policy, if present, then the [admission policy](../reference/admission-policy.md).
3. Identify the semantic owner.

Route user, session, repository, project, organization, and machine facts to their owners, but do not route away a
self-contained scientific proposition merely because one project produced it. Keep semantically essential program,
study, system, dataset, or protocol scope; remove incidental origin coordinates. For a research corpus, first apply the
[research extraction guide](capture-research-knowledge.md).

## Capture

1. State one main proposition and apply every admission condition.
2. Search bounded titles, tags, and claim keywords in `Knowledge/Canonical/`, `Knowledge/Papers/`, and
   `Knowledge/Candidates/`. Read related deferred/rejected `review_reason`; recreate only when new scope, evidence,
   mechanism, or reuse value addresses it.
3. Choose:
   - `SKIP`: no durable claim;
   - `ROUTE`: preserve with its contextual owner;
   - `CAPTURE`: create one candidate;
   - `REFINE`: revise the same proposition in an existing pending candidate;
   - `DEFER`: evidence, scope, or rationale is insufficient.
4. For `CAPTURE`, resolve `candidate.md`, generate the random-suffix ID defined by the vault contract, and use the full
   ID as filename stem.
5. For `REFINE`, require `pending`; preserve `id`, `record_type`, `created`, and filename. A materially changed
   proposition, owner, or claim split requires `CAPTURE` instead.
6. Write a concise semantic `title` exactly matching the first H1; exclude timestamps, random suffixes, tickets, and
   activity wording.
7. Add zero or more relevant, deduplicated `topic/<lowercase-kebab-case>` tags. Reuse equivalent tags; add a new one
   when needed; do not select a primary topic.
8. Separate observation or source claim from proposed generalization. Record scope, assumptions, mechanism or
   rationale, self-contained evidence, portable references, invalidation conditions, and likely semantic owner or
   owner-search terms. Use equations when they improve precision and define symbols, domains, assumptions, and prose
   interpretation.
9. New candidates start with:

   ```yaml
   status: pending
   canonical_id: null
   review_reason: null
   ```

   Refined candidates remain `pending` and update `updated`.

10. Run structural validation.

Never set `ready`, merge canonical notes, or broaden capture into curation. Return a ready, deferred, or rejected
candidate to `pending` before editing so an old selection or disposition cannot govern new content.

## Granularity And Explicit Requests

Keep one proposition per candidate; split when scope, evidence, owner, or invalidation differs. Prefer a semantic title
such as “Flexible post-hoc calibration is variance-limited in small residual samples,” not “experiment notes from
Tuesday.”

An explicit preservation request does not require central capture. Store preferences in user memory; implementation,
proof/run status, and project administration with the project; admitted self-contained science in candidates; and
unsupported science as scoped unverified hypotheses. Never use a candidate when the correct contextual owner exists.

## Preserve Evidence

For local observation or derivation, add an anchored `## Evidence` capsule containing the claim, portable setup and
conditions, result, qualification or uncertainty, and practical reproduction details. Reference it as
`embedded:<anchor>`. Add stable DOI, arXiv, PMID, URN, immutable HTTPS, or
`vault:record:<stable-id>#<anchor>` locators where applicable. For explicitly authorized exact bytes, apply the
[artifact guide](attach-evidence-artifact.md) and use its `vault:artifact:sha256:<64hex>` reference.

Never cite session IDs, local paths, bare filenames, local ticket/issue names, or machine labels. Do not copy
conversations, hidden reasoning, secrets, unnecessary personal data, or proprietary content. If support cannot be made
portable safely, keep the candidate unverified or defer and route it.

## Report

Report candidate path and ID, one-sentence claim, `pending` status and current `review_reason`, evidence state,
prospective canonical owner, promotion blockers, and material routed or skipped. For refinement, state how any prior
disposition was addressed.
