---
id: paper-<stable-source-identifier>
title: <Paper title>
record_type: paper
status: source
citation_key: <author-year-short-title>
doi: <DOI or null>
arxiv: <arXiv identifier or null>
pmid: <PMID or null>
source_ref: <paper:doi:<DOI> | paper:arxiv:<identifier> | paper:pmid:<identifier> | stable HTTPS URI | embedded:claim-ledger>
source_uri: <stable external URI or null>
source_sha256: <64 lowercase hex characters or null; identity and integrity only>
tags:
  - <topic>
created: <ISO-8601 UTC timestamp>
updated: <ISO-8601 UTC timestamp>
---

# <Paper title>

## Citation

<Authors, title, venue, year, identifiers.>

## Research question

<What quantity, mechanism, or problem is studied?>

## Setting and assumptions

<Population/data, model class, theoretical assumptions, benchmark/protocol, and exclusions.>

## Method

<Core method, objective, architecture, derivation, or experimental design. Preserve or restate
important equations when they clarify the method; define symbols and assumptions nearby.>

## Main results

<Results with uncertainty and exact locators. Use equations or symbolic notation when they express
the result more precisely than prose, followed by a concise interpretation.>

## Claim ledger

| Claim | Locator | Type | Evidence/qualification |
|---|---|---|---|
| <claim> | p. X, §Y, Eq. Z / Fig. A / Table B | author claim | <qualification> |
| <interpretation> | based on <locators> | agent interpretation | inferred; explain why |

<Keep the ledger sufficient to understand the cited support on another replica. Never record the
originating local file path.>

## Limitations and failure regimes

<Author-stated limitations plus clearly separated agent criticism.>

## Relation to existing knowledge

<Where this supports, narrows, or conflicts with existing paper/canonical notes.>

## Durable candidate assessment

List each claim that received a durable candidate assessment. For each, state one of:

- `paper-only` — remains here;
- `candidate-created` — link the candidate;
- `deferred` — insufficient scope/evidence;
- `conflict` — link the affected canonical entry or proposal.

## Open questions

<Questions not answered by the paper.>

## Related

<Relevant wikilinks.>
