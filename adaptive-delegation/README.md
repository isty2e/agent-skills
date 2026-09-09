# Adaptive Delegation

Choose whether and how to delegate, then use observed cost, time, and parent repair to improve project-local choices.

## Setup

1. Make this directory available through your host's supported skill path.
2. Merge [assets/AGENTS.section.md](assets/AGENTS.section.md) into the project instructions your host reads. Do not
   replace existing instructions wholesale.
3. Use authorized local settings for models, tools, permissions, and budgets.
4. Keep current hints and compact observations in project-root `.agents/delegation.md`, or in the one alternative named
   by project instructions.

The skill description covers delegation decisions, dispatch, results, failures, cancellations, and experience review.
Direct execution remains valid; installing the skill creates no hook or write authority.

## Project-Local Learning

Record every launch attempt, not every direct operation. Start a pending observation before dispatch. If that would
violate a launch precondition such as a clean checkout, keep the fields in permitted session state and persist them
immediately after the attempt. Add returned statistics, one bounded lookup for missing fields, and the parent's verified
assessment. Missing values stay unknown with a reason; unchanged hints, failures, cancellations, and unused results
still count as experience.

Keep observations and current hints together without copying transcripts. Preserve human content, reconcile concurrent
edits, and consolidate only without losing covered IDs, failures, missingness, or contrary evidence. Recording does not
authorize commits, publication, permission changes, or weaker acceptance. If the approved destination is unavailable,
disclose the gap; the task result need not fail.

A separate authorized review may compare selected projects' records and propose shared-skill changes. Local recording
never publishes or promotes those changes automatically. Actual no-reminder behavior depends on the host; use the
[recording check](evaluations/recording.md) before relying on unattended capture.

## Documents

- [SKILL.md](SKILL.md): decision, execution, recording, assessment, and learning workflow.
- [references/model-starting-points.md](references/model-starting-points.md): conditional model-specific starting points.
- [references/measurement.md](references/measurement.md): fields, attribution, and comparisons.
- [references/tuning.md](references/tuning.md): project-file ownership, consolidation, hint updates, and shared review.
- [templates/delegation.md](templates/delegation.md): project hints and compact observations.
- [evaluations/recording.md](evaluations/recording.md): static contract and no-reminder host checks.

Read references only at the decision points named in the skill.

## License

[MIT](LICENSE).
