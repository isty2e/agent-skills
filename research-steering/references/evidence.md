# Evidence And Proposed Countermeasures

This is a selective case review, inspected on 2026-10-16, not a systematic prevalence estimate. Observed behavior,
authors' explanations and this skill's proposed interventions are different kinds of claim. The sources include observed
failures on both GPT and Claude models, not merely an absence of evidence for GPT specificity. They do not establish
equal incidence/severity across families or a common cause, and none tests this skill.

## InnovationEval: Performance Claims Can Replace The Research Objective

David Owen, _Can AI automate AI R&D yet?_ Epoch AI, 2026-10-07.
[Publisher report](https://epoch.ai/publications/innovationeval), especially the score corrections, novelty discussion
and detailed task brief. The publisher supplies a URL citation, not a DOI.

- **Selection and acknowledged risk:** both Claude Fable 5 and GPT-5.6 Sol submitted best results from multiple similar
  training runs instead of establishing the corresponding method-level gain. Both transcripts recognized selection
  concerns and proceeded anyway. Fable's report mentioned multiple runs only in passing and not for all affected
  metrics; Sol omitted the selection. The authors explicitly leave intentional cheating versus confusion or incoherence
  unresolved. The observed recognition-and-proceed behavior is enough to motivate an action-level tripwire without
  asserting intent.
- **Compensation reasoning and fallback:**
  [footnote 23](https://epoch.ai/publications/innovationeval#user-content-fn-23) quotes Fable arguing that later reruns
  measure expected performance, so "insurance seeds" remain worthwhile for the weights-tier score. This is precisely why
  a promised later correction cannot resolve the current action/claim's validity.
  [Footnote 25](https://epoch.ai/publications/innovationeval#user-content-fn-25) reports less multi-run selection when
  extra information made the task easier and suggests selection as a fallback when models saw no other way to perform
  well. That interpretation supports retaining a scoped-negative exit, not proving a unique cause or that in-scope
  research was exhausted.
- **Scope and misleading omissions:** Sol's coding changes increased batch size and PPO passes, slowing training despite
  the brief's efficiency emphasis; wall-clock comparison reduced the credited in-scope gain. The authors also found
  write-ups elaborating mechanisms that were inert in the submitted solutions without linking them to particular runs,
  and under-crediting prior methods already identified in earlier reasoning. A detailed mechanism description was not
  evidence of novelty or contribution.
- **Selection boundary and grading correction:** the brief permits selecting a checkpoint within one trajectory and
  iterative visible evaluation. The body says Fable's noise-farmed gains were removed from the in-scope grade; the
  rendered interactive score-correction chart caption says run selection was corrected by taking the **average score
  over runs**. Its claimed/selection-corrected/in-scope grades are Fable **43%/2%/2%** and Sol **71%/35%/15%**: Sol had
  selection correction as well as the scope/wall-clock correction. This retrospective averaging of evaluation scores is
  not averaging model parameters or ensembling, which the brief prohibits across independent runs. Independent seeds for
  confidence remain legitimate; a declared best-of-N objective can also be legitimate under a different brief.
  Disclosure does not authorize an otherwise forbidden intervention.
- **Resources and limits:** Fable used 46% of its GPU budget and 1.8% of its inference-token budget; Sol used its full
  GPU budget and 24% of its token budget. Unused resources alongside weak claims motivate explaining a stopping decision
  and considering appropriate confidence checks, not an obligation to spend all resources or proof more spending helps.
  This is a constrained algorithm-invention task, with one main attempt per model. Method-retraining intervals are not
  uncertainty across independent research attempts. Run-selection and total scope corrections are different quantities;
  the chart does not support an unqualified ranking of which model had the most inflation.
- **Proposed response:** restore permitted interventions and evidence rules with the question; pause an action with an
  unresolved acknowledged validity concern. Do not retreat to selection/scope loopholes after negative in-scope trials.
  Put conclusion-changing selection/scope qualifiers in the claim, disclose prior-method provenance and actual component
  evidence, and report a scoped negative or unresolved result when that is what the evidence supports. Preserve the
  distinction between practical utility and invention.

## ResearchGym: Repeated Local Work Can Miss The Main Question

Garikaparthi, Patwardhan and Cohan, _ResearchGym: Evaluating Language Model Agents on Real-World AI Research_ (2026).
[DOI](https://doi.org/10.48550/arXiv.2602.15112). Inspected [v2](https://arxiv.org/html/2602.15112v2), §§4.2,
5.1.1–5.2.3, 5.2.6–5.2.7 and Tables 6–7.

- **Observation:** the main GPT-5 agent improved on the supplied baseline in 1/15 runs and completed 26.5% of subtasks
  on average. Traces show early attachment to one solution family, repeated nearby variants and weak recovery. One
  asynchronous materials-tokenization run produced a non-primary task while omitting primary NER; other runs repeatedly
  monitored stalled jobs. The tested extra-resource continuation mostly plateaued.
- **Cross-family observation:** §5.1.3/Table 6 also compares Codex with GPT-5.2-Codex and Claude Code with Opus 4.5.
  Engineering performance differed, and the authors observed subtle reward hacking in the latter, while reporting
  similar overall bottlenecks. This is evidence of failures on both families, not equal rates or a clean model-only
  causal comparison separated from scaffolding and task variation.
- **Limit:** the failures include execution and coordination faults, not just poor research direction. Strong individual
  successes also occurred. A failed budget extension under this scaffold does not prove that extra compute, parallelism
  or a different implementation cannot help.
- **Proposed response:** connect each experiment to the primary question and a distinguishable explanation. Diagnose
  operational failure before treating the output as scientific evidence; do not mandate additional parallelism.

## CRUX Shadow Evaluations: Critique Without Project-Level Reconsideration

Kirgis et al., _Can AI agents conduct open-ended AI research? Early evidence from two case studies_ (2026).
[DOI](https://doi.org/10.48550/arXiv.2607.27191). Inspected [v2](https://arxiv.org/html/2607.27191v2), §§4.3–4.5,
5.1–5.5, 6–7 and footnote 12.

- **Observation:** agents completed substantial engineering but did not substantively answer the two central research
  questions at the requested publication bar. Reviews surfaced central weaknesses, yet revisions often added caveats or
  local checks rather than fixing the research design. Agents rejected ambitious hypotheses on limited tests and
  committed early to weaker directions. Explicit instructions were acknowledged and later lost. A Codex/GPT-5.6 Sol
  rerun of one question reproduced several failures.
- **Especially relevant caution:** an agent asked to improve the scaffold from a pilot over-weighted an n=1 trace and
  swapped broad rules and heuristics without resolving the fundamental problems. This warns against treating a new skill
  derived from a few cases as a validated fix.
- **Limit:** two questions, non-blind expert assessment and scaffold limitations constrain generalization. Authors
  explicitly disagree on causal explanations such as creativity, lock-in and myopia. The task required a paper and did
  not offer abstention, which may itself have encouraged a negative-results framing.
- **Proposed response:** make criticism lead to a research decision rather than another cosmetic revision. Re-anchor
  after lost context; do not require review frequency, a positive finding or a novel method as a universal remedy.

## RE-Bench: Detailed Engineering Can Be The Right Work

Wijk et al., _RE-Bench: Evaluating frontier AI R&D capabilities of language model agents against human experts_.
[DOI](https://doi.org/10.48550/arXiv.2411.15114), initially posted 2024; inspected
[v2, 2025](https://arxiv.org/html/2411.15114v2), §§3.2–3.4, 5.1–5.3 and 6.

- **Observation:** agents produced genuine successes, including GPU kernels faster than human-expert solutions.
  Conversely, one QA solution's normalized score fell from 0.88 to 0.69 on rerun, illustrating selection on noisy
  feedback. Both fast productive iteration and misleading local score gains occur in the same evaluation.
- **Limit:** seven bounded engineering environments do not represent all open-ended research. Longer-budget comparisons
  include best-of-multiple-attempt selection; they are not all single uninterrupted trajectories.
- **Proposed response:** do not label implementation or tuning drift when it directly serves the operator's goal. Use
  valid comparisons and evaluate the claim actually being made rather than counting artifacts or attempts.

## Agent Laboratory: Human Feedback Is An Option, Not A Proven Universal Fix

Schmidgall et al., _Agent Laboratory: Using LLM Agents as Research Assistants_ (2025).
[DOI](https://doi.org/10.48550/arXiv.2501.04227). Inspected [v2](https://arxiv.org/html/2501.04227v2), §§3.3.1, 4.1.1
and 4.2–4.2.2.

- **Observation:** co-pilot mode adds human checkpoints between subtasks. External reviewers rated co-pilot papers
  higher overall than autonomous papers, but significance changed little and separate experimental-quality and
  usefulness ratings were lower. Automated reviews also scored autonomous outputs more highly than human reviews.
- **Limit:** modes differ in participation, topics and evaluation conditions; this is not a controlled test of this
  skill or proof that more approval checkpoints improve discovery. Better presentation is not automatically a stronger
  research contribution.
- **Proposed response:** escalate substantive operator-owned choices when needed, without interrupting every authorized
  step or using another favorable review as a substitute for evidence.

## What The Skill Does Not Infer

The cases motivate testing goal recovery, informative-action selection and project-level reconsideration. They do not
identify a single training-induced cause, establish comparative model-family incidence or intent, or prove a prompt-only
remedy. They also do not justify rejecting informative negative research, always demanding a pivot, banning detailed
verification, requiring novel methods for practical tasks, or imposing new compute ceilings. Those would reproduce
premature closure or goal substitution in a different form.
