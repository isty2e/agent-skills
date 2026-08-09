# Set up a durable-knowledge vault

Use this guide to initialize an empty directory or add the managed knowledge roots to an existing
Markdown or Obsidian vault.

## Bootstrap the directory

```bash
python <skill>/scripts/bootstrap.py --vault <vault>
```

Bootstrap creates missing managed directories, marker files, explanatory README files, default
template directories, and `Knowledge/candidate-review.base`. It leaves existing notes and customized
files unchanged.

To install an editable vault-local admission policy:

```bash
python <skill>/scripts/bootstrap.py \
  --vault <vault> \
  --install-policy-copy
```

The policy is copied to `.llm-wiki/POLICY.md` only when that file does not already exist. Customize
admission and routing there; keep the record model's `knowledge_kind` values unchanged.

## Configure agent discovery

Set the vault path in the environment used to launch the agent:

```bash
export DK_VAULT_PATH="<vault>"
```

An explicit path in a user request overrides the environment variable. Agents running inside the
vault may also discover the nearest ancestor containing `.llm-wiki/ROOT` and `Knowledge/`.

## Enable Obsidian review

Open the directory as an Obsidian vault and enable the Bases core plugin. Then open:

```text
Knowledge/candidate-review.base
```

The Base is optional. Any Markdown editor or script can review the same YAML properties.

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
