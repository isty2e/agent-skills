# Evaluate Durable-Knowledge Behavior

Compare models, harnesses, policies, or revisions without confounding the skill with the system under test.

## Hold The Fixture Constant

Use the same skill package, vault policy, sources, initial vault, prompts, operation boundaries, and validation commands.
Never fork the skill per model; record capability differences separately.

The fixture should discriminate:

- three papers with overlapping scopes;
- sessions yielding zero, one, and multiple durable findings;
- contextual facts that must route away;
- a self-contained project theorem whose exact proof remains repository-owned;
- a scoped zero-occurrence result preserving denominator, protocol, conditions, and uncertainty;
- mutable theorem/proof status that stays repository-owned;
- local outputs and ticket IDs requiring embedded evidence, authorized artifact attachment, or routing;
- valid, missing, duplicate, symlinked, and hash-mismatched artifacts;
- a user preference; near-duplicate owners; apparent and genuine conflicts;
- all candidate lifecycle states;
- a deferred/rejected near-duplicate whose reason should prevent low-value recapture.

## Run

1. Reset every run to the same fixture.
2. Run capture, paper ingest, recall, and curation separately.
3. Preserve generated files and validator output.
4. Score every axis below and count human corrections required for accepted output.
5. Repeat ambiguous cases before attributing differences to the model.

## Score

### Admission And Abstention

Captured claims must be reusable, decision-relevant, scoped, nontrivial, and not cheaply reconstructed as propositions;
reuse within one named research program counts. Treat transient status, implementation trivia, generic advice, and
unsupported universals as false positives. Require zero candidates when appropriate and deferral instead of invented
scope or evidence.

### Research-Forward Extraction

Prompt in a clean context:

```text
Find what should be preserved as knowledge from this research.
```

The agent must inventory theorems, mechanisms, empirical findings, scoped negatives, and conjectures before provenance
discipline or generic methodology, while separating repository-owned artifacts from vault-owned propositions. Failure
to extract substantive science is a failure.

Discriminating cases:

- repository-proved closure factorization -> central candidate with semantic kind;
- proved theorem with wording under revision -> its semantic kind plus `pending`, not `hypothesis`;
- genuinely unproved proposition -> pending `hypothesis`;
- zero activations under checkpoint/protocol -> scoped distinction between non-observation and impossibility, or
  hypothesis only for a genuinely unproved explanation; never a constraint merely because inference is limited;
- “127 Lean files pass” -> repository status.

For every release changing research routing, preserve a compact receipt with fixture, model/harness, source revision,
observed routing, deviations, reviewer verdict, and review status. See the
[baseline receipt](../../evaluations/research-forward-baseline.md). Written scenarios alone do not prove behavior.

### Activation

Test tasks with and without relevant prior knowledge or a durable finding. Useful opportunistic recall/capture must not
wait for explicit invocation, mechanically search every vault, report no-op checks, block primary work, or manufacture
weak candidates.

### Scope And Provenance

Check assumptions, benchmark, target, named subject, regime, and failure conditions. Context stripping must preserve
definitions, equations, protocols, and data conditions. Verify claims against precise pages, sections, equations,
figures, tables, embedded capsules, synced records, artifacts, or stable external resources.

### Replica Portability

Open records on a replica lacking the originating tree, tickets, and session. Claims and evidence must remain usable
from the record plus synced records/artifacts or stable locators. Local paths, bare filenames, tickets/issues, sessions,
machine labels, and hash-only unresolved refs fail. Required replicas must receive exactly one regular hash-valid
artifact payload; a local validator pass does not prove transport.

### Ownership, Conflict, And Recall

Confirm correct semantic owner, separation of distinct concepts, and no title-only identity. Distinguish scope mismatch
from contradiction and preserve genuine conflict. Compare downstream work with and without recall:

```text
utility delta = quality or efficiency with recall - quality or efficiency without recall
```

Measure both avoided rediscovery and anchoring to stale/provisional material. Measure human edits per accepted record;
page count is not quality.

### Lifecycle Integrity

Confirm:

- capture creates only `pending`; ordinary selection is one property edit;
- defer/reject requires substantive reason, savable before status in property editors;
- curation uses only `ready`; explicit named integration records `ready` before canonical work;
- same-proposition pending refinement preserves ID, creation, and filename;
- `ready` freezes claims; revision returns to pending and requires reselection;
- canonical state precedes integration metadata; integrated/contested candidates reference existing owners;
- deferred/rejected claim revision returns to pending; capture honors their reasons before recapture;
- proposal-only work leaves candidate state unchanged; delayed apply rejects stale `base_sha256`;
- same-owner curation serializes or surfaces conflict; desktop and headless clients see the same YAML;
- attachment is append-only and idempotent, and invalid payload states block promotion.

## Accept A Pilot

Accept only when admission is claim-justified rather than quota-driven; paper locators are reliable; contextual material
routes correctly without discarding project-originated science; capture, ingest, and recall never write canonical state;
conflicts and failures remain recoverable; records interoperate across tested models/clients; no accepted record depends
on machine-local context; and validation rejects structural errors while warning on known non-portable refs.

Report failures by axis with exact fixture, generated paths, validator output, and required human corrections.
