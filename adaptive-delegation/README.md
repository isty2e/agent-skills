# Adaptive Delegation

Choose whether and how to delegate to subagents, then use observed results to improve project-local routing.

## Setup

1. Make this directory available through your host's supported skill path.
2. Merge [assets/AGENTS.section.md](assets/AGENTS.section.md) into the project instructions your host reads. Do not
   replace the existing instructions wholesale.
3. Use authorized local settings for models, tools, permissions, and budgets.
4. Keep local hints in `.agents/delegation.md` at the project root. To use another file, name it in project
   instructions; do not maintain both.

Load the skill when substantive task decomposition reveals an independent delegation candidate, when assessing returned
work, or when tuning delegation. Compare delegation with direct execution; loading the skill does not require spawning.

## Project-Local Learning

The shared skill defines the procedure. `.agents/delegation.md` holds learned project choices. Adopting the supplied
section in project instructions allows the parent agent to create and update that file within those instructions and
repository write policy.

Start from [templates/delegation.md](templates/delegation.md) when there is a useful observation to retain. Do not
replace an existing file with the template. Keep current choices, scope, evidence and counterevidence, recheck
conditions, and the previous choice for rollback—not a full execution log. File tracking, commits, and sharing require
the corresponding repository policy and authority.

Before execution, state the primary expected benefit and acceptable extra burden. Afterward, assess the evidence and
parent repair effort, then keep, adjust, or revert the local choice. Recheck changes on the next applicable task; weak
evidence does not require a change. If no local file and update authority are approved, use permitted session-local
notes and disclose the persistence limit.

Local adjustments cover direct-versus-delegated work, task partition, handoff, context, and allowed execution settings.
Changing the shared skill, governing instructions, permissions, budgets, or acceptance criteria requires separate
authorization. The guide does not establish that a routing choice improves quality, latency, or cost; evaluate those
outcomes in the adopting project.

## Documents

- [SKILL.md](SKILL.md): candidate selection, execution settings, handoff and recovery, assessment, and a first-run
  example.
- [references/model-starting-points.md](references/model-starting-points.md): conditional model-specific starts when
  local evidence is insufficient.
- [references/measurement.md](references/measurement.md): routine records, comparison detail, and cost/time attribution.
- [references/tuning.md](references/tuning.md): diagnosis, project hint updates, rechecks, and rollback.
- [templates/delegation.md](templates/delegation.md): a starting format for project-local hints.

Read references at the decision points named in the skill rather than adding all of them to the routine prompt.

## License

[MIT](LICENSE).
