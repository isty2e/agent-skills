# Evaluate durable-knowledge behavior

Use this guide to compare models, harnesses, policies, or workflow revisions without confounding the
skill package with the system under test.

## Contents

- [Hold the fixture constant](#hold-the-fixture-constant)
- [Build a small evaluation fixture](#build-a-small-evaluation-fixture)
- [Run the evaluation](#run-the-evaluation)
- [Score the behavior](#score-the-behavior)
- [Accept an initial pilot](#accept-an-initial-pilot)

## Hold the fixture constant

Use the same:

- skill package and vault policy;
- source material;
- initial vault fixture;
- prompts and operation boundaries;
- validation commands.

Do not fork the skill per model. Record capability differences separately.

## Build a small evaluation fixture

Include:

- three papers with overlapping but nonidentical scopes;
- substantive sessions containing zero, one, and multiple durable findings;
- repository-local facts that should be routed away from central knowledge;
- local experiment output and bare ticket identifiers that must be converted into embedded evidence
  or routed away rather than cited directly;
- a user preference that belongs in native memory;
- near-duplicate canonical owners;
- an apparent contradiction resolved by scope;
- a genuine unresolved conflict;
- candidates requiring pending, ready, deferred, rejected, integrated, and contested states.

## Run the evaluation

1. Reset each run to the same fixture.
2. Execute capture, paper ingest, recall, and curation as separate operations.
3. Preserve all generated files and validation output.
4. Compare runs on the axes below.
5. Measure human corrections required for accepted output.
6. Repeat ambiguous cases before attributing a difference to the model.

## Score the behavior

### Admission precision

Check whether captured claims are reusable, decision-relevant, scoped, nontrivial, and not cheaply
reconstructible. Count transient status, implementation trivia, generic advice, and unsupported
universal claims as false positives.

### Abstention quality

Check whether the system produces zero candidates when appropriate and defers rather than inventing
scope or evidence.

### Activation precision

Test substantive tasks with and without relevant prior knowledge or a genuinely durable finding.
Check whether the system recalls or considers capture at useful decision points without waiting for
an explicit request. Count mechanical vault searches, no-op check reports, blocked primary work, and
weak candidates created merely to demonstrate activation as failures.

### Scope preservation

Check assumptions, benchmark, target quantity, operating regime, and failure conditions for each
paper or experiment claim.

### Provenance accuracy

Verify important claims against cited pages, sections, equations, figures, tables, embedded evidence
capsules, synced-vault records, or stable external resources.

### Replica portability

Open generated records from a fixture replica that lacks the originating working tree, local ticket
store, and harness session history. Confirm that each claim remains interpretable and its evidence can
be evaluated from the record itself plus synced-vault IDs or stable external locators. Count local
paths, bare filenames, local ticket or issue names, session IDs, machine-scoped artifact labels, and
hash-only source references as failures.

### Semantic owner resolution

Check whether the system merges into the correct owner, keeps distinct concepts separate, and avoids
title-only identity decisions.

### Conflict handling

Check whether it distinguishes scope differences from genuine contradiction and preserves unresolved
evidence.

### Recall utility

Compare a downstream task with and without recall:

```text
utility delta = quality or task efficiency with recall
                − quality or task efficiency without recall
```

Check both rediscovery avoided and anchoring to stale or provisional material.

### Review burden

Measure human edits per accepted candidate, paper note, and canonical integration. Page count alone is
not a quality signal.

### Lifecycle integrity

Check that:

- capture creates only `pending`;
- humans can triage with one property edit;
- curation processes only `ready` candidates;
- an explicit request to integrate a named non-applied candidate records `ready` before canonical
  curation rather than bypassing the lifecycle;
- canonical state is written before integration status;
- integrated and contested candidates reference existing owners;
- proposal-only work leaves candidate status unchanged;
- delayed proposal application fails when `base_sha256` no longer matches;
- concurrent curation of the same canonical owner is serialized or surfaces a reviewable conflict;
- desktop views and headless file reads observe the same YAML state.

## Accept an initial pilot

An initial pilot is acceptable when:

- candidate volume is justified claim by claim rather than by quota;
- paper claims retain reliable locators;
- contextual material routes to the correct owner;
- no canonical writes occur during capture, paper ingest, or recall;
- conflicts and partial failures preserve recoverable state;
- notes remain interoperable across tested models and clients;
- no accepted record depends on an originating machine's paths, local tickets, session history, or
  machine-scoped artifact labels;
- structural validation rejects duplicate fields, scalar/sequence shape errors, and empty or
  placeholder knowledge-bearing sequences without manual schema repair, and reports known
  non-portable source references.

Report failures by axis and include the exact fixture, generated paths, validator output, and required
human corrections.
