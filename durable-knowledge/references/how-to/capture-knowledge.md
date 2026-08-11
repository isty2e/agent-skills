# Capture a durable knowledge candidate

Use this guide to preserve a reusable claim from current work without changing canonical knowledge.

## Before capture

1. Resolve the vault.
2. Read the vault-local policy when present, then the bundled
   [admission policy](../reference/admission-policy.md).
3. Identify the owner of the material.

Route user, session, repository, project, organization, and machine-bound facts to their contextual
owner. Do not route away a scientific proposition merely because it was produced in one project.
Continue when the proposed claim is context-complete: incidental origin coordinates are removable,
while semantically essential research scope is explicit.

When the task asks what a research project or corpus has learned, first follow
[Extract durable knowledge from a research corpus](capture-research-knowledge.md).

## Capture procedure

1. State one main proposition without incidental origin-local names. Retain a research program,
   study, system, dataset, or protocol name when it is semantically essential.
2. Apply every condition in the admission test.
3. Search `Knowledge/Canonical/`, `Knowledge/Papers/`, and `Knowledge/Candidates/` for semantic
   owners, aliases, close claims, and existing topic tags. Use bounded title, tag, and claim-keyword
   searches rather than loading the full queue. For each semantically similar deferred or rejected
   candidate, read `review_reason`; recreate the claim only when new scope, evidence, mechanism, or
   reuse value materially addresses that reason.
4. Choose one result:
   - `SKIP` — no durable candidate;
   - `ROUTE` — preserve the material at its contextual owner;
   - `CAPTURE` — write one candidate;
   - `DEFER` — the abstraction lacks enough evidence, scope, or rationale.
5. For `CAPTURE`, instantiate the vault override of `candidate.md` or
   `assets/templates/candidate.md`. Generate the candidate ID using the vault contract's random-suffix
   format and use the full ID as the filename stem.
6. Write one concise semantic `title` and mirror it exactly in the first H1 heading. Do not expose the
   timestamp, random suffix, ticket name, or activity-log wording in the title.
7. Assign zero or more relevant `topic/<lowercase-kebab-case>` tags. Reuse equivalent existing tags;
   add a new topic freely when no equivalent exists. Include every materially relevant topic without
   choosing a primary tag.
8. Separate the actual observation or source claim from the proposed generalization.
9. Record scope, assumptions, mechanism or rationale, a self-contained evidence summary, portable
   source references, and invalidation conditions. When equations or symbolic notation make a
   relationship more precise, use them and define their symbols, domains, assumptions, and prose
   interpretation nearby.
10. Record the likely semantic owner or the search terms used when none was found.
11. Write the note under `Knowledge/Candidates/` with:

   ```yaml
   status: pending
   canonical_id: null
   review_reason: null
   ```

12. Run structural validation.

Capture must not set `ready`, merge canonical notes, or broaden the task into curation.

## Choose candidate granularity

Keep one main proposition per candidate. Split claims only when their scope, evidence, semantic owner,
or invalidation conditions differ.

Prefer a semantic title:

```text
Flexible post-hoc calibration is variance-limited in small residual samples
```

Avoid activity-log titles:

```text
fastcp experiment notes from Tuesday
```

## Handle explicit user requests

An explicit request requires preservation, not necessarily central capture:

- store preferences and standing instructions in user memory;
- store repository implementation, proof-status, run-status, and project-administration facts with
  their owning project;
- preserve self-contained project-originated scientific propositions when they pass admission;
- preserve unsupported scientific assertions as unverified hypotheses;
- create a central candidate only when the abstraction passes admission.

Do not use a central candidate as a fallback when the correct contextual owner is available. Do not
confuse the repository that owns an exact proof or experiment artifact with the semantic owner of the
scientific proposition extracted from it.

## Preserve sources

Do not record a session ID, local path, bare filename, local ticket or issue name, or machine-scoped
artifact label as evidence. These identifiers do not resolve on another synced replica.

For a local observation or derivation, add an evidence capsule under `## Evidence` with:

- a stable anchor such as `### evidence-1`;
- the directly observed or derived claim;
- portable setup, data shape, versions, parameters, and operating conditions that affect the result;
- the result, qualification, uncertainty, and reproduction details when practical.

Set `source_refs` to `embedded:evidence-1`. When an external source exists, add a stable DOI, arXiv,
PMID, URN, or immutable HTTPS locator. When another synced managed note owns the source material, use
`vault:record:<stable-record-id>#<anchor>` instead of its filename.

Do not copy complete conversations, hidden reasoning, secrets, unnecessary personal data, or
proprietary source content. If the useful support cannot be made portable safely, keep the candidate
unverified or defer and route it to the contextual owner.

## Report the result

Report:

- candidate path and ID;
- one-sentence claim;
- `status: pending` and `review_reason: null`;
- evidence state;
- possible canonical owner;
- limitations blocking promotion;
- material routed or skipped instead.
