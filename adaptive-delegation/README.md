# Adaptive Delegation

Choose whether and how to delegate, collect statistics and parent feedback during ordinary work, and improve project
choices or later shared guidance from accumulated experience.

## Setup

1. Make this directory available through your host's supported skill path.
2. Merge [assets/AGENTS.section.md](assets/AGENTS.section.md) into the project instructions your host reads. Do not
   replace the existing instructions wholesale.
3. Use authorized local settings for models, tools, permissions, and budgets.
4. Keep hints and compact observations in project-root `.agents/delegation.md`. To use another file, name it in project
   instructions; do not maintain both. No separate log store is required.

The description lets the host select the skill before deciding whether to delegate. The supplied section makes the
procedure a standing instruction and authorizes project-local recording; no per-task logging request is required.
Consult selectively, not every tool call. Direct execution remains valid. Installing a skill alone installs no hooks and
does not establish project write authority.

## Project-Local Learning

The shared skill defines the procedure. `.agents/delegation.md` holds project choices and compact experience. Adopting
the supplied section in project instructions allows the parent agent to create and update that file within those
instructions and repository write policy.

Before the first delegated run, initialize the authorized file from [templates/delegation.md](templates/delegation.md)
with a pending observation; do not wait for a useful lesson. If that write would violate an enforced launch precondition
such as a clean source checkout, retain the pending fields in permitted session state, launch once, then persist the
observation immediately with the returned attempt ID or failure. Never weaken the launch precondition to record early.
Extend existing files without replacing human content. After results, failures, or cancellations, retrieve available
per-run statistics from exposed sources. After verification, add the parent's assessment and repair burden to the same
observation. Keeping a hint unchanged does not waive recording.

Keep current choices, compact observations, counterevidence, recheck conditions, and previous choices—not transcripts.
Reconcile pending observations on the next skill activation. Tracking, commits, and sharing need repository authority.
If the approved destination is unwritable or authority absent, disclose the gap rather than choosing another path. Keep
permitted session evidence; missing telemetry need not block the work result.

This guidance does not guarantee host activation, complete capture, or collection after session termination. Check the
[recording scenarios](evaluations/recording.md) in the actual host before relying on unattended use.

Local adjustments cover direct-versus-delegated work, task partition, handoff, context, and allowed execution settings.
Changing the shared skill, governing instructions, permissions, budgets, or acceptance criteria requires separate
authorization. The guide does not establish that a routing choice improves quality, latency, or cost; evaluate those
outcomes in the adopting project.

## Later Skill Improvement

In a separate authorized review, gather the selected projects' `.agents/delegation.md` files. Use observations and
hints, including failures, missing measurements, parent repair, and contrary evidence. Distinguish project-specific
lessons from candidates for common guidance; propose and review skill/reference changes, then check them on subsequent
work. Local recording does not automatically publish data or edit shared instructions. See
[tuning.md](references/tuning.md#4-review-project-experience-for-shared-guidance).

## Documents

- [SKILL.md](SKILL.md): candidate selection, execution settings, handoff and recovery, assessment, and a first-run
  example.
- [references/model-starting-points.md](references/model-starting-points.md): conditional model-specific starts when
  local evidence is insufficient.
- [references/measurement.md](references/measurement.md): active collection, compact records, and cost/time attribution.
- [references/tuning.md](references/tuning.md): project-file ownership, consolidation, hint updates, and shared review.
- [templates/delegation.md](templates/delegation.md): current hints and compact observations.
- [evaluations/recording.md](evaluations/recording.md): contract scenarios and a no-reminder host check, not measured
  compliance results.

Read references at the decision points named in the skill rather than adding all of them to the routine prompt.

## License

[MIT](LICENSE).
