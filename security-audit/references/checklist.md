# Baseline checklist

Modified for security-audit. See [NOTICE](../NOTICE) for licensing and
upstream attribution.

For every in-scope file, walk this list. Each item ends in a disposition:
finding candidate, verified control, or inapplicable (one line why). Sibling
code (routes sharing a dispatcher, parsers sharing a helper, render paths
sharing a template) is always in scope for the item. The id in parentheses is
what a file receipt lists in `items`.

1. **Command/code injection** (`injection`). `subprocess`/`os.system`/`eval`/`exec`/template
   expansion. List form or shell string? Every argument traced to its source;
   flag values in option position are still one argv element — verify, don't assume.
2. **Authentication/authorization** (`authz`). Every entry point × anonymous/caller:
   what check runs, where, what it compares. Missing check + sensitive op = candidate.
3. **SSRF / egress** (`egress`). Every fetch of a non-fixed URL: who chooses the host,
   what guards (allowlists, link-local blocks, timeouts, size caps), what the
   response becomes (parsed, stored, reflected, error oracle).
4. **Path traversal** (`path`). Every filesystem path from input: allowlist regex,
   hash-derived names, `.name` stripping, symlink handling, suffix control.
5. **Deserialization/parsing** (`parsing`). Pickle/marshal/YAML/XML/plist/zip/office/PDF:
   entity expansion, decompression ratios, temp files, magic validation vs
   content sniffing, native-code parsers and their pinned versions.
6. **Render sinks** (`render`). Server templates and client JS: escaping order
   (escape-first vs markup-first), `innerHTML` sinks, `href`/`src` schemes,
   JSON-into-`<script>` breakouts, markdown-to-HTML subsets.
7. **Uploads** (`upload`). Size caps, type validation (magic vs extension), name
   sanitization, storage location, who re-parses them and as whom.
8. **Secrets** (`secrets`). Literals and context in code, config, docs, tests, examples.
   Purpose from format + usage. Placeholders and public keys are not secrets.
   Never use or transmit them; record reference + location + control.
9. **DoS / spend** (`dos`). Unbounded reads, missing timeouts, thread/process bombs,
   decompression/memory amplification, unauthenticated expensive operations
   (model calls, conversions, downloads) billed to whom.
10. **Model I/O as boundary** (`model-io`). Prompts carrying untrusted text: what tools the
    callee has, what constrains it (permission config, schema validation of
    replies), where replies flow (stored, rendered, published).
11. **Integrity/attribution** (`integrity`). Fingerprints, signatures, names, timestamps:
    who computes, who verifies, what forgery costs, what relies on it.
12. **Defaults and config** (`config`). Listen addresses, debug flags, CORS/Origin logic,
    permissive defaults, env-var overrides and who sets them.
