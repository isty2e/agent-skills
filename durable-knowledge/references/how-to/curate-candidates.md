# Curate selected candidates

Use this guide to integrate human-selected candidates into canonical knowledge or preserve an
explicit conflict.

## Contents

- [Select authorized candidates](#select-authorized-candidates)
- [Integrate directly](#integrate-directly)
- [Prepare a proposal when needed](#prepare-a-proposal-when-needed)
- [Merge without prose accretion](#merge-without-prose-accretion)
- [Handle human-owned notes](#handle-human-owned-notes)
- [Retire a canonical owner](#retire-a-canonical-owner)
- [Recover from partial failure](#recover-from-partial-failure)
- [Report the result](#report-the-result)

## Select authorized candidates

Process only candidates with `status: ready`.

When a user explicitly names a non-applied candidate and requests integration, select it in the same
operation before canonical curation:

1. set `status: ready`;
2. keep `canonical_id: null`;
3. set `updated` to the current UTC timestamp.

Naming a candidate without requesting integration does not select it. The `ready` transition is the
single authorization path for an ordinary create or merge under `Knowledge/Canonical/`; it does not
authorize conflict, retirement, edits to human-owned notes, or unrelated canonical changes.

Humans may triage queue state in Obsidian, another Markdown editor, or a script:

```text
pending  → ready | deferred | rejected
deferred → ready
rejected → ready
```

These review transitions leave `canonical_id: null` and do not rewrite candidate provenance.

## Integrate directly

1. Read the admission policy, record model, and vault contract.
2. Select authorized candidates.
3. Search canonical IDs, titles, aliases, summaries, body text, and backlinks.
4. Identify the semantic owner by meaning, scope, assumptions, definitions, and target quantity.
5. Read the evidence capsules and portable source locators needed to support the change.
6. Choose one decision:
   - `create` — no semantic owner exists;
   - `merge` — an existing owner covers the compatible claim;
   - `conflict` — materially competing evidence remains under compatible scope;
   - `reject` — material is not durable, supported, or correctly routed;
   - `defer` — evidence, scope, or identity remains incomplete;
   - `retire` — an obsolete canonical owner has an authorized successor.
7. Confirm that the current authorization covers the chosen effect and that no other curation
   operation is modifying the same canonical owner.
8. For create, resolve `canonical-entry.md`, except that `knowledge_kind: synthesis` resolves
   `synthesis.md`. For merge, retain the existing canonical owner's record shape.
9. Give a new canonical owner a concise semantic `title` and mirror it exactly in the first H1. The
   canonical title names the durable topic and need not copy the candidate title. A title change on
   an existing canonical owner preserves its stable ID and records useful former names in `aliases`.
10. For create or merge, write the canonical result and inspect the diff. Restate the minimum
   claim-supporting evidence in the canonical note so it does not depend on the candidate file or an
   originating local source.
11. For conflict, preserve each competing claim and set canonical `lifecycle: contested` or
   `evidence_state: contested`.
12. After the canonical write succeeds, update each applied candidate:

    ```yaml
    status: integrated  # or contested
    canonical_id: <existing canonical ID>
    updated: <current UTC timestamp>
    ```

13. Run structural validation.

## Prepare a proposal when needed

Use `_durable-knowledge/Proposals/` instead of direct application when:

- the user requests a preview or diff;
- application will be delayed;
- the change retires a canonical owner;
- the target is human-owned;
- unresolved risk makes direct application inappropriate.

To prepare a proposal:

1. Compute the target canonical SHA-256 for merge, conflict, or retire; use `null` for create, reject,
   or defer.
2. Instantiate the vault override of `merge-proposal.md` or the bundled template. Generate the
   proposal ID using the vault contract's random-suffix format and use the full ID as the filename
   stem.
3. Give the proposal a concise `Proposal: <short action>` title and mirror it exactly in the first
   H1.
4. Record the proposed canonical body or patch, candidate IDs, source references, and unresolved
   questions.
5. Leave candidate status unchanged while the proposal is only under review.
6. Before delayed application, require the current target hash to match `base_sha256`.

A proposal records a possible action. It does not authorize application.

## Merge without prose accretion

- Merge only claims with compatible semantic ownership.
- Preserve narrower scopes instead of flattening them into a universal statement.
- Add evidence without automatically increasing lifecycle or evidence state.
- Preserve candidate IDs as provenance when useful, but never propagate a local path, bare filename,
  local ticket or issue name, session ID, or machine-scoped artifact label into canonical
  `source_refs`.
- State what changed and why when evidence revises a claim.
- Rewrite the canonical page into a coherent current model rather than appending disconnected
  fragments.
- Preserve or improve equations and symbolic notation when they make the canonical relationship
  more precise. Define symbols, domains, and assumptions nearby, and retain a concise prose
  interpretation.
- Preserve important dissent in evidence and conflict sections.

## Handle human-owned notes

When a human-owned note already discusses the topic:

- create or update an agent-managed canonical page that links to it; or
- prepare a proposal targeting the human note.

Do not edit the human-owned note without an explicit request naming that target.

## Retire a canonical owner

Retirement requires explicit authorization. Keep the stable ID and historical rationale, set
`lifecycle: retired`, and identify a successor or explain why none exists. The retired page remains
linkable.

## Recover from partial failure

Canonical state must become durable before candidate status claims integration. If the canonical
write succeeds but candidate metadata fails:

1. leave or restore the candidate as `ready`;
2. search for the existing canonical owner on retry;
3. reconcile the candidate with that owner instead of creating a duplicate.

Do not auto-resolve concurrent edits or sync-conflict files in a canonical note.

## Report the result

Distinguish:

- queue state changed only;
- canonical create, merge, or conflict applied;
- proposal prepared but not applied;
- candidate left ready after a failed precondition;
- validation or base-hash failure.
