---
name: research-steering
description: >-
  Guide autonomous empirical research at start, batch interpretation and before milestone/final reports or submissions.
  Also use after context loss or handoff, when evidence challenges the plan, before material evaluation, baseline or
  resource changes, or after unexpected coverage or failure-handling shifts. Choose informative actions, preserve
  evaluation boundaries and avoid drift, local fixation or misleading progress claims. Not a routine coding checklist.
---

# Research Steering

Steer toward the operator's question without replacing domain judgment. Preserve governing experiment-design,
task-management, approval, correctness, reproducibility and verification rules; this skill replaces none of them.

## Triggers

Use a brief pass at research start, when interpreting a coherent experiment batch, and before a substantive milestone or
final report/submission. Also revisit before materially changing evaluation definitions, baselines or resource
conditions that affect the question or comparison. Revisit when new evidence challenges the plan or these signals
appear:

- Progress is measured by completed runs, code, reviews or reports rather than the requested outcome.
- A result is repeatedly answered with more tuning or training without checking the explanation it bears on.
- Core critiques produce cosmetic replies or minor repairs without a decision about the underlying experiment.
- The metric, cohort, comparison or research question changes to accommodate the results, or evaluated cases, failure
  handling or coverage shift unexpectedly.
- Apparent method gains mainly come from selecting seeds, runs or configurations, tuning or out-of-scope changes.
- Scores repeatedly used to guide design are presented as independent confirmation.
- Plans proceed despite acknowledged unresolved scope or selection-validity concerns.
- Context loss or a handoff leaves the latest local TODO disconnected from the objective.

No timers or per-command ritual. Reuse unchanged decisions/checks, but check the actual action or submitted claim. Long
implementation/verification is not itself drift. Keep the pass decision-sized: no new essay, hypothesis inventory or
review campaign; once supported and required gates satisfied, act or report.

## Steering Pass

1. **Restore the question and brief.** Read the owning task, accepted decisions and relevant results. Recover the
   target, comparison, permitted interventions and evidence/selection rules, including allowed selection signals and any
   algorithm-only or tuning restrictions. Do not import another benchmark's restrictions. Distinguish practical utility,
   novelty, publication quality and deployment readiness. Correct stale derived plans from their owner, not vice versa.
2. **Assess progress.** When evaluating an intervention, check that it actually ran in the evaluated path before
   treating the outcome as evidence for or against its mechanism; execution alone does not establish an effect. Before
   crediting a method gain, check method changes, selection and tuning history, scope, comparison conditions, evaluated
   cases/coverage and measurement noise. Include research selection, design or tuning decisions informed by observed
   evaluation results, regardless of pilot/debug labels or executor; keep history dimensions separate, not one N. A
   selected best run is not expected method performance; repeatedly consulted scores are development-conditioned, not
   independent confirmation by themselves.

   Check the comparison conditions required by the question/claim, evaluated identities/weights and contractual handling
   of failures and missingness; report coverage and failures rather than silently dropping cases. Reuse baseline
   evidence only while its relevant inputs and evaluation semantics remain applicable. Separate observations from
   explanations; leave unresolved attribution or confounding explicit rather than inventing a cause. Before calling an
   approach ineffective, distinguish method limitations from implementation faults, invalid comparisons, data or
   representation limits, power and tested conditions. Informative negatives are progress; better scores and finished
   artifacts need not be.

3. **Choose the next action.** Compare continuation with a diagnostic or a materially different explanation or approach
   where evidence makes one plausible. State the uncertainty addressed and how plausible outcomes would change the next
   decision. Prefer decision-relevant information, not predictable success, cheapness or novelty. For unresolved claim
   reliability, prioritize an appropriate permitted check over more variants, or narrow the claim: independent seeds or
   a valid held-out check, not an automatic new split or changed evaluation contract. Necessary engineering and
   verification may justify themselves through the accepted result or guarantee they establish.
4. **Decide and act.** Continue, repair the experiment, explore differently or report. Stay within authority; ask only
   for unresolved operator-owned choices or required approval. Record changed decisions with the existing owner and link
   evidence there, including candidate-screening history from already-authorized delegation. Do not create a second
   ledger or reopen reviews without changed inputs. Keep unresolved mechanisms unknown rather than inventing causal
   stories. If tested in-scope ideas fail, report the scoped negative or unresolved result; do not salvage scores
   through selection or scope loopholes or claim all possible approaches failed.

   **Recognized-risk tripwire:** pause an action with an acknowledged unresolved scope/selection concern. Resolve it
   only through permission for the disputed action/claim in the actual brief/evaluation contract or an authorized
   operator decision, or an actual change removing the identified effect from the action/claim. Remaining actions must
   still be permitted: revising a claim grants no authority. Promised later checks, another scoring tier, compensation
   reasoning or disclosure alone do not resolve the concern. Otherwise seek the needed decision or do not proceed;
   continue independent authorized work where possible.

## Guardrails

- **Exploration:** do not force a pivot after a failure quota or broadly reject an approach from an underpowered probe.
  Scope negatives and apply comparable evidence standards to incumbents/alternatives. Known baselines may answer utility
  questions; novelty is not the default. Honest negatives remain reportable even below a requested success bar.
- **Stopping:** with substantial approved resources left, state why you are stopping: the question is answered, evidence
  supports the scoped claim, a plausible next action lacks justification or feasibility, or a constraint requires
  stopping. No proof about every possible future experiment is required. Unused resources need not be spent, but needed
  confidence checks must not be skipped. Respect explicit limits without inventing budgets or constraints. Resource
  limits stop execution, not scientific possibility; report unresolved questions.
- **Critique:** a reviewer's accept/reject score is not itself scientific evidence or approval to change goals, cohort,
  criteria or budget. Answer valid criticism with evidence, redesign or a transparent scoped/unresolved claim, not
  cosmetic wording.
- **Process:** honor governing design, correctness, reproducibility and approval rules. Reuse applicable checks;
  slowness is no waiver. Keep the existing state owner. Do not multiply receipts, automatic reviewers, routine
  re-approval requests, context resets, or changes to tooling or instructions. Each such intervention needs its own
  authority and evidence.

## Reporting And Limits

Lead with **what was learned, what it does not establish and the next decision**. Put conclusion-changing qualifiers in
the headline claim; group other limitations without obscuring it. For actual performance/novelty/causal claims, disclose
relevant:

- selection history: known run/seed/config counts, repeated split queries and evaluation-guided design changes,
  including metric-informed pilot/debug or delegated screening; keep dimensions distinct and state gaps. Distinguish
  checkpoint selection, best-of-N and aggregates;
- brief/evaluation departures, claim-relevant resource/tuning and pipeline differences, baseline reuse validity,
  evaluated-set identity/weights, coverage and failure/missingness handling;
- prior methods informing the idea, without implying independent novelty;
- active submitted components and ablation evidence: verified execution in the evaluated path, supported effects,
  measured nulls, demonstrably inert components and untested/unisolated effects. Execution alone does not establish
  contribution; a null alone does not prove inertness. Descriptions do not establish contribution.

State decision-relevant unknowns and limit claims rather than conceal/invent them. Link evidence; separate utility,
novelty, uncertainty and resource constraints when decision-relevant.

[Case evidence](references/evidence.md) motivates this skill; neither efficacy nor GPT-specific causality is
established. [Review scenarios](references/scenarios.md) inspect interpretation, not efficacy. Consult these when
revising/evaluating the skill, not before every experiment.
