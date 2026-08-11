---
id: proposal-<utc>-<slug>-<random16hex>
title: "Proposal: <short action>"
record_type: proposal
decision: <create|merge|conflict|reject|defer|retire>
target_id: <canonical ID or null>
target_path: <vault-relative path or null>
base_sha256: <64 lowercase hex chars, or null for create, reject, or defer>
candidate_ids:
  - <candidate ID>
source_refs:
  - <embedded evidence, synced-vault record ID, or stable external locator>
created: <ISO-8601 UTC timestamp>
---

# Proposal: <short action>

## Decision

<Why create, merge, conflict, reject, defer, or retire is appropriate.>

## Semantic owner analysis

<Search performed, likely owners considered, and why the target is or is not the correct owner.>

## Scope comparison

<Compare candidate and target scope, assumptions, definitions, and target quantity.>

## Evidence assessment

<Self-contained support, portable source locators, independence, conflicts, and proposed evidence
state. Do not propagate local paths, bare filenames, local ticket names, session IDs, or
machine-scoped artifact labels.>

## Proposed canonical result

<Complete proposed page body or an unambiguous patch. Preserve qualifiers and conflicts.>

## Candidate disposition

<How each candidate's status, canonical_id, tags, and updated timestamp change only after
successful application.>

## Preconditions for apply

- [ ] `base_sha256` still matches the target, or target is a create.
- [ ] Candidate and source references still exist.
- [ ] No new semantic owner or duplicate appeared.
- [ ] Structural validation passes.
- [ ] The applicable authorization exists. Candidate `ready` state covers only an ordinary create or
      merge; it does not authorize conflict, retirement, or edits to human-owned targets.

## Unresolved questions

<Anything that should force defer rather than apply.>
