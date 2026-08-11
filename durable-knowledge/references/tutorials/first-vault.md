# Build your first durable knowledge loop

This tutorial creates a small vault, captures one candidate, reviews it, and integrates it into
canonical knowledge. The result is a complete capture-to-curation loop that works with Obsidian or
any Markdown editor.

## Contents

- [Before you start](#before-you-start)
- [Create the vault](#1-create-the-vault)
- [Capture a candidate](#2-capture-a-candidate)
- [Review the candidate](#3-review-the-candidate)
- [Integrate the candidate](#4-integrate-the-candidate)
- [Inspect the result](#5-inspect-the-result)

## Before you start

You need:

- a local copy of the `durable-knowledge` skill;
- Python 3;
- a writable directory for the vault;
- an agent harness that can load the skill.

Obsidian is optional. If you use it, enable the Bases core plugin before opening the generated
knowledge browser.

## 1. Create the vault

Choose an empty directory or an existing Obsidian vault:

```bash
python <skill>/scripts/bootstrap.py --vault ~/vaults/knowledge
```

The command creates the managed roots without changing existing notes:

```text
Knowledge/
├── Candidates/
├── Papers/
├── Canonical/
├── Artifacts/
├── knowledge-browser.base
└── candidate-review.base
_durable-knowledge/
├── Proposals/
├── templates/
└── ROOT.md
```

The control directory uses an underscore rather than a dot prefix so Obsidian Sync includes it.

Point agents at the vault:

```bash
export DK_VAULT_PATH="$HOME/vaults/knowledge"
```

Confirm the initial structure:

```bash
python <skill>/scripts/validate.py --vault "$DK_VAULT_PATH"
```

## 2. Capture a candidate

Give the agent a portable claim rather than a user preference or repository fact. For example:

```text
Save this as durable knowledge: when an external side effect and its local record cannot commit
atomically, durable intent should precede the side effect so recovery can distinguish work that was
never attempted from work that completed but was not recorded.
```

The agent creates one file under `Knowledge/Candidates/`. Its ID and filename stem use the form
`candidate-<utc>-<slug>-<random16hex>`. Open it and confirm that it contains:

```yaml
record_type: candidate
title: Durable intent should precede non-atomic external side effects
status: pending
canonical_id: null
review_reason: null
tags:
  - topic/distributed-systems
```

The note should separate the observed or sourced claim from the proposed generalization and state its
scope, assumptions, evidence, and invalidation conditions. Its evidence must be understandable from
the note itself, and `source_refs` must use `embedded:<anchor>`, a synced-vault record or
content-addressed artifact ID, or a stable external locator rather than a local path, ticket name, or
session ID.

## 3. Review the candidate

In Obsidian, open `Knowledge/knowledge-browser.base` and select the **Candidate inbox** view. The
human-readable `title` is a clickable link even though the filename remains the machine-oriented
candidate ID, and its topics appear in the **Topics** column. In another Markdown editor, open the
candidate file directly.

Change only the review status:

```yaml
status: ready
```

Leave `canonical_id: null` and `review_reason: null`. The `ready` state authorizes an ordinary
canonical create or merge; it does not authorize retirement or edits to human-owned notes.

## 4. Integrate the candidate

Ask the agent:

```text
Process ready durable-knowledge candidates. Integrate them into canonical knowledge and validate the
vault.
```

The agent searches for an existing semantic owner, creates or updates a note under
`Knowledge/Canonical/`, and then updates the candidate:

```yaml
status: integrated
canonical_id: knowledge-<kind>-<slug>
review_reason: null
```

The canonical write must complete before the candidate claims integration.

## 5. Inspect the result

Open the canonical note and check that it contains:

- a compact core claim;
- scope and assumptions;
- a mechanism or rationale;
- decision implications;
- self-contained evidence and replica-resolvable source references;
- counterexamples or invalidation conditions.

In Obsidian, an integrated or conflict-preserving candidate now appears in the **Integrated
candidates** view with its resulting status. The canonical owner appears automatically in the
**Canonical knowledge** view. In a headless environment, the same states are visible in YAML.

Run validation again:

```bash
python <skill>/scripts/validate.py --vault "$DK_VAULT_PATH"
```

You have now exercised the complete workflow:

```text
capture → pending → human selection → ready → canonical integration → integrated
```

Next, use the task-oriented guides for [paper ingest](../how-to/ingest-paper.md),
[recall](../how-to/recall-knowledge.md), and [multi-client sync](../how-to/sync-clients.md). Read
[the knowledge boundary](../explanation/knowledge-boundary.md) when deciding whether something belongs
in contextual memory or central knowledge.
