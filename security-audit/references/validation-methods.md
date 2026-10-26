# Validation methods and confidence

Modified for security-audit. See [NOTICE](../NOTICE) for licensing and
upstream attribution.

Choose evidence that tests the claimed boundary and resolves material
uncertainty. These methods are not a ranking. Runtime checks are appropriate
when authorized, feasible and proportionate; do not require a build or live
deployment when source evidence settles the claim. Record what each method
establishes and what it cannot establish. The id in parentheses is the
`validation.method` value in `candidates.json`. Every method that executes
target code runs under `references/poc-policy.md`.

- **Crash reproduction** (`crash`): reproduce a claimed crash or resource
  failure through the original code, distinguishing application behavior from
  a harness or resource-limit failure. No crash is required for non-crash claims.
- **Sanitizer / valgrind** (`sanitizer`): test a memory-safety claim when the
  build supports the instrumentation and its result resolves uncertainty.
- **Debugger trace** (`debugger`): use non-interactive gdb/lldb when observing
  the actual runtime chain would settle a missing hop.
- **Focused test** (`test`): exercise the relevant control and operation,
  with a legitimate-behavior control where useful, in a disposable copy.
- **Realistic interface** (`interface`): use the actual HTTP, CLI, parser, RPC,
  plugin hook or package API to test reachability and the claimed consequence.
- **Static trace** (`static`): establish the assessment tuple below from
  source. This can be decisive evidence, not merely a fallback when tools fail.

## Assessment tuple

For every candidate: `source`, `control`, `sink`, `reachable path`, `boundary`,
`counterevidence`, `proof gaps`. A dependency's presence, a string match, or a
partial call chain is not an assessment.

Evidence search order: supplied locations → manifests/deploy config/generated
boundaries → affected functions/routes/parsers → nearby guards → product
surface evidence (policy, docs, tests, comments).

## Boundary and surface classification

Before calling a static path security-relevant, classify:

- **product surface**: hosted service, library API, CLI, local UI, MCP/tooling,
  plugin hook, example/fixture, docs, generated, vendored, unknown.
- **source trust**: untrusted user, tenant-controlled, remote, trusted
  operator, trusted developer config, local-only, intentionally code-executing
  extension point, unknown.
- **policy basis**: repository policy, product docs, deploy/config, package
  metadata, comment, threat model, unknown.

Check whether untrusted input can reach the bug on a supported surface.

## Confidence in the complete finding

- `high`: exact source/control/sink path, stated preconditions, boundary
  evidence, no material unresolved counterevidence.
- `medium`: plausible path with direct evidence but incomplete call chain,
  config, version, deployment, or boundary evidence.
- `low`: weak or indirect support, significant ambiguity, missing context.

A crash establishes the observed crash, not every claimed security consequence.
Instrumentation and debugger output likewise prove only their observations.
A complete static argument can support high confidence; a reproduced crash
with an uncertain attacker path or impact cannot bypass those proof gaps.
Do not assign fixed numeric confidence from the method or tool name. Decisive
counterevidence changes the disposition rather than becoming a method score.

## Instance preservation

- Validate each candidate instance independently; do not collapse siblings into
  one finding because they share a family.
- A representative PoC may support a family, but every sibling still needs its
  own file:line, source, closest control, sink, disposition, and counterevidence.
- Expand broad family candidates into child rows before deciding survival.
- Suppress a sibling only with the specific control that makes that exact
  instance safe.

## Class-specific proof tuples

- **authz/tenant/state change**: attacker path + missing/wrong guard +
  protected object/state transition.
- **injection/traversal/upload/redirect**: attacker bytes + sanitizer/
  canonicalization/allowlist result + dangerous sink in context.
- **XSS/template/SSTI**: attacker value + escaping/template context +
  execution sink.
- **deserialization/codec**: attacker bytes + unsafe loader/registered handler +
  object-construction or execution effect.
- **SSRF/callback**: attacker destination + destination-control bypass +
  network/read/side-effect impact. An intended feature is not suppression
  evidence; an optional or empty filter is not proof of safety.
- **path/archive/resource**: attacker path + allowlist/decode/canonicalization/
  selection + filesystem effect. Containment must run before extraction/write.
- **auth/token/assertion**: attacker token/state + validator semantics +
  validated-vs-consumed mismatch or missing binding.
- **parser/object model**: untrusted structure + unchecked conversion,
  recursion, numeric parse, allocation, or iteration + crash/DoS/confusion/
  control bypass.
- **secret exposure**: credential material + reader boundary + missing
  protection; do not require execution.

## Hard rules

- Do not imply runtime validation that did not happen.
- Do not treat a setup/build failure as counterevidence; record the proof gap.
- Prefer a disposable copy for builds and harnesses; keep the target read-only.
- Do not abandon a long check with signs of progress without inspecting status.
- Keep commands bounded, non-interactive, and scoped to the candidate.
