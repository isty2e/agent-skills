import contextlib
import importlib.util
import io
import json
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "osv-lookup.py"


class OsvLookupTests(unittest.TestCase):
    def setUp(self) -> None:
        spec = importlib.util.spec_from_file_location("osv_lookup_under_test", SCRIPT)
        assert spec is not None and spec.loader is not None
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def test_token_only_page_is_followed_with_the_same_package_metadata(self) -> None:
        pages = [
            io.BytesIO(b'{"next_page_token":"page-2"}'),
            io.BytesIO(b'{"vulns":[{"id":"TEST-1","summary":"example","aliases":[]}]}'),
        ]
        output = io.StringIO()
        with (
            patch("urllib.request.urlopen", side_effect=pages) as request,
            contextlib.redirect_stdout(output),
        ):
            code = self.module.main(
                ["osv-lookup.py", "--ecosystem", "npm", "@scope/example==1.2.3"]
            )

        self.assertEqual(code, 0)
        result = json.loads(output.getvalue())
        self.assertEqual(
            result["results"]["@scope/example==1.2.3"]["vulns"][0]["id"], "TEST-1"
        )
        bodies = [json.loads(call.args[0].data) for call in request.call_args_list]
        self.assertEqual(
            bodies,
            [
                {
                    "package": {"name": "@scope/example", "ecosystem": "npm"},
                    "version": "1.2.3",
                },
                {
                    "package": {"name": "@scope/example", "ecosystem": "npm"},
                    "version": "1.2.3",
                    "page_token": "page-2",
                },
            ],
        )

    def test_an_empty_successful_lookup_is_distinct_from_an_error(self) -> None:
        output = io.StringIO()
        with (
            patch("urllib.request.urlopen", return_value=io.BytesIO(b"{}")),
            contextlib.redirect_stdout(output),
        ):
            code = self.module.main(
                ["osv-lookup.py", "--ecosystem", "PyPI", "example==1.0"]
            )

        self.assertEqual(code, 0)
        self.assertEqual(
            json.loads(output.getvalue())["results"], {"example==1.0": {"vulns": []}}
        )

    def test_lookup_error_does_not_become_no_advisories(self) -> None:
        output = io.StringIO()
        with (
            patch("urllib.request.urlopen", side_effect=OSError("offline fixture")),
            contextlib.redirect_stdout(output),
        ):
            code = self.module.main(
                ["osv-lookup.py", "--ecosystem", "npm", "example==1.0"]
            )

        self.assertEqual(code, 1)
        self.assertEqual(
            json.loads(output.getvalue())["results"],
            {"example==1.0": {"error": "offline fixture"}},
        )

    def test_malformed_response_is_not_no_advisories(self) -> None:
        output = io.StringIO()
        with (
            patch(
                "urllib.request.urlopen", return_value=io.BytesIO(b'{"vulns":false}')
            ),
            contextlib.redirect_stdout(output),
        ):
            code = self.module.main(
                ["osv-lookup.py", "--ecosystem", "npm", "example==1.0"]
            )

        self.assertEqual(code, 1)
        self.assertIn("error", json.loads(output.getvalue())["results"]["example==1.0"])

    def test_page_limit_discards_partial_results_instead_of_claiming_completion(
        self,
    ) -> None:
        pages = [
            io.BytesIO(b'{"next_page_token":"more"}'),
            io.BytesIO(b'{"vulns":[{"id":"TEST-1"}],"next_page_token":"more"}'),
        ]
        output = io.StringIO()
        with (
            patch.object(self.module, "MAX_PAGES", 2),
            patch("urllib.request.urlopen", side_effect=pages),
            contextlib.redirect_stdout(output),
        ):
            code = self.module.main(
                ["osv-lookup.py", "--ecosystem", "npm", "example==1.0"]
            )

        self.assertEqual(code, 1)
        result = json.loads(output.getvalue())["results"]["example==1.0"]
        self.assertIn("error", result)
        self.assertNotIn("vulns", result)

    def test_unpinned_input_is_rejected_before_network_access(self) -> None:
        with (
            patch("urllib.request.urlopen") as request,
            contextlib.redirect_stderr(io.StringIO()),
        ):
            with self.assertRaises(SystemExit) as stopped:
                self.module.main(["osv-lookup.py", "--ecosystem", "npm", "example"])

        self.assertEqual(stopped.exception.code, 2)
        request.assert_not_called()


if __name__ == "__main__":
    unittest.main()
