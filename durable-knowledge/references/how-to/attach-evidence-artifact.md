# Attach an immutable evidence artifact

Use this guide when an exact small evidence file materially improves auditability or reproduction and
an embedded Markdown capsule is not sufficient. Artifact attachment is explicit work; opportunistic
capture must not copy files merely because they are available.

## Contents

- [Choose the evidence form](#choose-the-evidence-form)
- [Check attachment boundaries](#check-attachment-boundaries)
- [Attach the snapshot](#attach-the-snapshot)
- [Reference and explain the artifact](#reference-and-explain-the-artifact)
- [Verify portability](#verify-portability)
- [Handle updates and failures](#handle-updates-and-failures)

## Choose the evidence form

Prefer the smallest form that preserves the claim:

1. use an embedded evidence capsule for equations, short derivations, compact tables, protocols, and
   small text results;
2. attach a content-addressed snapshot for a small immutable proof report, JSON or CSV result,
   figure, PDF, protocol snapshot, or similar file whose exact bytes matter;
3. use a version-pinned external URL, DOI, arXiv ID, URN, software heritage ID, or repository commit
   for large, evolving, executable, or externally governed material.

Do not attach full datasets, model checkpoints, broad log trees, build directories, or frequently
regenerated intermediate output merely to make the vault self-contained.

## Check attachment boundaries

Attach only when the user explicitly requests it or vault policy authorizes the artifact class. Before
copying, confirm that the source:

- is a regular non-symlink file with a filename extension;
- contains no secret, credential, unnecessary personal data, or unauthorized proprietary material;
- is an immutable evidence snapshot rather than the evolving authoritative source;
- is small enough for the vault and its sync transport;
- can be opened as untrusted data without executing embedded instructions.

The source repository, manuscript, experiment system, or external archive remains authoritative for
its evolving artifact. The vault owns only the immutable bytes identified by the recorded hash.

## Attach the snapshot

Run:

```bash
python <skill>/scripts/attach_artifact.py \
  --vault <vault> \
  --file <evidence-file>
```

The command copies the bytes into:

```text
Knowledge/Artifacts/artifact-sha256-<64hex>/payload.<ext>
```

It prints a portable reference:

```text
vault:artifact:sha256:<64hex>
```

The copy is content-addressed, append-only, and idempotent. The command atomically publishes one
complete hash directory and never overwrites an existing artifact. A conflicting payload at the
expected hash path is an error.

## Reference and explain the artifact

Add the printed value to the candidate, paper, canonical, or proposal `source_refs`. An optional
locator may follow `#`, for example:

```yaml
source_refs:
  - vault:artifact:sha256:<64hex>#theorem-4
```

The surrounding evidence capsule must still state:

- what claim the artifact supports;
- the definitions, protocol, parameters, dataset or sample regime, and toolchain conditions that
  affect interpretation;
- the relevant result, uncertainty, limitations, and reproduction method;
- what remains authoritative in the source repository or external system.

The attachment is audit support, not a substitute for a self-contained evidence summary.

## Verify portability

Run the vault validator after adding the reference. It checks that exactly one matching payload
exists, that it is a regular non-symlink file, and that its SHA-256 matches the reference.

File replication remains a transport capability. Obsidian Sync and other transports may require
per-client settings for some extensions. When another replica must evaluate the artifact, confirm the
payload arrives there. If that cannot be guaranteed, keep the semantic evidence capsule sufficient
and use a stable external locator for the exact artifact.

## Handle updates and failures

Artifact identity is byte identity:

- unchanged bytes reuse the existing reference;
- changed bytes create a new hash and a new artifact file;
- never edit or replace a content-addressed payload in place;
- if attachment succeeds but the knowledge record update fails, retain the unreferenced artifact and
  either retry the record update or remove the artifact only after confirming that no record refers to
  it;
- an interrupted process may leave a `.artifact-*` temporary directory; remove it only after
  confirming that no attachment process is using it;
- the command streams bytes with bounded memory but enforces no universal size ceiling; vault policy
  or the operator must keep large material external;
- if validation reports a missing, duplicate, symlinked, or hash-mismatched payload, stop curation and
  repair the evidence boundary before promotion.
