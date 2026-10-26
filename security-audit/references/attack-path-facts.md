# Attack-path facts (adapted)

Modified for security-audit. See [NOTICE](../NOTICE) for licensing and
upstream attribution.

Gather in structured form during analysis; render as readable bullets or short
labeled paragraphs, never a raw schema dump. Cover every item; each carries its
evidence or an explicit unknown:

- **Assumptions.** What the path takes for granted.
- **Context.** Self-only or a crossed boundary, with repository evidence.
- **In-scope status.** Whether the component is in scope, and why.
- **Exposure.** Public/internal/admin-only/localhost-only/unknown; ports and
  ingress when evidenced.
- **Identity.** Service account or managed identity; effective privileges.
- **Cross-boundary behavior.** Whether the crossing is verified, with the chain.
- **Vector.** `remote`, `local_network`, `localhost`, `none`, or `unknown`,
  with evidence.
- **Preconditions.** What the attacker needs; plausible, unlikely,
  unachievable, or unknown — with evidence.
- **Attacker input control.** Yes, plausible, no, or unknown — with evidence.
- **Category.** Bug family (CWE-level).
- **Mitigations present.** Controls already in the path.
- **Auth scope.** Public, internal-only, admin-only, or unknown — with evidence.
- **Impact surface.** Build, runtime, data, identity, network, or other.
- **Target reach.** Single service, fleet, or unknown.
- **Secrets references.** Type and reference chain when present.
- **Counterevidence.** Strongest conflicting evidence and why it does or does
  not dispose of the finding.
- **Blindspots.** What was not checked.
- **Confidence.** What would raise or lower it.

Then render: the factual path as numbered attacker steps; the reachability and
scoping logic; the strongest counterevidence; the final policy decision
(`report` or `ignore`) after suppression; the impact × likelihood reasoning.
Keep the full narrative out — concise, inspectable, no speculation padding.
