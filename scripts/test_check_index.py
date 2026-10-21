#!/usr/bin/env python3
"""Unit tests for scripts/check_index.py.

Standard library only (unittest), so the suite runs anywhere Python runs.
Run with:  python3 -m unittest discover -s scripts -p 'test_*.py' -v
"""

from __future__ import annotations

import importlib.util
import os
import unittest

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)


def load_checker():
    spec = importlib.util.spec_from_file_location(
        "check_index", os.path.join(SCRIPT_DIR, "check_index.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


checker = load_checker()

VALID_ROW = "| Widget 100 | [widget-driver](https://github.com/ami3go/widget-driver) | wip |"

HEADER = "| Device | Repository | Status |\n|---|---|---|\n"


def table(*rows: str) -> str:
    """Build a complete markdown index table from data rows."""
    return HEADER + "".join(row + "\n" for row in rows)


class TableCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        checker.problems.clear()

    def check(self, text: str):
        checker.problems.clear()
        return checker.check_tables(text)

    def test_valid_row_is_accepted(self) -> None:
        found = self.check(table(VALID_ROW))
        self.assertEqual(checker.problems, [])
        self.assertEqual(found, [("ami3go/widget-driver", "wip", 3)])

    def test_unknown_status_is_rejected(self) -> None:
        self.check(table("| W | [w](https://github.com/ami3go/w) | released |"))
        self.assertEqual(len(checker.problems), 1)
        self.assertIn("unknown status", checker.problems[0])

    def test_external_status_is_allowed_for_third_party_repos(self) -> None:
        found = self.check(
            table("| W | [w](https://github.com/picotech/picosdk-python-wrappers) | external |")
        )
        self.assertEqual(checker.problems, [])
        self.assertEqual(found, [("picotech/picosdk-python-wrappers", "external", 3)])

    def test_non_ami3go_repo_must_be_external(self) -> None:
        self.check(table("| W | [w](https://github.com/someone/else) | stable |"))
        self.assertEqual(len(checker.problems), 1)
        self.assertIn("not owned by ami3go", checker.problems[0])

    def test_wrong_column_count_is_rejected(self) -> None:
        self.check(table("| W | [w](https://github.com/ami3go/w) |"))
        self.assertEqual(len(checker.problems), 1)
        self.assertIn("expected 3", checker.problems[0])

    def test_missing_link_is_rejected(self) -> None:
        self.check(table("| W | widget-driver | wip |"))
        self.assertEqual(len(checker.problems), 1)
        self.assertIn("no github.com link", checker.problems[0])

    def test_duplicate_repository_is_rejected(self) -> None:
        checker.problems.clear()
        found = checker.check_tables(table(VALID_ROW, VALID_ROW))
        checker.check_duplicate_repos(found)
        self.assertEqual(len(checker.problems), 1)
        self.assertIn("already indexed", checker.problems[0])

    def test_rows_outside_an_index_table_are_ignored(self) -> None:
        found = self.check("| A | B |\n|---|---|\n| 1 | 2 |\n")
        self.assertEqual(checker.problems, [])
        self.assertEqual(found, [])


class RepositoryStateTests(unittest.TestCase):
    """The checker must agree with the repository as it is actually checked in."""

    def setUp(self) -> None:
        checker.problems.clear()

    def test_repository_index_is_consistent(self) -> None:
        checker.check_tables(checker.read(checker.README))
        checker.check_guides_index()
        checker.check_relative_links()
        self.assertEqual(checker.problems, [])

    def test_every_indexed_repo_is_in_the_ami3go_org_or_external(self) -> None:
        found = checker.check_tables(checker.read(checker.README))
        for slug, status, _line in found:
            owner = slug.split("/", 1)[0]
            if owner != "ami3go":
                self.assertEqual(status, "external", f"{slug} must be marked external")

    def test_status_labels_are_from_lpds_001(self) -> None:
        self.assertEqual(checker.VALID_STATUSES, ("wip", "untested", "stable"))


class GuidesIndexTests(unittest.TestCase):
    def setUp(self) -> None:
        checker.problems.clear()

    def test_all_lpds_documents_are_indexed(self) -> None:
        checker.check_guides_index()
        self.assertEqual(checker.problems, [])

    def test_index_ids_match_filenames(self) -> None:
        text = checker.read(checker.GUIDES_INDEX)
        for doc_id, filename in checker.LPDS_LINK_RE.findall(text):
            match = checker.LPDS_FILE_RE.match(filename)
            self.assertIsNotNone(match, filename)
            self.assertEqual(match.group(1), doc_id)


class RemoteCheckTests(unittest.TestCase):
    """A GitHub API hiccup must not be reported as a broken index entry."""

    def setUp(self) -> None:
        checker.problems.clear()
        checker.warnings.clear()

    def _with_fake_fetch(self, fake_fetch, slug="ami3go/example", status="wip"):
        """Run check_remote against a stubbed fetch, restoring globals after."""
        original_fetch = checker.fetch_repo
        original_sleep = checker.time.sleep
        checker.fetch_repo = fake_fetch
        checker.time.sleep = lambda _seconds: None
        try:
            checker.check_remote([(slug, status, 1)])
        finally:
            checker.fetch_repo = original_fetch
            checker.time.sleep = original_sleep

    def test_404_is_a_definitive_failure(self) -> None:
        self.assertEqual(checker.classify_http_error(404), checker.MISSING)

    def test_auth_failure_is_reported_separately(self) -> None:
        self.assertEqual(checker.classify_http_error(401), checker.FORBIDDEN)

    def test_rate_limit_is_detected(self) -> None:
        self.assertEqual(checker.classify_http_error(429), checker.RATE_LIMITED)
        self.assertEqual(
            checker.classify_http_error(403, body="API rate limit exceeded"),
            checker.RATE_LIMITED,
        )
        self.assertEqual(
            checker.classify_http_error(403, headers={"x-ratelimit-remaining": "0"}),
            checker.RATE_LIMITED,
        )

    def test_permission_error_is_not_a_rate_limit(self) -> None:
        self.assertEqual(
            checker.classify_http_error(403, body="Resource not accessible by integration"),
            checker.FORBIDDEN,
        )

    def test_server_errors_are_transient(self) -> None:
        for code in (500, 502, 503, 504):
            self.assertEqual(checker.classify_http_error(code), checker.TRANSIENT)

    def test_transient_failure_warns_instead_of_failing(self) -> None:
        self._with_fake_fetch(lambda slug, headers: (None, checker.TRANSIENT, "HTTP 502"))
        self.assertEqual(checker.problems, [])
        self.assertEqual(len(checker.warnings), 1)
        self.assertIn("network problem", checker.warnings[0])

    def test_transient_failure_is_retried(self) -> None:
        calls = []

        def fake_fetch(slug, headers):
            calls.append(slug)
            return None, checker.TRANSIENT, "HTTP 502"

        self._with_fake_fetch(fake_fetch)
        self.assertEqual(len(calls), checker.RETRY_ATTEMPTS)

    def test_missing_repository_fails(self) -> None:
        self._with_fake_fetch(lambda slug, headers: (None, checker.MISSING, "HTTP 404"))
        self.assertEqual(len(checker.problems), 1)
        self.assertIn("does not exist on GitHub", checker.problems[0])

    def test_forbidden_repository_fails(self) -> None:
        self._with_fake_fetch(lambda slug, headers: (None, checker.FORBIDDEN, "HTTP 403"))
        self.assertEqual(len(checker.problems), 1)
        self.assertIn("permissions", checker.problems[0])

    def test_rate_limit_stops_the_sweep_with_one_warning(self) -> None:
        calls = []

        def fake_fetch(slug, headers):
            calls.append(slug)
            return None, checker.RATE_LIMITED, "HTTP 403"

        self._with_fake_fetch(fake_fetch, slug="ami3go/example")
        self.assertEqual(checker.problems, [])
        self.assertEqual(len(checker.warnings), 1)
        self.assertIn("rate limit", checker.warnings[0])

    def test_archived_repository_fails(self) -> None:
        self._with_fake_fetch(
            lambda slug, headers: ({"archived": True, "private": False}, "", "")
        )
        self.assertEqual(len(checker.problems), 1)
        self.assertIn("archived", checker.problems[0])

    def test_private_repository_fails(self) -> None:
        self._with_fake_fetch(
            lambda slug, headers: ({"archived": False, "private": True}, "", "")
        )
        self.assertEqual(len(checker.problems), 1)
        self.assertIn("is private", checker.problems[0])


if __name__ == "__main__":
    unittest.main()
