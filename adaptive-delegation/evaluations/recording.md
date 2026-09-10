# Recording And Learning Check

This is a review and host-test protocol, not a compliance result or permission for paid comparison runs.

## Contract Review

Check the skill, project section, references, and template together:

- Direct work remains valid; record launch attempts and representative delegation decisions kept with the parent, not
  routine direct work.
- An attempt starts pending before dispatch, except when an enforced launch precondition requires immediate post-attempt
  persistence from permitted session state.
- Results, failures, cancellations, retries, fallbacks, and unused output retain their identities and known usage.
- One bounded exposed lookup may fill missing fields; unknown, unavailable, failed, unattributable, and skipped
  collection are not zero.
- Parent review records `output_quality` for the original artifact and `output_use` for actual handling. Neither means
  final task acceptance; finding count or silence does not establish quality, and unknown recall remains unknown.
- Missing authority or a failed write is disclosed without relocation or weaker acceptance.
- Cooperating recorder writes serialize and preserve surrounding content; conflicts fail rather than overwrite. Do not
  hand-edit the managed block. Consolidate human summaries without deleting attempt evidence.
- Shared guidance changes require a separate authorized review; local records are not published automatically.

## Local Script Check

Run `python -m unittest discover -s tests -v` from the skill directory. Tests use synthetic temporary records, not model
calls or private telemetry. Check the stage-input schemas, retries, late metrics, corrections, missing values,
preservation of surrounding Markdown, and JSON export. This does not test network filesystems, every operating system,
or concurrent non-cooperating editors.

## No-Reminder Host Check

1. In an approved test project, adopt the skill and project section; record host and skill revisions.
2. Give an ordinary substantive task without mentioning delegation, telemetry, or logging. Confirm that the skill is
   considered; direct execution is allowed but does not test post-launch recording.
3. Run an ordinary delegated task. Check that `prepare`, `record-run`, and `assess` were called without a reminder, and
   compare native run IDs and supplied metrics to the staged record. No child-side collector is required. Reuse existing
   failures or cancellations rather than manufacturing costly ones.
4. In a fresh session, check that hint applicability matches the actual settings or handoff, including a scoped reason
   when a hint is not applied, and that the new outcome is recorded. Reconcile unfinished observations without
   relaunching work to recreate metrics.
5. Report activation, collection, persistence, application, and assessment separately as observed, not observed, or not
   exercised. Claim complete capture only when an authoritative runtime inventory supports it.

In a separate authorized batch, check that `export` includes failures and incomplete records, produces identical JSON
fields, and does not invoke Git, a server, or a prose-generation step. Track recording overhead separately if
observable; do not run a new timing investigation merely to complete a record.

Static review and token counts do not prove host behavior. The skill installs no hook and cannot guarantee capture after
session termination.
