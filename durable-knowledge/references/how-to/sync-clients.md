# Sync desktop and headless clients

Use Obsidian Sync to replicate one durable-knowledge vault across desktop and Linux clients. Each
client owns a separate local copy connected to the same remote vault. An active Obsidian Sync
subscription is required.

## Contents

- [Choose the client for each machine](#choose-the-client-for-each-machine)
- [Connect the desktop client](#connect-the-desktop-client)
- [Connect a Linux headless client](#connect-a-linux-headless-client)
- [Run multiple clients safely](#run-multiple-clients-safely)
- [Verify the replicated vault](#verify-the-replicated-vault)
- [Upstream documentation](#upstream-documentation)

## Choose the client for each machine

| Client | Command | Requires desktop app | Purpose |
|---|---|---:|---|
| Obsidian desktop | Obsidian app | Yes | Editing, Properties, Bases, desktop Sync |
| Obsidian CLI | `obsidian` | Yes, running | Open, query, and automate the desktop app |
| Obsidian Headless | `ob` | No | Sync and Publish transport on servers |

Obsidian Headless does not provide the desktop command surface or execute Bases. Server-side agents
work directly with the synced Markdown and YAML files.

## Connect the desktop client

On each desktop machine:

1. Open or create a local vault.
2. Connect it to the intended Obsidian Sync remote vault.
3. Enable the Bases core plugin if you want to use `Knowledge/knowledge-browser.base` or the focused
   `Knowledge/candidate-review.base`.
4. Let the initial sync finish before editing shared files.

The optional desktop CLI can open or query the knowledge browser while Obsidian is running:

```bash
cd "$DK_VAULT_PATH"
obsidian open path="Knowledge/knowledge-browser.base"
obsidian base:query \
  path="Knowledge/knowledge-browser.base" \
  view="Ready for curation" \
  format=paths
```

Use `property:set` only for a review transition explicitly requested by the user. Capture must not
select its own output by setting `ready`.

## Connect a Linux headless client

Install Node.js 22 or later and the official headless package:

```bash
npm install -g obsidian-headless
```

Set up a separate local replica:

```bash
mkdir -p ~/vaults/knowledge
cd ~/vaults/knowledge

ob login
ob sync-list-remote
ob sync-setup \
  --vault "My Knowledge Vault" \
  --device-name "knowledge-server"
```

Run a one-time sync:

```bash
ob sync --path ~/vaults/knowledge
```

Keep the replica current under an existing process supervisor:

```bash
ob sync --path ~/vaults/knowledge --continuous
```

Point the agent at that local replica:

```bash
export DK_VAULT_PATH="$HOME/vaults/knowledge"
```

The agent reads and writes files under `DK_VAULT_PATH`; `ob` only transports those changes.

## Run multiple clients safely

Desktop and headless clients are equal replicas at the sync layer. Multiple desktop clients and
multiple headless clients may connect to the same remote vault.

Apply these constraints:

- Give every client its own local vault directory.
- Run one sync engine for a given local vault path.
- Do not run desktop Sync and Headless Sync against the same local directory.
- Let initial sync complete before enabling writes on a new replica.
- Keep claim support inside the synced record or behind a synced-vault ID or stable external URI;
  never cite an originating machine's path, bare filename, local ticket name, or session ID.
- Use the random-suffixed candidate and proposal IDs from the vault contract, with each full ID as
  the filename stem.
- Serialize edits to the same canonical note.
- Do not rely on Sync to provide a multi-file transaction.
- Choose and review conflict behavior on every client; the skill never treats an automatic merge as
  semantic approval.

Different canonical notes may be curated concurrently. The exclusivity boundary is one canonical
semantic owner, not the entire vault. Serialization is an operator or agent responsibility; the
skill does not create synchronized lock files or run a coordination service.

## Verify the replicated vault

On a headless client:

```bash
ob sync-status --path ~/vaults/knowledge
python <skill>/scripts/validate.py --vault ~/vaults/knowledge
```

On a desktop client, confirm that:

- newly captured candidates appear in the Inbox view;
- a `ready` edit reaches the headless replica;
- integrated candidates move to the Integrated view;
- contested candidates move to the Contested view;
- canonical notes remain free of unresolved sync-conflict files.

Use Git or another backup layer in addition to Sync when rollback and diff review matter.

## Upstream documentation

- [Obsidian CLI](https://obsidian.md/cli)
- [Obsidian Headless](https://github.com/obsidianmd/obsidian-headless)
