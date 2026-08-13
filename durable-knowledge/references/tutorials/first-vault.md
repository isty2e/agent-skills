# Build Your First Durable Knowledge Loop

Create a vault, capture one candidate, review it, and integrate it. You need the skill, Python 3, a writable directory,
and a compatible harness. Obsidian is optional; enable Bases before using the generated browser.

## 1. Create The Vault

```bash
python <skill>/scripts/bootstrap.py --vault ~/vaults/knowledge
export DK_VAULT_PATH="$HOME/vaults/knowledge"
python <skill>/scripts/validate.py --vault "$DK_VAULT_PATH"
```

Bootstrap preserves existing notes and creates:

```text
Knowledge/{Candidates,Papers,Canonical,Artifacts}/
Knowledge/knowledge-browser.base
Knowledge/candidate-review.base
_durable-knowledge/{Proposals,templates}/
_durable-knowledge/ROOT.md
```

The visible control root lets Obsidian Sync include it.

## 2. Capture

Give the agent a portable proposition rather than preference or repository fact:

```text
Save this as durable knowledge: when an external effect and its local record cannot commit atomically, durable intent
should precede the effect so recovery distinguishes never attempted from completed but unrecorded work.
```

The resulting `Knowledge/Candidates/candidate-<utc>-<slug>-<random16hex>.md` should include:

```yaml
record_type: candidate
title: Durable intent should precede non-atomic external side effects
status: pending
canonical_id: null
review_reason: null
tags:
  - topic/distributed-systems
```

Confirm title matches H1; observation/source is separate from generalization; scope, assumptions, evidence, and
invalidation are explicit; and refs use embedded anchors, synced records/artifacts, or stable external locators, never
local paths, tickets, or sessions.

## 3. Review

Open the candidate directly or use the browser's Candidate inbox. While pending, refine the same proposition in place,
preserving ID, creation, and filename, updating `updated`, and validating. A materially different proposition needs a
new candidate.

Select the exact revision:

```yaml
status: ready
canonical_id: null
review_reason: null
```

Ready authorizes ordinary create/merge and freezes claim-bearing content. Revision requires pending, edit, validation,
and reselection. It does not authorize retirement or human-note edits.

## 4. Integrate

Ask:

```text
Process ready durable-knowledge candidates. Integrate them into canonical knowledge and validate the vault.
```

The agent resolves the semantic owner, writes canonical state, then updates the candidate:

```yaml
status: integrated
canonical_id: knowledge-<kind>-<slug>
review_reason: null
```

Canonical write must precede integration status.

## 5. Inspect

Confirm the owner contains claim, scope/assumptions, mechanism/rationale, decision implications, self-contained evidence
with portable refs, and counterexamples/invalidation. Verify integrated/contested and canonical views or inspect YAML
headlessly, then run:

```bash
python <skill>/scripts/validate.py --vault "$DK_VAULT_PATH"
```

The exercised lifecycle is:

```text
capture -> pending -> selection -> ready -> canonical integration -> integrated
```

Continue with [paper ingest](../how-to/ingest-paper.md), [recall](../how-to/recall-knowledge.md),
[sync](../how-to/sync-clients.md), or the [knowledge boundary](../explanation/knowledge-boundary.md).
