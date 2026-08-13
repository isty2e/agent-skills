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
- a project-originated theorem with self-contained assumptions and conclusion whose exact proof
  artifact remains repository-owned;
- a scoped zero-occurrence or negative experiment result that must preserve its denominator,
  protocol, operating conditions, and uncertainty;
- current theorem inventory or proof-status counts that must remain repository-owned;
- local experiment output and bare ticket identifiers that must be converted into embedded evidence,
  an explicitly authorized content-addressed artifact, or routed away rather than cited directly;
- valid, missing, duplicated, symlinked, and hash-mismatched `vault:artifact:sha256:` fixtures;
- a user preference that belongs in native memory;
- near-duplicate canonical owners;
- an apparent contradiction resolved by scope;
- a genuine unresolved conflict;
- candidates requiring pending, ready, deferred, rejected, integrated, and contested states;
- a deferred or rejected near-duplicate whose `review_reason` should prevent low-value recapture.

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
reconstructible as semantic propositions. Reuse within the same named research program counts. Count
transient status, implementation trivia, generic advice, and unsupported universal claims as false
positives.

### Research extraction priority

Run the forward prompt:

```text
Find what should be preserved as knowledge from this research.
```

The agent must inventory actual theorem families, mechanisms, empirical findings, scoped negative
results, and conjectures before offering provenance discipline, issue-tracking advice, or general
research methodology. It must distinguish repository-owned proof and experiment artifacts from
vault-owned semantic propositions. Treat an answer that extracts only workflow or epistemic
methodology while overlooking substantive scientific content as a failure.

Check these discriminating cases:

- a closure factorization theorem proved in one repository → central candidate with its semantic
  kind preserved;
- a proved theorem whose statement wording is still being refined → keep its semantic kind and use
  `pending`, not `hypothesis`;
- a genuinely unproved proposition → pending `hypothesis` candidate;
- zero witness activations under a specified checkpoint and protocol → scoped `distinction`
  between finite non-observation and impossibility, or `hypothesis` only when a genuinely unproved
  explanatory proposition is stated; do not label the observation a `constraint` merely because it
  limits inference;
- “the current Lean tree has 127 passing files” → repository status, not knowledge.

A written scenario is not evidence that an agent follows it. For each release that changes research
routing, run this prompt in a clean context and preserve a compact receipt containing the fixture,
model and harness, source revision, observed routing, deviations, reviewer verdict, and whether human
review occurred. The current baseline receipt is
[Research forward-evaluation baseline](../../evaluations/research-forward-baseline.md).

### Abstention quality

Check whether the system produces zero candidates when appropriate and defers rather than inventing
scope or evidence.

### Activation precision

Test substantive tasks with and without relevant prior knowledge or a genuinely durable finding.
Check whether the system recalls or considers capture at useful decision points without waiting for
an explicit request. Count mechanical vault searches, no-op check reports, blocked primary work, and
weak candidates created merely to demonstrate activation as failures.

### Scope preservation

Check assumptions, benchmark, target quantity, named research subject, operating regime, and failure
conditions for each theorem, paper, or experiment claim. Confirm that context stripping removed only
repository coordinates and temporary status, not definitions, equations, protocols, or data
conditions that give the proposition meaning.

### Provenance accuracy

Verify important claims against cited pages, sections, equations, figures, tables, embedded evidence
capsules, synced-vault records, or stable external resources.

### Replica portability

Open generated records from a fixture replica that lacks the originating working tree, local ticket
store, and harness session history. Confirm that each claim remains interpretable and its evidence can
be evaluated from the record itself plus synced-vault records, content-addressed artifacts, or stable
external locators. Count local paths, bare filenames, local ticket or issue names, session IDs,
machine-scoped artifact labels, and hash-only references with no resolvable payload as failures.

For attached evidence, confirm that every required replica receives the payload, exactly one file
matches the hash, and the file bytes validate. A local validator pass does not prove remote transport.

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
- humans can triage ordinary selection with one property edit and record a substantive
  `review_reason` when deferring or rejecting;
- property-by-property editors can save the reason before the status without creating an invalid
  intermediate record;
- curation processes only `ready` candidates;
- an explicit request to integrate a named non-applied candidate records `ready` before canonical
  curation rather than bypassing the lifecycle;
- pending candidates can be refined in place without changing their ID, creation time, or filename
  when they still represent the same proposed proposition;
- `ready` freezes the selected claim-bearing revision, and any later claim edit first returns the
  candidate to `pending` and requires a new selection;
- canonical state is written before integration status;
- integrated and contested candidates reference existing owners;
- deferred and rejected candidates have a non-empty reason; revising their claim-bearing content
  first returns them to `pending` so the old disposition does not silently govern a new revision;
- capture checks semantically similar deferred or rejected candidates and does not recreate one
  unless new evidence, scope, mechanism, or reuse value addresses the recorded reason;
- proposal-only work leaves candidate status unchanged;
- delayed proposal application fails when `base_sha256` no longer matches;
- concurrent curation of the same canonical owner is serialized or surfaces a reviewable conflict;
- desktop views and headless file reads observe the same YAML state;
- artifact attachment never overwrites existing bytes, retries identical bytes idempotently, and
  blocks promotion when a referenced payload is missing, duplicated, symlinked, or hash-mismatched.

## Accept an initial pilot

An initial pilot is acceptable when:

- candidate volume is justified claim by claim rather than by quota;
- paper claims retain reliable locators;
- contextual material routes to the correct owner without misclassifying project-originated
  scientific propositions as repository trivia;
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
