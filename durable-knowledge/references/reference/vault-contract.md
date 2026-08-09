# Vault contract reference

## Contents

- [Managed layout](#managed-layout)
- [Ownership and write permissions](#ownership-and-write-permissions)
- [Vault resolution](#vault-resolution)
- [Naming and IDs](#naming-and-ids)
- [Frontmatter subset](#frontmatter-subset)
- [Source references](#source-references)
- [Template resolution](#template-resolution)
- [Bootstrap interface](#bootstrap-interface)
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
│   └── candidate-review.base
└── .llm-wiki/
    ├── ROOT
    ├── POLICY.md
    ├── Proposals/
    └── templates/
```

`POLICY.md` and vault-local templates are optional. Policy overrides may refine admission and
routing, but they must preserve the record model's closed `knowledge_kind` set. Everything outside
the managed roots is human-owned by default.

## Ownership and write permissions

| Root | Owner | Default agent permission |
|---|---|---|
| `Knowledge/Candidates/**` | Shared review queue | Append pending candidates; curation updates lifecycle fields |
| `Knowledge/Papers/**` | Source-grounded notes | Create or update from the identified source |
| `Knowledge/Canonical/**` | Reviewed knowledge layer | Read; write only for `ready` candidates |
| `Knowledge/candidate-review.base` | Obsidian projection | Create if absent; users may customize |
| `.llm-wiki/Proposals/**` | Optional review artifacts | Create when preview, delay, retirement, or risk justifies one |
| Everything else | Human or external owner | Read and link only unless the user names the exact target |

For an existing candidate, review or authorized curation may change only `status`, `canonical_id`, and
`updated`. Treat all other fields and body content as provenance.

`status: ready` authorizes ordinary create or merge under `Knowledge/Canonical/`. It does not
authorize conflict, retirement, unrelated canonical changes, or edits to human-owned notes. When an
explicit user request names a non-applied candidate and requests integration, first transition it to
`ready` in the same operation; the request does not create a second canonical-write authorization
path.

## Vault resolution

Resolve a target in this order:

1. explicit user-supplied path;
2. `DK_VAULT_PATH`;
3. nearest ancestor containing both `.llm-wiki/ROOT` and `Knowledge/`.

Do not guess a destination. The `.llm-wiki/ROOT` marker prevents accidental writes to an arbitrary
repository.

## Naming and IDs

Use lowercase kebab-case filenames. Keep the visible title in frontmatter and the H1 heading.

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
must also contain at least one item.

Additional metadata may use richer YAML, but the validator does not interpret its nested meaning.
Do not move a managed contract field into nested metadata or rely on unvalidated metadata to satisfy
a record invariant.

## Source references

Recommended forms:

```text
paper:doi:10.xxxx/...
paper:arxiv:2605.12341
paper:pmid:12345678
file:sha256:<hex>
session:<harness>:<session-id>
artifact:<repository-or-project>:<relative-path>@<commit-or-hash>
user-instruction:<UTC timestamp>
```

Paper claims require exact page, section, equation, figure, or table locators where available. Do not
copy complete transcripts into the vault.

## Template resolution

For `<name>.md`:

1. use `<vault>/.llm-wiki/templates/<name>.md` when present;
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

Bootstrap is idempotent. It does not modify existing notes, policy copies, template overrides, or an
existing `Knowledge/candidate-review.base`.

## Validation interface

```bash
python <skill>/scripts/validate.py --vault <vault>
```

Validation checks structural contracts, not semantic truth, source quality, reviewer identity, or
semantic equivalence.

## Replication model

Markdown and YAML are authoritative local state. Obsidian, Git, Obsidian Sync, and other transports
may replicate the vault without becoming semantic authorities.

Desktop and headless Sync clients are equal replicas connected to one remote vault. Capabilities
differ: the desktop app and `obsidian` CLI can project Properties and Bases, while `ob` provides
headless Sync and Publish transport.

Every client must use a separate local vault directory. Run one sync engine per local path; do not run
desktop Sync and Headless Sync against the same directory.

## Concurrency and recovery

Concurrency control is a lightweight operating convention, not a distributed lock protocol. The
skill does not create lock files, leases, or a coordination service.

- Multiple clients may append candidates with unique IDs and filenames.
- Only one curation transaction may modify a given canonical note at a time.
- Different canonical owners may be curated concurrently.
- Write canonical state before marking a candidate `integrated` or `contested`.
- If candidate metadata fails after a canonical write, leave or restore the candidate as `ready` and
  reconcile against the existing canonical owner on retry.
- Verify `base_sha256` before delayed proposal application.
- Do not treat an automatic sync merge as semantic approval.
- Do not auto-resolve sync-conflict files in canonical notes.
- Use Git or another versioning layer when review and rollback matter.
