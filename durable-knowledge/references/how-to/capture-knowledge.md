# Capture a durable knowledge candidate

Use this guide to preserve a reusable claim from current work without changing canonical knowledge.

## Before capture

1. Resolve the vault.
2. Read the vault-local policy when present, then the bundled
   [admission policy](../reference/admission-policy.md).
3. Identify the owner of the material.

Route user, session, repository, project, organization, and machine-bound facts to their contextual
owner. Continue only when the proposed claim is plausibly origin-independent.

## Capture procedure

1. State one main proposition without origin-local names unless they are semantically essential.
2. Apply every condition in the admission test.
3. Search `Knowledge/Canonical/` and `Knowledge/Candidates/` for semantic owners, aliases, and close
   claims.
4. Choose one result:
   - `SKIP` — no durable candidate;
   - `ROUTE` — preserve the material at its contextual owner;
   - `CAPTURE` — write one candidate;
   - `DEFER` — the abstraction lacks enough evidence, scope, or rationale.
5. For `CAPTURE`, instantiate the vault override of `candidate.md` or
   `assets/templates/candidate.md`. Generate the candidate ID using the vault contract's random-suffix
   format and use the full ID as the filename stem.
6. Separate the actual observation or source claim from the proposed generalization.
7. Record scope, assumptions, mechanism or rationale, evidence, source references, and invalidation
   conditions.
8. Record the likely semantic owner or the search terms used when none was found.
9. Write the note under `Knowledge/Candidates/` with:

   ```yaml
   status: pending
   canonical_id: null
   ```

10. Run structural validation.

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
- store repository and project facts with their owning project;
- preserve unsupported scientific assertions as unverified hypotheses;
- create a central candidate only when the abstraction passes admission.

Do not use a central candidate as a fallback when the correct contextual owner is available.

## Preserve sources

For session-derived knowledge, record a session ID or artifact locator. Do not copy complete
conversations or hidden reasoning. Cite a result file, test, commit, benchmark, paper locator, or
other checkable artifact when the claim relies on one.

## Report the result

Report:

- candidate path and ID;
- one-sentence claim;
- `status: pending`;
- evidence state;
- possible canonical owner;
- limitations blocking promotion;
- material routed or skipped instead.
