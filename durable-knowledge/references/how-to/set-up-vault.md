# Set up a durable-knowledge vault

Use this guide to initialize an empty directory or add the managed knowledge roots to an existing
Markdown or Obsidian vault.

## Bootstrap the directory

```bash
python <skill>/scripts/bootstrap.py --vault <vault>
```

Bootstrap creates missing managed directories, marker files, explanatory README files, default
template directories, `Knowledge/knowledge-browser.base`, and `Knowledge/candidate-review.base`. It
leaves existing notes and customized files unchanged.

The `_durable-knowledge/` control directory is deliberately visible so Obsidian Sync and ordinary
file replication include it. Obsidian Sync excludes dot-prefixed directories other than its
configuration directory.

To install an editable vault-local admission policy:

```bash
python <skill>/scripts/bootstrap.py \
  --vault <vault> \
  --install-policy-copy
```

The policy is copied to `_durable-knowledge/POLICY.md` only when that file does not already exist.
Customize admission and routing there; keep the record model's `knowledge_kind` values unchanged.

## Migrate a legacy control directory

Vaults created by earlier drafts may contain `.llm-wiki/`. Run the current bootstrap command on the
replica that contains the complete legacy control state:

```bash
python <skill>/scripts/bootstrap.py --vault <vault>
```

When `.llm-wiki/` exists and `_durable-knowledge/` does not, bootstrap renames the directory without
rewriting its files. If both directories exist, bootstrap exits with an error. Compare the two
directories, preserve the intended policy, proposals, and template overrides under
`_durable-knowledge/`, then remove the legacy directory and rerun bootstrap.

## Configure agent discovery

Set the vault path in the environment used to launch the agent:

```bash
export DK_VAULT_PATH="<vault>"
```

An explicit path in a user request overrides the environment variable. Agents running inside the
vault may also discover the nearest ancestor containing `_durable-knowledge/ROOT` and `Knowledge/`.

## Enable Obsidian review

Open the directory as an Obsidian vault and enable the Bases core plugin. Then open:

```text
Knowledge/knowledge-browser.base
```

The browser provides all-knowledge and paper views plus candidate inbox, ready, deferred, canonical,
contested, integrated, and retired views. It displays the frontmatter `title` as a clickable note
link, exposes multi-valued `topic/...` tags as **Topics**, and falls back to the filename for legacy
records. Move the open Base tab into the left sidebar when a persistent knowledge-navigation surface
is useful. Sidebar placement is client-local workspace state.

`Knowledge/candidate-review.base` remains available as a smaller candidate-only queue. Both Bases are
optional projections; any Markdown editor or script can review the same YAML properties.

To show the same `title` in Obsidian's ordinary File Explorer, optionally install the community
plugin [Front Matter Title](https://github.com/snezhig/obsidian-front-matter-title) and enable its
Explorer surface. Each desktop or mobile client must install and enable the plugin independently.
The plugin can also replace Obsidian's inline title, but the skill already preserves the first H1 as
the portable document title; enabling both may show two title surfaces depending on client settings.
The knowledge contract does not depend on the plugin: without it, the first H1 remains authoritative
for the open document and bundled Bases continue to display candidate, paper, and canonical titles.

## Validate the setup

```bash
python <skill>/scripts/validate.py --vault <vault>
```

Re-running bootstrap should report no changes unless managed files were removed:

```bash
python <skill>/scripts/bootstrap.py --vault <vault>
```

Use [Sync desktop and headless clients](sync-clients.md) when the vault must be replicated across
machines.
