#!/usr/bin/env python3
"""Pinned package versions to OSV advisory IDs (metadata only: names and versions leave this host, never code).

Usage: osv-lookup.py --ecosystem <ECOSYSTEM> <name>==<version> [<name>==<version> ...]
ECOSYSTEM is OSV's exact, case-sensitive name: PyPI, npm, crates.io, Go, Maven, NuGet, RubyGems, ...
Prints one JSON object keyed by pin. Exits 0 only when every lookup completed; a pin with
an "error" entry has no answer, never an implied "no advisories".
"""

import argparse
import json
import sys
import urllib.error
import urllib.request
from typing import TypedDict

OSV_QUERY_URL = "https://api.osv.dev/v1/query"
TIMEOUT_SECONDS = 30
MAX_PAGES = 50


class Advisory(TypedDict):
    id: str
    summary: str
    aliases: list[str]


class LookupResult(TypedDict, total=False):
    vulns: list[Advisory]
    error: str


class Package(TypedDict):
    name: str
    ecosystem: str


class _QueryPage(TypedDict, total=False):
    page_token: str


class Query(_QueryPage):
    package: Package
    version: str


def _query(body: Query) -> tuple[list[Advisory], str | None]:
    """One OSV page: its advisories and the token for the next page, if any."""
    request = urllib.request.Request(OSV_QUERY_URL, data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        page = json.loads(response.read())

    vulns = page.get("vulns", []) if isinstance(page, dict) else None
    if not isinstance(vulns, list) or not all(isinstance(vuln, dict) and isinstance(vuln.get("id"), str)
                                              for vuln in vulns):
        raise ValueError("unexpected OSV response shape")
    advisories = [Advisory(id=vuln["id"], summary=str(vuln.get("summary") or "")[:200],
                           aliases=[str(alias) for alias in vuln.get("aliases") or []]) for vuln in vulns]
    token = page.get("next_page_token")
    return advisories, token if isinstance(token, str) and token else None


def lookup(ecosystem: str, name: str, version: str) -> LookupResult:
    """All advisories for one pin, following OSV pagination (large or slow results arrive in pages)."""
    body = Query(package=Package(name=name, ecosystem=ecosystem), version=version)
    advisories: list[Advisory] = []
    try:
        for _ in range(MAX_PAGES):
            page, token = _query(body)
            advisories += page
            if token is None:
                return LookupResult(vulns=advisories)
            body["page_token"] = token
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")[:200]
        return LookupResult(error=f"HTTP {error.code}: {detail}")
    except (OSError, ValueError) as error:
        return LookupResult(error=str(error)[:200])
    return LookupResult(error=f"more than {MAX_PAGES} result pages; partial results discarded")


def _parse_pin(pin: str) -> tuple[str, str]:
    name, separator, version = pin.partition("==")
    name, version = name.strip(), version.strip()
    if not separator or not name or not version or version.startswith("=") or "[" in name:
        raise ValueError(f"want name==version without extras, got {pin!r}")
    return name, version


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--ecosystem", required=True, help="OSV ecosystem name, e.g. PyPI or npm")
    parser.add_argument("pins", nargs="+", metavar="name==version")
    args = parser.parse_args(argv[1:])

    try:
        pins = {pin: _parse_pin(pin) for pin in args.pins}
    except ValueError as error:
        parser.error(str(error))

    results = {pin: lookup(args.ecosystem, name, version) for pin, (name, version) in pins.items()}
    print(json.dumps({"ecosystem": args.ecosystem, "results": results}, indent=1))
    return 1 if any("error" in result for result in results.values()) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
