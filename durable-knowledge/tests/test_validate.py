import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_SKILL_ROOT = Path(__file__).resolve().parents[1]
_VALIDATOR = _SKILL_ROOT / "scripts/validate.py"


class ValidateFrontmatterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.vault = Path(self.temporary_directory.name)
        (self.vault / "_durable-knowledge").mkdir()
        (self.vault / "_durable-knowledge/ROOT.md").write_text(
            "durable-knowledge-vault-v1\n", encoding="utf-8"
        )
        (self.vault / "Knowledge/Candidates").mkdir(parents=True)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def validate_candidate(
        self,
        scope_yaml: str,
        *,
        status_yaml: str = " pending",
        source_ref: str = "embedded:evidence-1",
        title_line: str = "title: Example candidate\n",
        heading: str = "Example candidate",
        extra: str = "",
    ) -> subprocess.CompletedProcess[str]:
        candidate = self.vault / "Knowledge/Candidates/example.md"
        candidate.write_text(
            f"""---
id: candidate-20260313t142233123456z-example
{title_line}record_type: candidate
knowledge_kind: method
status:{status_yaml}
evidence_state: observed
canonical_id: null
scope:{scope_yaml}
assumptions:
  - example assumption
invalidation_conditions:
  - example invalidation
source_refs:
  - {source_ref}
created: 2026-03-13T14:22:33Z
updated: 2026-03-13T14:22:33Z
{extra}---

# {heading}
""",
            encoding="utf-8",
        )
        return self.run_validator()

    def validate_paper(
        self,
        *,
        source_uri: str | None = "https://example.org/paper",
        source_sha256: str | None = "a" * 64,
        title_line: str = "title: Example paper\n",
        heading: str = "Example paper",
        tags_yaml: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        papers = self.vault / "Knowledge/Papers"
        papers.mkdir(parents=True, exist_ok=True)
        source_metadata = ""
        if source_uri is not None:
            source_metadata += f"source_uri: {source_uri}\n"
        if source_sha256 is not None:
            source_metadata += f"source_sha256: {source_sha256}\n"
        tag_metadata = "" if tags_yaml is None else f"tags:{tags_yaml}\n"
        (papers / "paper-example.md").write_text(
            f"""---
id: paper-example
{title_line}record_type: paper
status: source
citation_key: example-2026-paper
source_ref: embedded:claim-ledger
{source_metadata}{tag_metadata}created: 2026-03-13T14:22:33Z
updated: 2026-03-13T14:22:33Z
---

# {heading}
""",
            encoding="utf-8",
        )
        return self.run_validator()

    def validate_canonical(
        self, tags_yaml: str = " []"
    ) -> subprocess.CompletedProcess[str]:
        canonical = self.vault / "Knowledge/Canonical"
        canonical.mkdir(parents=True, exist_ok=True)
        (canonical / "knowledge-method-example.md").write_text(
            f"""---
id: knowledge-method-example
title: Example canonical knowledge
record_type: canonical
knowledge_kind: method
lifecycle: provisional
evidence_state: observed
aliases: []
tags:{tags_yaml}
scope:
  - example scope
assumptions:
  - example assumption
invalidation_conditions:
  - example invalidation
source_refs:
  - embedded:evidence-1
created: 2026-03-13T14:22:33Z
updated: 2026-03-13T14:22:33Z
---

# Example canonical knowledge
""",
            encoding="utf-8",
        )
        return self.run_validator()

    def validate_proposal(
        self,
        *,
        title_line: str = 'title: "Proposal: Create example owner"\n',
        heading: str = "Proposal: Create example owner",
    ) -> subprocess.CompletedProcess[str]:
        proposals = self.vault / "_durable-knowledge/Proposals"
        proposals.mkdir(parents=True, exist_ok=True)
        (proposals / "proposal-example.md").write_text(
            f"""---
id: proposal-20260313t142233123456z-example
{title_line}record_type: proposal
decision: create
target_id: null
target_path: null
base_sha256: null
candidate_ids:
  - candidate-20260313t142233123456z-example
source_refs:
  - embedded:proposed-canonical-result
created: 2026-03-13T14:22:33Z
---

# {heading}
""",
            encoding="utf-8",
        )
        return self.run_validator()

    def run_validator(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(_VALIDATOR), "--vault", str(self.vault)],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_valid_flat_sequence_passes(self) -> None:
        result = self.validate_candidate(
            "\n  - example scope", extra="metadata:\n  nested: ignored\n"
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("replica-portable", result.stdout)

    def test_multiple_topic_tags_pass(self) -> None:
        result = self.validate_candidate(
            "\n  - example scope",
            extra=(
                "tags:\n"
                "  - topic/conformal-prediction\n"
                "  - topic/uncertainty-quantification\n"
            ),
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("topic tags should use", result.stdout)

    def test_empty_topic_tags_pass(self) -> None:
        result = self.validate_candidate("\n  - example scope", extra="tags: []\n")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_topic_tags_must_be_sequence(self) -> None:
        result = self.validate_candidate(
            "\n  - example scope", extra="tags: topic/conformal-prediction\n"
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("fields must be flat sequences: tags", result.stdout)

    def test_noncanonical_topic_tag_warns_for_legacy_compatibility(self) -> None:
        result = self.validate_candidate(
            "\n  - example scope", extra="tags:\n  - conformal-prediction\n"
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(
            "topic tags should use topic/<lowercase-kebab-case>", result.stdout
        )

    def test_duplicate_topic_tags_warn(self) -> None:
        result = self.validate_candidate(
            "\n  - example scope",
            extra=(
                "tags:\n"
                "  - topic/conformal-prediction\n"
                "  - topic/conformal-prediction\n"
            ),
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("topic tags contain duplicate values", result.stdout)

    def test_topic_tag_placeholder_fails(self) -> None:
        result = self.validate_candidate(
            "\n  - example scope", extra="tags:\n  - topic/<slug>\n"
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "sequence fields contain empty or placeholder items: tags", result.stdout
        )

    def test_paper_and_canonical_topic_tags_pass(self) -> None:
        paper_result = self.validate_paper(tags_yaml="\n  - topic/example")
        canonical_result = self.validate_canonical("\n  - topic/example")

        self.assertEqual(
            paper_result.returncode, 0, paper_result.stdout + paper_result.stderr
        )
        self.assertEqual(
            canonical_result.returncode,
            0,
            canonical_result.stdout + canonical_result.stderr,
        )

    def test_local_source_reference_warns_without_invalidating_record(self) -> None:
        result = self.validate_candidate(
            "\n  - example scope", source_ref="session:pi:local-session"
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("source reference is local-only", result.stdout)

    def test_bare_ticket_reference_warns(self) -> None:
        result = self.validate_candidate("\n  - example scope", source_ref="LOCAL-123")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("not recognized as replica-portable", result.stdout)

    def test_malformed_portable_source_reference_warns(self) -> None:
        malformed_references = (
            "embedded:",
            "vault:record:knowledge-example",
            "paper:doi:#section",
            "https://",
            "https://[bad",
            "urn:namespace:",
        )
        for source_reference in malformed_references:
            with self.subTest(source_reference=source_reference):
                result = self.validate_candidate(
                    "\n  - example scope", source_ref=source_reference
                )

                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("source reference is malformed", result.stdout)

    def test_paper_source_metadata_passes_when_portable_and_well_formed(self) -> None:
        result = self.validate_paper()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_legacy_paper_without_optional_source_metadata_passes(self) -> None:
        result = self.validate_paper(source_uri=None, source_sha256=None)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_paper_null_source_metadata_passes(self) -> None:
        result = self.validate_paper(source_uri="null", source_sha256="null")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_paper_source_uri_rejects_local_path(self) -> None:
        result = self.validate_paper(source_uri="/tmp/paper.pdf")

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "source_uri must be null or a resolvable HTTPS URI", result.stdout
        )

    def test_paper_source_uri_handles_malformed_url_without_crashing(self) -> None:
        result = self.validate_paper(source_uri="https://[bad")

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "source_uri must be null or a resolvable HTTPS URI", result.stdout
        )

    def test_paper_empty_source_metadata_fails(self) -> None:
        result = self.validate_paper(source_uri="", source_sha256="")

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "source_uri must be null or a resolvable HTTPS URI", result.stdout
        )
        self.assertIn("source_sha256 must be null or 64 lowercase", result.stdout)

    def test_paper_source_sha256_rejects_malformed_hash(self) -> None:
        result = self.validate_paper(source_sha256="not-a-sha256")

        self.assertEqual(result.returncode, 1)
        self.assertIn("source_sha256 must be null or 64 lowercase", result.stdout)

    def test_legacy_paper_without_title_warns(self) -> None:
        result = self.validate_paper(title_line="")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("has no human-readable title", result.stdout)

    def test_paper_title_must_match_first_h1(self) -> None:
        result = self.validate_paper(heading="Different paper")

        self.assertEqual(result.returncode, 1)
        self.assertIn("title must exactly match the first H1", result.stdout)

    def test_valid_proposal_title_passes(self) -> None:
        result = self.validate_proposal()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_legacy_proposal_without_title_warns(self) -> None:
        result = self.validate_proposal(title_line="")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("has no human-readable title", result.stdout)

    def test_proposal_title_must_match_first_h1(self) -> None:
        result = self.validate_proposal(heading="Proposal: Different action")

        self.assertEqual(result.returncode, 1)
        self.assertIn("title must exactly match the first H1", result.stdout)

    def test_missing_title_warns_and_uses_legacy_fallback(self) -> None:
        result = self.validate_candidate("\n  - example scope", title_line="")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("has no human-readable title", result.stdout)

    def test_title_must_match_first_h1(self) -> None:
        result = self.validate_candidate(
            "\n  - example scope", heading="Different heading"
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("title must exactly match the first H1", result.stdout)

    def test_empty_required_sequence_fails(self) -> None:
        result = self.validate_candidate(" []")

        self.assertEqual(result.returncode, 1)
        self.assertIn("required sequence fields are empty: scope", result.stdout)

    def test_placeholder_sequence_item_fails(self) -> None:
        result = self.validate_candidate("\n  - <scope>")

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "sequence fields contain empty or placeholder items: scope", result.stdout
        )

    def test_comment_only_sequence_item_fails(self) -> None:
        result = self.validate_candidate("\n  - # missing scope")

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "sequence fields contain empty or placeholder items: scope", result.stdout
        )

    def test_scalar_instead_of_sequence_fails(self) -> None:
        result = self.validate_candidate(" example scope")

        self.assertEqual(result.returncode, 1)
        self.assertIn("fields must be flat sequences: scope", result.stdout)

    def test_sequence_instead_of_scalar_fails(self) -> None:
        result = self.validate_candidate(
            "\n  - example scope", status_yaml="\n  - pending"
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("fields must be scalars: status", result.stdout)

    def test_duplicate_top_level_field_fails(self) -> None:
        result = self.validate_candidate(
            "\n  - example scope", extra="id: duplicate-id\n"
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate top-level field: id", result.stdout)

    def test_legacy_control_directory_requires_migration(self) -> None:
        control = self.vault / "_durable-knowledge"
        legacy = self.vault / ".llm-wiki"
        control.rename(legacy)

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("legacy control directory remains", result.stdout)
        self.assertIn("run bootstrap to migrate", result.stdout)

    def test_non_file_marker_fails(self) -> None:
        marker = self.vault / "_durable-knowledge/ROOT.md"
        marker.unlink()
        marker.mkdir()

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("vault marker is not a regular file", result.stdout)

    def test_legacy_marker_requires_migration(self) -> None:
        marker = self.vault / "_durable-knowledge/ROOT.md"
        legacy_marker = self.vault / "_durable-knowledge/ROOT"
        marker.rename(legacy_marker)

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("legacy vault marker remains", result.stdout)
        self.assertIn("run bootstrap to migrate", result.stdout)


if __name__ == "__main__":
    unittest.main()
