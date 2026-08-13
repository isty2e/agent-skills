# Attach An Immutable Evidence Artifact

Use when exact small evidence bytes materially improve auditability and an embedded capsule is insufficient. Attachment
requires an explicit request or vault-policy authority; opportunistic capture must not copy available files by default.

## Choose And Check

Prefer, in order:

1. embedded capsules for short derivations, tables, protocols, and text results;
2. content-addressed snapshots for small immutable reports, JSON/CSV, figures, PDFs, or protocols whose bytes matter;
3. version-pinned URLs, DOI/arXiv/URN/SWH IDs, or commits for large, evolving, executable, or external material.

Do not attach datasets, checkpoints, log trees, builds, or frequently regenerated intermediates merely for
self-containment. Require a regular non-symlink file with an extension, no secrets/unnecessary personal or unauthorized
proprietary data, immutable snapshot semantics, acceptable sync size, and untrusted-data handling without execution.
The source system remains authority for evolving content; the vault owns only hash-identified bytes.

## Attach

```bash
python <skill>/scripts/attach_artifact.py \
  --vault <vault> \
  --file <evidence-file>
```

The command atomically writes one complete directory and prints its reference:

```text
Knowledge/Artifacts/artifact-sha256-<64hex>/payload.<ext>
vault:artifact:sha256:<64hex>
```

The operation is content-addressed, append-only, idempotent, and never overwrites. A conflicting payload at the expected
hash path fails.

## Explain And Verify

Add the reference, optionally with `#locator`, to record `source_refs`. The evidence capsule must still explain the
supported claim; material definitions, protocol, parameters, data/sample regime, and toolchain; result, uncertainty,
limitations, and reproduction; and what the external source still owns. Attachment is audit support, not evidence
summary replacement.

Run vault validation. It requires exactly one regular non-symlink payload with matching SHA-256. Also confirm every
replica required to evaluate the artifact receives its extension; local validity does not prove transport. Keep the
semantic capsule sufficient and use an external locator when replication is uncertain.

## Updates And Failures

- Same bytes reuse the reference regardless of source name or extension; changed bytes create a new hash. Never edit a
  payload in place.
- If record update fails after attachment, retry it or remove the unreferenced artifact only after proving no record
  references it.
- Remove interrupted `.artifact-*` directories only after confirming no attachment process owns them.
- The command streams with bounded memory but sets no universal size limit; policy/operator keeps large material
  external.
- Missing, duplicate, symlinked, or hash-mismatched payloads block curation until repaired.
