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


if __name__ == "__main__":
    unittest.main()
