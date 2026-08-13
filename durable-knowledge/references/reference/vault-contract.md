# Vault contract reference

## Contents

- [Managed layout](#managed-layout)
- [Ownership and write permissions](#ownership-and-write-permissions)
- [Vault resolution](#vault-resolution)
- [Naming and IDs](#naming-and-ids)
- [Frontmatter subset](#frontmatter-subset)
- [Source references](#source-references)
- [Evidence artifacts](#evidence-artifacts)
- [Template resolution](#template-resolution)
- [Bootstrap interface](#bootstrap-interface)
- [Legacy control-directory migration](#legacy-control-directory-migration)
- [Validation interface](#validation-interface)
- [Replication model](#replication-model)
- [Concurrency and recovery](#concurrency-and-recovery)

## Managed layout

```text
<vault>/
├── Knowledge/
│   ├── Candidates/
│   ├── Papers/
│   ├── Canonical/
│   ├── Artifacts/
│   ├── knowledge-browser.base
│   └── candidate-review.base
└── _durable-knowledge/
    ├── ROOT.md
    ├── POLICY.md
    ├── Proposals/
    └── templates/
```

`POLICY.md` and vault-local templates are optional. Policy overrides may refine admission and
routing, but they must preserve the record model's closed `knowledge_kind` set. Everything outside
the managed roots is human-owned by default.

`_durable-knowledge/` is intentionally visible. Obsidian Sync excludes dot-prefixed directories
other than its configuration directory, so a hidden control root would not replicate with the
knowledge records it governs. The marker uses Markdown so default note synchronization transports it
without requiring unsupported-file syncing on every replica.

## Ownership and write permissions

| Root | Owner | Default agent permission |
|---|---|---|
| `Knowledge/Candidates/**` | Shared review queue | Create or refine pending drafts; review or curation updates managed metadata |
| `Knowledge/Papers/**` | Source-grounded notes | Create or update from the identified source |
| `Knowledge/Canonical/**` | Reviewed knowledge layer | Read; write only for `ready` candidates |
| `Knowledge/Artifacts/artifact-sha256-*` | Evidence snapshots | Explicit or policy-authorized append only |
| `Knowledge/knowledge-browser.base` | Obsidian projection | Create if absent; users may customize |
| `Knowledge/candidate-review.base` | Obsidian projection | Create if absent; users may customize |
| `_durable-knowledge/Proposals/**` | Review artifacts | Create for preview, delay, retirement, or risk |
| Everything else | Human or external owner | Read and link only unless the user names the exact target |

For an existing candidate, claim-bearing fields and body content may change only while
`status: pending`, and only while preserving the same proposed proposition. Preserve `id`,
`record_type`, `created`, and the filename; update `updated`. Once the candidate leaves `pending`,
its claim-bearing revision is frozen. Return a ready, deferred, or rejected candidate to `pending`
before changing that revision, then require a new review. Integrated and contested claim revisions
are immutable.

Review or authorized curation may change `status`, `canonical_id`, `review_reason`, `tags`, and
`updated` without reopening the claim. Topic tags and `review_reason` are mutable curation metadata.
Deferred and rejected candidates require a substantive `review_reason` explaining the disposition.

`status: ready` authorizes ordinary create or merge under `Knowledge/Canonical/`. It does not
authorize conflict, retirement, unrelated canonical changes, or edits to human-owned notes. When an
explicit user request names a non-applied candidate and requests integration, first transition it to
`ready` in the same operation; the request does not create a second canonical-write authorization
path.

## Vault resolution

Resolve a target in this order:

1. explicit user-supplied path;
2. `DK_VAULT_PATH`;
3. nearest ancestor containing both `_durable-knowledge/ROOT.md` and `Knowledge/`.

Do not guess a destination. The `_durable-knowledge/ROOT.md` marker prevents accidental writes to an
arbitrary repository.

## Naming and IDs

Use lowercase kebab-case filenames. For new candidate, paper, canonical, and proposal records, store
the canonical human-readable label in the `title` frontmatter field and mirror it exactly in the
first H1 heading. Metadata-aware Obsidian surfaces may use `title` for display while IDs and filenames
remain machine-oriented identity and collision-control artifacts.

Recommended IDs:

```text
candidate-<utc>-<slug>-<random16hex>
paper-<stable source identifier>
knowledge-<kind>-<slug>
proposal-<utc>-<slug>-<random16hex>
```

Use `YYYYMMDDtHHMMSSffffffz` for the lowercase compact UTC component, for example
`20260313t142233123456z`. Generate `random16hex` independently for each candidate or proposal as 16
lowercase hexadecimal characters. Use the full candidate or proposal ID as its filename stem so
concurrent replicas also produce distinct filenames.

Frontmatter timestamps remain ISO-8601 UTC values. Existing IDs without the random suffix remain
valid; the validator preserves that compatibility and checks completed records for duplicate IDs.
IDs are stable after creation. Renaming a file must not change its ID.

Candidate titles may be refined while `status: pending`; after selection they follow the candidate
revision freeze. Canonical titles may change during authorized curation without changing the
canonical ID; retain useful former names in `aliases`. Paper titles identify their source, and
proposal titles describe their proposed action. Legacy records without `title` remain valid and fall
back to their filenames in metadata-aware views. A deliberate schema migration may copy an existing
first H1 into a missing `title` without otherwise changing candidate claim content.

## Frontmatter subset

Managed contract fields use top-level scalars or flat sequences:

```yaml
scalar_field: value
sequence_field:
  - first item
  - second item
empty_sequence: []
```

The validator enforces these shapes only for fields owned by the record model. It rejects duplicate
top-level fields, scalar/sequence mismatches, empty required knowledge-bearing sequences, and empty
or placeholder sequence items. Candidate and canonical `scope`, `assumptions`,
`invalidation_conditions`, and `source_refs` must contain at least one item. Proposal `source_refs`
must also contain at least one item. Candidate, paper, and canonical `tags` are optional flat
sequences; `[]` means that no topic has been assigned.

New candidate, paper, canonical, and proposal records must provide a non-empty scalar `title`. The
validator keeps legacy title-less records compatible by reporting a warning rather than an error.
When `title` is present, a missing or different first H1 is an error because it would create two
conflicting human labels.

Candidate `review_reason` is an optional managed scalar and starts as `null`. It becomes required and
non-empty when `status` is `deferred` or `rejected`. It records review rationale rather than claim
provenance, so authorized review may revise or clear it without changing the candidate body.

Paper `source_uri` and `source_sha256` are optional managed scalars for legacy compatibility. When
present, `source_uri` must be `null` or a resolvable HTTPS URI, and `source_sha256` must be `null` or
64 lowercase hexadecimal characters.

Topic values use `topic/<lowercase-kebab-case>`. Multiple topics are allowed, order carries no
meaning, and the vocabulary is open after searching existing tags for an equivalent label. The
validator warns rather than fails on legacy unnamespaced or duplicate tags, but new and modified
records must normalize them.

Additional metadata may use richer YAML, but the validator does not interpret its nested meaning.
Do not move a managed contract field into nested metadata or rely on unvalidated metadata to satisfy
a record invariant.

## Source references

`source_refs` are portable audit and retrieval pointers. The record body must still contain the
claim-supporting evidence summary needed to interpret and evaluate the claim. A reference is portable
only when another synced replica can resolve it from the vault itself or through a stable external
identifier or URI. Validation warns when a reference uses a local-only form, an unknown form, or a
recognized prefix without the required identifier, anchor, or HTTPS host.

Recommended forms:

```text
embedded:<evidence-anchor>
vault:record:<stable-record-id>#<anchor>
vault:artifact:sha256:<64hex>#<optional-locator>
paper:doi:10.xxxx/...#<page-section-equation-figure-or-table>
paper:arxiv:2605.12341#<page-section-equation-figure-or-table>
paper:pmid:12345678#<page-section-equation-figure-or-table>
https://<stable-or-versioned-resource>#<exact-locator>
urn:<namespace>:<identifier>
```

Use immutable or version-pinned HTTPS URLs when practical. Reference repository evidence through a
remotely resolvable URL pinned to a commit and exact lines, not through a repository nickname and
local relative path. Reference another managed note by stable record ID rather than filename so file
moves and renames do not break the locator.

For a local observation or derivation, include an evidence capsule in the current record with:

- the directly observed or derived claim;
- portable setup, data shape, versions, parameters, and operating conditions that materially affect
  the result;
- the result and its qualification or uncertainty;
- reproduction details when practical;
- omissions or redactions that limit independent checking.

Point to that capsule with `embedded:<anchor>`. Do not put local paths, bare filenames, local ticket
or issue names, harness session IDs, machine-scoped artifact labels, or `user-instruction` timestamps
in `source_refs`. A file hash may identify bytes or check integrity, but it is not a resolvable source
locator by itself.

Paper claims require exact page, section, equation, figure, or table locators where available. Do not
copy complete transcripts, hidden reasoning, secrets, unnecessary personal data, or proprietary
source content into the vault.

Existing records may retain legacy local references as immutable provenance. Validation warns about
these references without invalidating the vault. Do not copy them into a new or updated canonical
record; preserve the useful support as an embedded capsule or replace the pointer with a portable
locator.

## Evidence artifacts

`Knowledge/Artifacts/` may contain immutable content-addressed payloads named:

```text
artifact-sha256-<64 lowercase hexadecimal characters>/payload.<extension>
```

The payload is an evidence snapshot, not a managed knowledge record and not the evolving authority
for a proof, experiment, dataset, manuscript, or external source. Its bytes are identified by the
SHA-256 in the containing directory and `vault:artifact:sha256:` reference. The optional `#locator`
identifies a relevant theorem, table, page, field, or other internal target without changing artifact
identity.

Artifact creation follows these rules:

- attach only a regular non-symlink file with an extension;
- require an explicit user request or vault-policy authorization;
- copy bytes without executing or interpreting the source;
- never overwrite an existing payload;
- reuse the existing reference when the same bytes already exist, regardless of source filename or
  extension;
- create a new hash directory and payload when the bytes change;
- keep the supporting evidence capsule self-contained enough to interpret the claim without relying
  on the payload alone;
- keep large, evolving, executable, sensitive, or externally governed material at a stable external
  owner when a vault snapshot is inappropriate.

The bundled attachment command writes one payload into a temporary directory, hashes the copied
bytes, and atomically renames the complete directory to its hash identity without replacing an
existing entry. Validation resolves each artifact reference, requires exactly one regular
non-symlink payload, and verifies its SHA-256. A paper note using a vault artifact as `source_ref`
must use the same digest in `source_sha256`.
Unreferenced files that do not use the managed content-addressed naming scheme remain outside this
contract and are ignored.

Artifact file extensions remain subject to the capabilities and settings of the configured sync
transport. A locally valid reference is not replica-portable until every replica required to evaluate
it has received the payload.

## Template resolution

For `<name>.md`:

1. use `<vault>/_durable-knowledge/templates/<name>.md` when present;
2. otherwise use `assets/templates/<name>.md` from the skill package.

A vault override must preserve fields required by `scripts/validate.py` unless the validator and
contract change together.

## Bootstrap interface

```bash
python <skill>/scripts/bootstrap.py --vault <vault>
```

Optional policy copy:

```bash
python <skill>/scripts/bootstrap.py \
  --vault <vault> \
  --install-policy-copy
```

Bootstrap is idempotent. It creates `Knowledge/Artifacts/` when absent and does not modify existing
artifacts, notes, policy copies, template overrides, or an existing bundled Base. It installs
`Knowledge/knowledge-browser.base` for candidate, paper, and
canonical navigation and retains `Knowledge/candidate-review.base` as the focused candidate queue.
Both projections expose topic tags from managed frontmatter; the focused review Base also displays
`review_reason` across Inbox, Ready, Deferred, and Rejected views so reason-first edits are available
without opening the note body.

## Legacy control-directory migration

Earlier drafts used `.llm-wiki/`, which Obsidian Sync does not replicate. Bootstrap applies this
migration contract:

| Existing state | Result |
|---|---|
| Neither directory exists | Create `_durable-knowledge/` scaffolding |
| Only `.llm-wiki/` exists | Rename it to `_durable-knowledge/`, then create missing scaffolding |
| Only `_durable-knowledge/` exists | Preserve it and create only missing scaffolding |
| Both directories exist | Stop without merging or overwriting either directory |

Run migration first on the replica containing the complete legacy policy, proposals, and template
overrides, then let the new visible directory synchronize. If another replica contains both paths,
reconcile them manually before running bootstrap there. Validation rejects a remaining
`.llm-wiki/` directory so split control authority cannot pass unnoticed.

Earlier visible control directories used an extensionless `_durable-knowledge/ROOT` marker, which
Obsidian Sync omits unless every client enables unsupported file types. Bootstrap applies this marker
migration contract:

| Existing marker state | Result |
|---|---|
| Neither marker exists | Create `ROOT.md` |
| Only `ROOT` exists | Rename it to `ROOT.md` |
| Only `ROOT.md` exists | Preserve it |
| Both exist with identical contents | Preserve `ROOT.md` and remove the extensionless duplicate |
| Both exist with different contents | Stop without overwriting either file |

Marker paths must be regular files. A directory or other non-file entry at either marker path fails
bootstrap and validation.

## Validation interface

```bash
python <skill>/scripts/validate.py --vault <vault>
```

Validation checks structural contracts, not semantic truth, source quality, reviewer identity, or
semantic equivalence. It validates the current snapshot and cannot prove whether a candidate was
edited before or after a lifecycle transition. Enforce the pending-only claim-edit rule through the
write workflow and use Git or another history layer when revision auditability matters.

## Replication model

Markdown and YAML are authoritative local state. Obsidian, Git, Obsidian Sync, and other transports
may replicate the vault without becoming semantic authorities.

Desktop and headless Sync clients are equal replicas connected to one remote vault. Capabilities
differ: the desktop app and `obsidian` CLI can project Properties and Bases, while `ob` provides
headless Sync and Publish transport.

Every client must use a separate local vault directory. Run one sync engine per local path; do not run
desktop Sync and Headless Sync against the same directory.

The `.base` definitions sync as vault files and automatically query newly arrived records. Whether a
Base is pinned in a sidebar belongs to each desktop client's workspace state and may require local
setup. Headless clients synchronize `.base` files but do not render them.

The `_durable-knowledge/` directory also syncs as ordinary vault content. Its Markdown marker,
policy, proposals, and template overrides therefore share the same replication boundary as managed
records without a per-device unsupported-file setting.

Evidence artifacts live in visible `Knowledge/Artifacts/`, but some extensions may require transport
configuration on every client. Confirm required replicas receive an attached payload; validation can
check only the local replica.

## Concurrency and recovery

Concurrency control is a lightweight operating convention, not a distributed lock protocol. The
skill does not create lock files, leases, or a coordination service.

- Multiple clients may append candidates with unique IDs and filenames.
- Persist a transition back to `pending` before revising claim-bearing candidate content. This
  ordering prevents another replica from observing a changed claim under stale `ready`, `deferred`,
  or `rejected` authorization metadata.
- Repeated or concurrent attachment of identical artifact bytes converges on one hash directory even
  when source extensions differ. A conflicting existing hash path fails without overwrite.
- Only one curation transaction may modify a given canonical note at a time.
- Different canonical owners may be curated concurrently.
- Write canonical state before marking a candidate `integrated` or `contested`.
- If candidate metadata fails after a canonical write, leave or restore the candidate as `ready` and
  reconcile against the existing canonical owner on retry.
- Verify `base_sha256` before delayed proposal application.
- Do not treat an automatic sync merge as semantic approval.
- Do not auto-resolve sync-conflict files in canonical notes.
- Use Git or another versioning layer when review and rollback matter.
