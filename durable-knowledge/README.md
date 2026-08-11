# durable-knowledge skill — draft 0.5.1

`durable-knowledge` is a portable Agent Skill for maintaining a sparse Markdown knowledge base with
human review, optional Obsidian views, grounded paper notes, and bounded recall.

It stores context-complete mechanisms, constraints, methods, decision rules, distinctions,
syntheses, hypotheses, and project-originated scientific propositions. Incidental user, session,
repository, project, organization, or machine state remains with its contextual owner; a named
research program may remain as semantic scope.

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
- [Extract durable knowledge from a research corpus](references/how-to/capture-research-knowledge.md)
- [Attach an immutable evidence artifact](references/how-to/attach-evidence-artifact.md)
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
├── Artifacts/
├── knowledge-browser.base
└── candidate-review.base
_durable-knowledge/
├── README.md
├── Proposals/
├── templates/
└── ROOT.md
```

The control directory is intentionally named `_durable-knowledge/` rather than using a dot prefix.
Obsidian Sync excludes dot-prefixed files and directories other than its configuration directory.
The visible directory and Markdown `ROOT.md` marker keep the control state available on every
replica without requiring the **Sync all other types** setting.

Existing notes and existing bundled Bases are left unchanged. Add `--install-policy-copy` to create
an editable vault-local `_durable-knowledge/POLICY.md` for admission and routing rules. The
package-wide `knowledge_kind` values remain fixed.

Bootstrap automatically renames a legacy `.llm-wiki/` directory when `_durable-knowledge/` is
absent. If both directories exist, it stops without merging them so their contents can be reconciled
manually. It also migrates the former extensionless `_durable-knowledge/ROOT` marker to `ROOT.md`.

Set a default vault for agents:

```bash
export DK_VAULT_PATH="$HOME/path/to/vault"
```

## Browse managed knowledge

Markdown and YAML frontmatter are authoritative. Obsidian is an optional review surface through the
Bases core plugin; any Markdown editor or script can edit the same state.

Open `Knowledge/knowledge-browser.base` to browse all managed knowledge, paper notes, a candidate
inbox, ready and deferred candidates, active canonical knowledge, contested knowledge, integrated
candidate provenance, and retired owners. The Base shows a clickable human-readable `title` and
multi-valued **Topics** while machine-oriented IDs and filenames remain stable. It updates
automatically when matching Markdown records arrive or their lifecycle, review, or topic properties
change.
`Knowledge/candidate-review.base` remains available as a candidate-only view.

New candidate, paper, canonical, and proposal records store their human label in frontmatter and
mirror it in the first H1:

```yaml
title: Variance limits of residual calibration
```

Legacy title-less records remain valid and fall back to the filename in metadata-aware views.

Candidate, paper, and canonical records may use zero or more open-vocabulary topic tags:

```yaml
tags:
  - topic/conformal-prediction
  - topic/uncertainty-quantification
```

Search existing values before adding a new `topic/<lowercase-kebab-case>` tag, but do not force one
primary topic or a directory hierarchy. Multiple topics are expected when a record spans them. Keep
kind, lifecycle, and evidence semantics in their typed frontmatter fields rather than duplicating
them as tags.

The optional community plugin
[Front Matter Title](https://github.com/snezhig/obsidian-front-matter-title) can project the same
frontmatter title into Obsidian's File Explorer. Enable its Explorer surface when that display is
wanted. Its inline-title surface is separate and may create a second visible title alongside the
required H1, depending on client settings. The plugin is a client-local presentation adapter, not
part of the knowledge contract; each client enables it separately, and plain Markdown readers use
the matching first H1.

Reviewers normally change `status`, record disposition rationale, and may refine topic tags:

- `pending` → `ready` to authorize ordinary canonical create or merge;
- `pending` or `ready` → `deferred` with a non-empty `review_reason` to keep the candidate for later;
- `pending` or `ready` → `rejected` with a non-empty `review_reason` to remove it from the active queue;
- add, remove, or normalize `topic/...` tags without rewriting candidate claim provenance.

Before creating a candidate, inspect semantically similar deferred or rejected candidates and their
`review_reason`. Create a duplicate claim only when new scope, evidence, mechanism, or reuse value
materially addresses the recorded reason.

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

## Extract scientific content without losing its owner

A theorem, scientific mechanism, scoped empirical result, or conjecture does not become repository
trivia merely because its current proof or evidence lives in one project. The repository remains
authoritative for exact proof source, declaration and claim IDs, experiment artifacts, manuscript
wording, and current status. The vault may own the self-contained scientific proposition, its scope,
rationale, evidence state, and invalidation conditions.

Use [Extract durable knowledge from a research corpus](references/how-to/capture-research-knowledge.md)
when reviewing a research project. Inventory substantive definitions, theorem families, mechanisms,
results, and conjectures before extracting workflow methodology. Reuse within the same named research
program is sufficient; unrelated-project generality is not required.

## Keep evidence portable across replicas

Each candidate and canonical note must contain enough evidence summary to interpret and evaluate the
claim without access to the originating machine. Use `source_refs` for embedded anchors, synced-vault
record IDs, content-addressed vault artifacts, or stable external locators such as DOI, arXiv, PMID,
URN, and immutable HTTPS URLs. For local observations and derivations, embed a compact evidence
capsule in the note and reference it with `embedded:<anchor>`.

When exact small immutable bytes materially improve auditability, attach them explicitly:

```bash
python ~/.local/share/agent-skills/durable-knowledge/scripts/attach_artifact.py \
  --vault ~/path/to/vault \
  --file ./result.json
