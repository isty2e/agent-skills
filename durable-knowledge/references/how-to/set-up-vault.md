# Set Up A Durable-Knowledge Vault

Initialize an empty directory or add managed roots to a Markdown/Obsidian vault.

## Bootstrap

```bash
python <skill>/scripts/bootstrap.py --vault <vault>
```

Bootstrap creates missing managed roots, `Knowledge/Artifacts/`, markers, READMEs, template directories, and both
bundled Bases; it preserves existing notes, artifacts, and customized files. `_durable-knowledge/` is visible so Sync
replicates control state, and `ROOT.md` needs no per-client unsupported-file setting.

Optional editable policy:

```bash
python <skill>/scripts/bootstrap.py --vault <vault> --install-policy-copy
```

This creates `_durable-knowledge/POLICY.md` only when absent. It may refine admission/routing, not record-model
`knowledge_kind` values.

## Migrate Legacy State

Run bootstrap first on the replica with complete legacy state. If only `.llm-wiki/` exists, bootstrap renames it; if
both old and new directories exist, it stops. Manually preserve intended policy, proposals, and template overrides under
`_durable-knowledge/`, remove the old directory, and rerun.

Bootstrap similarly renames sole extensionless `_durable-knowledge/ROOT` to `ROOT.md`, removes an identical duplicate,
and stops when both differ.

## Configure Discovery

```bash
export DK_VAULT_PATH="<vault>"
```

An explicit user path overrides the environment. Agents inside a vault may find the nearest ancestor containing both
`_durable-knowledge/ROOT.md` and `Knowledge/`.

## Optional Obsidian Review

Enable the Bases core plugin and open `Knowledge/knowledge-browser.base` for managed knowledge, papers, candidate queue,
canonical/contested/integrated/retired views, clickable titles, and topics. Sidebar placement is client-local.
`Knowledge/candidate-review.base` is a smaller queue whose Inbox/Ready/Deferred/Rejected views show `review_reason`,
allowing reason-before-status edits. Any Markdown editor or script can edit the same authoritative YAML.

Bootstrap preserves existing Bases. On upgrade, merge needed `review_reason` columns from the bundled candidate Base or
replace only after preserving customizations.

Front Matter Title may optionally project frontmatter titles into File Explorer; each client configures it separately.
Its inline title can duplicate the required H1. No knowledge contract depends on the plugin.

## Verify

```bash
python <skill>/scripts/validate.py --vault <vault>
python <skill>/scripts/bootstrap.py --vault <vault>
```

The second command should report no changes unless managed files were removed. Apply the
[sync guide](sync-clients.md) for multi-machine replicas.
