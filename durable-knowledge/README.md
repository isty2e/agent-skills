# durable-knowledge skill — draft 0.1.0

`durable-knowledge` is a portable Agent Skill for maintaining a sparse Markdown knowledge base with
human review, optional Obsidian views, grounded paper notes, and bounded recall.

It stores origin-independent mechanisms, constraints, methods, decision rules, distinctions, and
syntheses. User preferences and session-, repository-, project-, organization-, or machine-bound
facts remain with their contextual owner.

## Start here

Follow [Build your first durable knowledge loop](references/tutorials/first-vault.md) to bootstrap a
vault, capture a candidate, select it for review, and integrate it into canonical knowledge.

## Documentation

The bundled documentation follows Diátaxis. Choose a document by what you need now.

### Tutorials — learn through a complete exercise

- [Build your first durable knowledge loop](references/tutorials/first-vault.md)

### How-to guides — accomplish a task

- [Set up a durable-knowledge vault](references/how-to/set-up-vault.md)
- [Capture a durable knowledge candidate](references/how-to/capture-knowledge.md)
- [Curate selected candidates](references/how-to/curate-candidates.md)
- [Ingest an academic paper](references/how-to/ingest-paper.md)
- [Recall relevant knowledge](references/how-to/recall-knowledge.md)
- [Sync desktop and headless clients](references/how-to/sync-clients.md)
- [Evaluate durable-knowledge behavior](references/how-to/evaluate-skill.md)

### Reference — consult contracts and controlled values

- [Knowledge admission policy](references/reference/admission-policy.md)
- [Record model](references/reference/record-model.md)
- [Vault contract](references/reference/vault-contract.md)

### Explanation — understand the design

- [Why knowledge is separate from contextual memory](references/explanation/knowledge-boundary.md)
- [Understanding knowledge routing through examples](references/explanation/routing-examples.md)

## Install one canonical skill copy

Place the package at a stable path and point compatible harnesses to the same directory:

```bash
mkdir -p ~/.local/share/agent-skills ~/.codex/skills ~/.pi/agent/skills
mv durable-knowledge ~/.local/share/agent-skills/

ln -s ~/.local/share/agent-skills/durable-knowledge \
  ~/.codex/skills/durable-knowledge
ln -s ~/.local/share/agent-skills/durable-knowledge \
  ~/.pi/agent/skills/durable-knowledge
```

Inspect existing paths before creating symlinks. Do not overwrite another installed skill silently.

## Bootstrap a vault

```bash
python ~/.local/share/agent-skills/durable-knowledge/scripts/bootstrap.py \
  --vault ~/path/to/vault
```

Bootstrap creates:

```text
Knowledge/
├── README.md
├── Candidates/
├── Papers/
├── Canonical/
└── candidate-review.base
.llm-wiki/
├── README.md
├── Proposals/
├── templates/
└── ROOT
```

Existing notes and an existing `candidate-review.base` are left unchanged. Add
`--install-policy-copy` to create an editable vault-local `.llm-wiki/POLICY.md` for admission and
routing rules. The package-wide `knowledge_kind` values remain fixed.

Set a default vault for agents:

```bash
export DK_VAULT_PATH="$HOME/path/to/vault"
```

## Review candidates

Markdown and YAML frontmatter are authoritative. Obsidian is an optional review surface through the
Bases core plugin; any Markdown editor or script can edit the same state.

Reviewers normally change only `status`:

- `pending` → `ready` to authorize ordinary canonical create or merge;
- `pending` or `ready` → `deferred` to keep the candidate for later;
- `pending` or `ready` → `rejected` to remove it from the active queue.

Capture never sets `ready`, and agents curate only `ready` candidates. When a user explicitly names
a non-applied candidate and requests integration, the agent first sets it to `ready` in the same
operation and then curates it.

## Use multiple clients

Each machine keeps a separate local replica connected to the same remote vault:

```text
                 Obsidian Sync remote vault
              ┌───────────┼───────────┐
        desktop client  desktop client  headless client
        Obsidian app     Obsidian app   ob sync
```

All clients are peers at the sync layer. Their capabilities differ:

- `obsidian` controls a running desktop app and can open or query Bases;
- `ob` is the headless Sync and Publish client;
- agents read and write the local Markdown/YAML replica directly.

Run one sync engine per local vault path and serialize concurrent edits to the same canonical note.
New candidates and proposals use a 16-character random hex suffix in both the ID and filename to
avoid ordinary cross-replica creation collisions. Existing IDs remain valid. See
[Sync desktop and headless clients](references/how-to/sync-clients.md) for setup commands.

## Enable rare agent-initiated capture

Append `assets/AGENTS-snippet.md` to the always-on agent instructions used by each harness. Keep one
shared copy so capture policy does not drift between models.

Zero agent-initiated captures is normal. Candidate count has no numeric quota, but every candidate
must independently satisfy admission.

## Validate a vault

```bash
python ~/.local/share/agent-skills/durable-knowledge/scripts/validate.py \
  --vault ~/path/to/vault
```

Validation checks paths, required frontmatter, scalar versus flat-sequence shape, non-empty
knowledge-bearing sequences, placeholder items, duplicate top-level fields and IDs, controlled
values, and candidate-to-canonical lifecycle relationships. Managed contract fields use top-level
scalars or block sequences; `[]` represents an explicit empty sequence where allowed. Arbitrary
nested metadata is outside this structural subset. Validation does not establish truth, reviewer
identity, source quality, or semantic equivalence.

## Package layout

```text
durable-knowledge/
├── SKILL.md
├── README.md
├── references/
│   ├── tutorials/
│   ├── how-to/
│   ├── reference/
│   └── explanation/
├── assets/
│   ├── AGENTS-snippet.md
│   ├── candidate-review.base
│   └── templates/
├── scripts/
│   ├── bootstrap.py
│   └── validate.py
└── tests/
    └── test_validate.py
```

## Draft limitations

- Admission and semantic merge remain model-dependent.
- Recall uses ordinary file and search tools unless a later index is added.
- There is no lock manager or multi-file transaction service.
- Existing human notes are linked rather than rewritten by default.
- Obsidian Headless is an optional sync transport, not a Bases or plugin runtime.
- Earlier draft candidates using `resolution_ref` and `resolved_at` require migration to
  `canonical_id`; the validator rejects mixed lifecycle schemas.
