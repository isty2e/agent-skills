# Curate Selected Candidates

Integrate selected candidates into canonical knowledge or preserve explicit conflict.

## Select Authorized Candidates

Process only `ready`. It freezes `title`, `knowledge_kind`, `evidence_state`, `scope`, `assumptions`,
`invalidation_conditions`, `source_refs`, and body. Tags and review metadata remain mutable. To revise frozen content,
set `pending`, keep `canonical_id: null`, update the timestamp, edit, validate, and select again.

An explicit request to integrate a named non-applied candidate may select it in the same operation: set `ready`, keep
`canonical_id: null`, and update UTC `updated` before curation. Naming without an integration request does not select.
`ready` authorizes ordinary canonical create/merge only, not conflict, retirement, human-note edits, or unrelated
changes.

Allowed review transitions:

```text
pending  -> ready | deferred | rejected
ready    -> pending | deferred | rejected
deferred -> pending | ready
rejected -> pending | ready
```

Returning to pending withdraws prior selection/disposition. Other review transitions keep `canonical_id: null` and do
not edit frozen claims. `deferred`/`rejected` require substantive `review_reason`; property-by-property UIs should save
the reason before status. Clear or revise stale rationale when moving to ready. Update `updated` for every metadata
change.

## Integrate

1. Read the admission policy, record model, and vault contract; select authorized candidates.
2. Search canonical IDs, titles, aliases, topics, summaries, body, and backlinks. Resolve owner by meaning, scope,
   assumptions, definitions, and target quantity, not title.
3. Read required evidence and portable locators; validate any artifact payload.
4. Decide:
   - `create`: no owner exists;
   - `merge`: an owner covers a compatible claim;
   - `conflict`: materially competing evidence remains under compatible scope;
   - `reject` or `defer`: no canonical write; set status/reason, keep `canonical_id: null`, update, validate, stop;
   - `retire`: an authorized successor replaces an obsolete owner.
5. Confirm authority for the chosen effect and exclusive modification of that canonical owner.
6. For create, resolve `canonical-entry.md`, or `synthesis.md` for synthesis. Merge retains the owner's record shape.
7. Give a new owner a semantic `title` matching H1. Existing title changes retain ID and useful former names in
   `aliases`.
8. Reconcile relevant candidate, paper, and canonical topic tags; do not copy mechanically.
9. For create/merge, write canonical state, inspect the diff, and restate minimum supporting evidence so the owner does
   not depend on candidate or local source. For conflict, preserve each claim and set canonical lifecycle or evidence
   state to `contested`.
10. Only after canonical success, set each applied candidate:

    ```yaml
    status: integrated # or contested
    canonical_id: <canonical ID>
    review_reason: null
    updated: <current UTC timestamp>
    ```

11. Run structural validation.

## Proposals

Use `_durable-knowledge/Proposals/` when the user requests preview/diff, application is delayed, retirement is proposed,
the target is human-owned, or unresolved risk blocks direct application.

1. For merge/conflict/retire, compute target SHA-256; use `null` for create/reject/defer.
2. Resolve `merge-proposal.md`, generate the random-suffix proposal ID, and use it as filename stem.
3. Set a concise `Proposal: <action>` title matching H1.
4. Record proposed body or patch, candidate IDs, source refs, and unknowns.
5. Leave candidate status unchanged during review.
6. Before delayed application, require current target hash to equal `base_sha256`.

A proposal describes an action; it does not authorize it.

## Merge Discipline

- Merge only compatible semantic owners; preserve narrower scopes and genuine dissent.
- New evidence does not automatically raise lifecycle or evidence state.
- Keep useful candidate IDs as provenance, but never propagate local paths, filenames, tickets, sessions, or machine
  labels into canonical refs.
- State evidence-driven revisions and rewrite a coherent current model rather than appending fragments.
- Preserve useful equations with definitions, assumptions, and prose interpretation.
- For a human-owned note, link it from an agent-managed owner or propose a named-target edit; never edit it implicitly.
- Retirement needs explicit authority, stable ID and rationale, `lifecycle: retired`, and successor or reason none exists.

## Recovery And Report

Canonical state must precede integration metadata. If metadata fails after canonical success, leave or restore `ready`,
clear/revise stale reason, find the existing owner on retry, and reconcile rather than duplicate. Never auto-resolve
concurrent edits or sync-conflict canonical files.

Report separately: queue-only transition; applied create/merge/conflict; unapplied proposal; candidate left ready after a
failed precondition; and validation or base-hash failure.