```

The command writes `Knowledge/Artifacts/artifact-sha256-<64hex>/payload.<ext>` and prints a
`vault:artifact:sha256:<64hex>` reference. Artifacts are append-only evidence snapshots: changed bytes
produce a new reference, and existing files are never overwritten. The record's evidence capsule
must still explain what the artifact supports. See
[Attach an immutable evidence artifact](references/how-to/attach-evidence-artifact.md).

Do not use local paths, bare filenames, local ticket or issue names, harness session IDs, or
machine-scoped artifact labels as claim support. Existing legacy references remain readable, but the
validator reports portability warnings and curation must not propagate them into new canonical
state.

## Enable an always-on soft reminder

The skill metadata supports opportunistic recall and selective capture without an explicit request.
For harnesses that need a stronger reminder at natural decision points, append
`assets/AGENTS-snippet.md` to their always-on agent instructions. Keep one shared copy so activation
and capture policy do not drift between models.

The reminder is not a completion gate: it must not block the primary task, report no-op checks, or
create weak candidates merely to prove that knowledge was considered. Zero retrieved records and
zero agent-initiated captures are normal. Candidate count has no numeric quota, but every candidate
must independently satisfy admission.

## Validate a vault

```bash
python ~/.local/share/agent-skills/durable-knowledge/scripts/validate.py \
  --vault ~/path/to/vault
```

Validation checks paths, required frontmatter, scalar versus flat-sequence shape, non-empty
knowledge-bearing sequences, placeholder items, duplicate top-level fields and IDs, controlled
values, topic-tag shape and normalization, candidate-to-canonical lifecycle relationships, malformed
or non-portable source-reference forms, content-addressed artifact existence and SHA-256 integrity,
and optional paper source URI and SHA-256 shape. Managed
contract fields use top-level scalars or block sequences; `[]` represents an explicit empty sequence
where allowed. Arbitrary nested
metadata is outside this structural subset.
Missing display titles and portability findings remain warnings for legacy compatibility. A present
`title` must match the first H1. Validation does not establish truth, reviewer identity, source
quality, or semantic equivalence.

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
│   ├── knowledge-browser.base
│   └── templates/
├── scripts/
│   ├── attach_artifact.py
│   ├── bootstrap.py
│   └── validate.py
└── tests/
    ├── test_attach_artifact.py
    ├── test_bootstrap.py
    └── test_validate.py
```

## Draft limitations

- Admission and semantic merge remain model-dependent.
- Recall uses ordinary file and search tools unless a later index is added.
- There is no lock manager or multi-file transaction service.
- Artifact transport depends on each replica's sync settings for the attached file extension.
- Existing human notes are linked rather than rewritten by default.
- Obsidian Headless is an optional sync transport, not a Bases or plugin runtime.
- Earlier draft candidates using `resolution_ref` and `resolved_at` require migration to
  `canonical_id`; the validator rejects mixed lifecycle schemas.
- Candidates already marked `deferred` or `rejected` must add a substantive `review_reason` before
  validation under draft 0.3.0 or later; other existing candidate states remain compatible without
  the field.
- Bootstrap does not overwrite an existing customized `candidate-review.base`; upgrades must merge
  the bundled `review_reason` property and review-view columns deliberately.
