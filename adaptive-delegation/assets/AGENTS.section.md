## Delegation

At substantive task decomposition, consider independent research, verification, or implementation work. When a candidate
exists, before dispatch, on returned/failed/cancelled work, or during experience review, load and apply
`adaptive-delegation` without another request. Direct execution remains valid; activation is not a spawn quota.

Use project-root `.agents/delegation.md` unless these instructions name another file. The parent may create/update it
within repository write policy without per-run reapproval. Preserve human hints and legacy records; never silently
change destinations. Use the skill's recorder for its managed block, not agent-written JSON or a new report.

- Compare delegation's whole-task burden with direct work. The parent retains scope, decisions, checking, integration,
  and acceptance; respect existing parent-only duties, permissions, and budgets.
- Before a selected launch, call `prepare` with existing task text, known requested settings, and the expected benefit.
  If writing would break a launch precondition, retain inputs and persist immediately after the attempt instead.
- Execute through the native harness. The parent calls `record-run` for outcomes and available statistics, then `assess`
  after verification/repair. No child-side self-accounting, automatic host discovery, or repeated metric searches.
- Keep output verdicts distinct from whole-delegation usefulness, including retries and parent burden. Add usefulness to
  the final `assess` call; unknown is valid and no savings are inferred. Use only a useful short note. Keep
  failed/cancelled attempts, late metrics, and pending assessments visible; recording needs neither a new lesson nor a
  changed hint.
- For seriously considered but rejected delegation, call `record-direct` with task/type and a short reason. Export
  includes these representative choices; do not log routine direct work or invent alternative costs.
- Before reporting, reconcile known attempts and confirm persistence or disclose the gap. Never let telemetry collection
  grow into a separate investigation or block delivery of the work result.
- Review hints later when evidence warrants it. Export selected records only to an approved local destination; commits,
  remote publication, shared-skill updates, permission changes, and weaker acceptance need separate authority.
