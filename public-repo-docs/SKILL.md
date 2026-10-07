---
name: public-repo-docs
description: >-
  Draft or audit public package/repository docs: READMEs, installation, usage. Check each paragraph and sentence for
  reader value, public support, instruction accuracy, and coherent organization without imposing fixed headings or
  extra files.
license: MIT
---

# Public Repository Documentation

Identify what package users, adopters, or contributors need to understand, decide, or do. Inspect the requested document
and enough package, workflow, and linked-doc context to verify claims. Report findings by default; edit on request.
Exclude code comments, docstrings, agent instructions, private plans, and PR narratives.

## Keep Only Reader-Relevant Content

For each paragraph, then each sentence, ask what reader question it answers and whether it belongs here. Keep actionable
setup, usage, current behavior and limits, compatibility, security warnings, troubleshooting, and migration details
that affect real decisions or tasks. Cut repetition and development-only material: diaries, review chronology, internal
test reports, abandoned options, and agent bookkeeping. Preserve current constraints regardless of origin; put needed
user-visible history in release notes or changelogs, not README diaries.

Check behavior, availability, version, and installation claims against public code, published artifacts, primary docs,
or source/artifacts included in the same public change as the docs. New user-facing promises need maintainer authority,
not inference from internal work. Never mention paths, names, or contents of local-only/private files or directories,
non-public tracker IDs, unrelated private evidence, or session details. Reader-relevant public repository paths and
shipped examples may be named. Link public issues only to explain reader-relevant behavior or changes. For current-behavior
claims backed only by unrelated private evidence, omit them or obtain public support before publication; never disguise
the gap with a citation.

## Organize By Reader Intent

Distinguish learning through an exercise, accomplishing a task, looking up facts, and understanding why something works.
A README directs readers to these paths and need not serve only one purpose. Keep section purposes clear and prerequisites
before dependent steps. Separate mixed purposes only for better navigation; choose headings and file boundaries to suit
the content, not a prescribed taxonomy. Link canonical details instead of repeating them across pages.

Lead a README with what the package/project is, why it is useful, and a short installation path.
Provide copyable commands for a supported environment; state necessary prerequisites and distinguish alternatives.
Verify package names, commands, flags, and paths against the supported distribution; never present placeholders as
runnable. Non-installable repositories need a first useful entry point instead. A small first-use example and
detailed-guide links may follow; avoid long catalogs or development history before installation. Put safety-critical
warnings before affected commands.

## Check And Report

Verify consequential commands and claims against supported package/docs. In audits, check consequential links in the
requested document, including existing ones; for edits without an audit, check changed links. Run examples when safe
and practical; distinguish checked from unexercised examples. Add no prose-assertion tests or scripts solely to police
wording.

In audits, report actionable issues with location, reader impact, and a proposed deletion, move, or rewrite, not
per-sentence scores. In edits, preserve supported contracts and state material facts left unverified.
