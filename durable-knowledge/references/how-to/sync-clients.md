# Sync Desktop And Headless Clients

Replicate one vault through Obsidian Sync. Every client uses a separate local copy connected to the same remote vault;
an active subscription is required.

| Client            | Command    | Desktop required | Purpose                          |
| ----------------- | ---------- | ---------------: | -------------------------------- |
| Obsidian desktop  | app        |              Yes | Editing, Properties, Bases, Sync |
| Obsidian CLI      | `obsidian` |     Yes, running | Open/query/automate desktop      |
| Obsidian Headless | `ob`       |               No | Server Sync/Publish transport    |

Headless does not execute Bases. Server agents read/write synced Markdown/YAML. Visible `_durable-knowledge/` and
Markdown `ROOT.md` ensure marker, policy, proposals, and templates sync without enabling unsupported file types.

## Desktop

1. Open/create a local vault and connect the intended remote.
2. Enable Bases if using the bundled browsers.
3. Let initial sync finish before writes.

Optional CLI while desktop runs:

```bash
cd "$DK_VAULT_PATH"
obsidian open path="Knowledge/knowledge-browser.base"
obsidian base:query path="Knowledge/knowledge-browser.base" view="Ready for curation" format=paths
```

Use `property:set` only for an explicitly requested review transition; capture cannot select itself as ready.

## Linux Headless

Install Node.js 22+ and `obsidian-headless`, then create a separate replica:

```bash
npm install -g obsidian-headless
mkdir -p ~/vaults/knowledge && cd ~/vaults/knowledge
ob login
ob sync-list-remote
ob sync-setup --vault "My Knowledge Vault" --device-name "knowledge-server"
ob sync --path ~/vaults/knowledge
```

Under an existing supervisor, use `ob sync --path ~/vaults/knowledge --continuous`. Point agents at the local replica:

```bash
export DK_VAULT_PATH="$HOME/vaults/knowledge"
```

`ob` transports changes; the agent owns file operations.

## Safety

- One local directory and one sync engine per client; never run desktop and headless Sync on one path.
- Finish initial sync and confirm `_durable-knowledge/ROOT.md` before writes.
- Keep evidence in synced records/artifacts or stable external URIs, never originating paths, filenames, tickets, or
  sessions.
- Configure every client for artifact extensions required there.
- Use random-suffixed candidate/proposal IDs and full-ID filenames.
- Serialize same-canonical-owner edits. Different owners may proceed concurrently.
- Sync is not a transaction, lock service, or semantic approval. Configure conflict behavior and never auto-approve
  merges.

## Verify

On headless:

```bash
ob sync-status --path ~/vaults/knowledge
python <skill>/scripts/validate.py --vault ~/vaults/knowledge
```

On desktop, confirm control state/policy/templates, candidate queue transitions, integrated/contested views, absence of
unresolved canonical conflicts, and artifact presence plus validation on every required replica. Use Git or another
backup when rollback and diff review matter.

Upstream: [CLI](https://obsidian.md/cli), [Headless](https://github.com/obsidianmd/obsidian-headless), and
[Sync settings](https://obsidian.md/help/sync/settings).
