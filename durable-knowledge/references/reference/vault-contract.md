# Vault Contract Reference

## Layout And Ownership

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
    ├── POLICY.md              # optional
    ├── Proposals/
    └── templates/             # optional overrides
```

The visible control root and Markdown marker replicate through Obsidian Sync without unsupported-file settings. Local
policy may refine admission/routing but must preserve closed `knowledge_kind` values. Everything outside managed roots
is human-owned by default.

| Root                                    | Owner                | Default agent permission                                   |
| --------------------------------------- | -------------------- | ---------------------------------------------------------- |
| `Knowledge/Candidates/**`               | Shared queue         | Create/refine pending; authorized review/curation metadata |
| `Knowledge/Papers/**`                   | Source notes         | Create/update from identified source                       |
| `Knowledge/Canonical/**`                | Reviewed layer       | Read; write for authorized ready-candidate curation        |
| `Knowledge/Artifacts/artifact-sha256-*` | Evidence snapshots   | Explicit/policy-authorized append only                     |
| Both `.base` files                      | Obsidian projections | Create if absent; preserve user customization              |
| `_durable-knowledge/Proposals/**`       | Review artifacts     | Create for preview, delay, retirement, or risk             |
| Everything else                         | Human/external owner | Read/link unless user names exact target                   |

Claim-bearing candidate content changes only in `pending`, for the same proposition, preserving `id`, `record_type`,
`created`, and filename and updating `updated`. Leaving pending freezes the revision; return ready/deferred/rejected to
pending and review again before edits. Integrated/contested revisions are immutable. Authorized review may update
status, canonical ID, review reason, tags, and timestamp; defer/reject requires substantive reason.

Ready authorizes ordinary create/merge only. Conflict, retirement, unrelated canonical changes, and human-note edits
need separate authority. Explicit integration of a named non-applied candidate first records ready; no parallel
canonical-write authorization exists.

## Resolution, Names, And IDs

Resolve explicit user path, then `DK_VAULT_PATH`, then nearest ancestor containing `_durable-knowledge/ROOT.md` and
`Knowledge/`. Otherwise stop; never guess.

Use lowercase kebab-case filenames. New records require `title` exactly matching first H1; IDs and filenames remain
machine identity.

```text
candidate-<utc>-<slug>-<random16hex>
paper-<stable source identifier>
knowledge-<kind>-<slug>
proposal-<utc>-<slug>-<random16hex>
```

`utc` is lowercase compact `YYYYMMDDtHHMMSSffffffz` (for example `20260313t142233123456z`); generate independent 16
lowercase hex suffixes and use full candidate/proposal ID as filename stem. Frontmatter timestamps remain ISO-8601 UTC.
Legacy unsuffixed IDs remain valid. IDs never change after creation, including file rename.

Pending candidate titles may be refined under the claim-revision rule. Authorized canonical title changes preserve ID
and useful former names in aliases. Paper titles identify sources; proposal titles identify actions. Legacy title-less
records warn and display filename; migration may copy existing H1 without rewriting claims.

## Managed Frontmatter

Managed fields are top-level scalars or flat sequences:

```yaml
scalar_field: value
sequence_field:
  - item
empty_sequence: []
```

Validation rejects duplicate managed fields, scalar/sequence mismatch, required empty knowledge sequences, and empty or
placeholder items. Candidate/canonical `scope`, `assumptions`, `invalidation_conditions`, and `source_refs` and proposal
`source_refs` are non-empty. Candidate/paper/canonical `tags` are optional; `[]` means none.

New records require non-empty scalar `title`; when present, missing/different H1 fails. Legacy missing title warns.
Candidate `review_reason` starts `null`, becomes non-empty for defer/reject, and remains mutable review rationale. Legacy
paper `source_uri`/`source_sha256` are optional; URI is null or resolvable HTTPS, digest null or 64 lowercase hex. Topics
are open-vocabulary `topic/<lowercase-kebab-case>`; new/modified values normalize and deduplicate, while legacy issues
warn. Rich extra YAML is allowed but cannot satisfy managed invariants.

## Source References

Refs are replica-resolvable audit/retrieval pointers; the body still owns a self-contained evidence summary.

```text
embedded:<anchor>
vault:record:<stable-id>#<anchor>
vault:artifact:sha256:<64hex>#<optional-locator>
paper:doi:10.xxxx/...#<locator>
paper:arxiv:2605.12341#<locator>
paper:pmid:12345678#<locator>
https://<stable-or-versioned-resource>#<locator>
urn:<namespace>:<identifier>
```

Prefer immutable/versioned HTTPS and commit-pinned repository line URLs. Link managed notes by stable ID, not filename.
Local evidence capsules state claim, portable setup/versions/parameters/conditions, result and qualification, practical
reproduction, and limiting omissions/redactions, then use `embedded:<anchor>`.

Never use local paths, bare filenames, tickets/issues, sessions, machine labels, or `user-instruction` timestamps. A
file hash identifies bytes but is not a locator. Paper claims use page/section/equation/figure/table locators where
available. Do not copy transcripts, hidden reasoning, secrets, unnecessary personal data, or proprietary content.
Legacy local refs may remain as provenance and warn, but cannot propagate into modified canonical state; replace with
embedded or portable support.

## Evidence Artifacts

Managed artifacts use:

```text
Knowledge/Artifacts/artifact-sha256-<64hex>/payload.<extension>
```

They are immutable snapshots, not records or evolving authority. Optional `#locator` targets internal content without
changing identity. Require explicit/policy authority and a regular non-symlink file with extension; copy without
execution; never overwrite; reuse same-byte references regardless of source name or extension; create a new hash for
changed bytes; keep evidence capsules self-contained; and leave large, evolving, executable, sensitive, or externally
governed content at its owner.

Attachment copies to a temporary directory, hashes, then atomically renames without replacement. Validation requires
exactly one regular non-symlink payload matching SHA-256. Paper artifact refs must match `source_sha256`. Unmanaged
unreferenced files are ignored. Transport settings may filter extensions, so every required replica must receive the
payload; local validation proves only local state.

## Templates, Bootstrap, And Migration

Resolve `<name>.md` from vault-local templates, then bundled assets. Overrides must preserve validator-required fields
unless contract and validator change together.

```bash
python <skill>/scripts/bootstrap.py --vault <vault>
python <skill>/scripts/bootstrap.py --vault <vault> --install-policy-copy
```

Bootstrap is idempotent: create missing roots/artifacts/Bases only; preserve notes, artifacts, policies, template
overrides, and existing Bases. The browser covers paper/candidate/canonical navigation and topics; candidate review shows
reason-first Inbox/Ready/Deferred/Rejected views.

Legacy directory migration:

| State                      | Result                             |
| -------------------------- | ---------------------------------- |
| Neither root               | Create `_durable-knowledge/`       |
| Only `.llm-wiki/`          | Rename, then fill missing scaffold |
| Only `_durable-knowledge/` | Preserve; fill missing scaffold    |
| Both                       | Stop without merge/overwrite       |

Migrate first on the complete replica, then sync. Reconcile other dual-root replicas manually. Validation rejects
remaining `.llm-wiki/`.

Legacy marker migration:

| State          | Result                               |
| -------------- | ------------------------------------ |
| Neither        | Create `ROOT.md`                     |
| Only `ROOT`    | Rename to `ROOT.md`                  |
| Only `ROOT.md` | Preserve                             |
| Both identical | Preserve `ROOT.md`; remove duplicate |
| Both different | Stop without overwrite               |

Both marker paths must be regular files; other types fail bootstrap/validation.

## Validation, Replication, And Recovery

```bash
python <skill>/scripts/validate.py --vault <vault>
```

Validation checks structural contracts, not truth, source quality, reviewer identity, semantic equivalence, or historical
edit order. Enforce pending-only revision operationally; use Git/history when auditability matters.

Markdown/YAML is authoritative; Obsidian, Git, and Sync are transports/projections. Desktop/`obsidian` can render/query
Bases; `ob` is headless transport. Every client uses a separate local directory and one sync engine. Bases sync but
headless clients do not render them; sidebar placement is local. Visible control state shares the record replication
boundary. Confirm artifact extensions on all required replicas.

Concurrency is an operating convention, not distributed locking:

- Unique IDs allow concurrent candidate append.
- Persist pending before revising frozen candidate content.
- Same-byte attachments converge on one hash; conflicting existing hash path fails without overwrite.
- Serialize curation per canonical owner; different owners may proceed concurrently.
- Write canonical state before integration/contest metadata.
- After canonical success plus metadata failure, leave/restore ready and reconcile existing owner on retry.
- Verify `base_sha256` before delayed proposal apply.
- Never treat sync merge as semantic approval or auto-resolve canonical conflict files.
- Use Git or another version layer for review and rollback.
