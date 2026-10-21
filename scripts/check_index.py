#!/usr/bin/env python3
"""Validate the Lab-equipment-pyDrivers hub index.

The hub is an index, so the only thing that can really break is the index
itself: a malformed table row, a status label that is not one of the three
labels defined by LPDS-001 section 9, a link to a repository that no longer
exists, or a standard document that is indexed but missing from disk.

This script checks all of that. It uses the standard library only, so it
runs identically on a maintainer's laptop and in CI.

Usage:
    python3 scripts/check_index.py                # offline checks only
    python3 scripts/check_index.py --check-remote # also resolve GitHub links

Exit code is 0 when every check passes, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(REPO_ROOT, "README.md")
GUIDES_DIR = os.path.join(REPO_ROOT, "AI_Guides")
GUIDES_INDEX = os.path.join(GUIDES_DIR, "README.md")

# LPDS-001 section 9 -- "Driver Status".
VALID_STATUSES = ("wip", "untested", "stable")

# LPDS documents are numbered LPDS-NNN; the index table links them by file.
LPDS_FILE_RE = re.compile(r"^LPDS-(\d{3})_.+\.md$")
LPDS_LINK_RE = re.compile(r"\[LPDS-(\d{3})\]\((LPDS-\d{3}_[^)]+\.md)\)")

GITHUB_LINK_RE = re.compile(r"https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)")

# Relative markdown links must resolve to a file in the repository.
MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")

problems: list[str] = []
warnings: list[str] = []


def fail(message: str) -> None:
    problems.append(message)


def warn(message: str) -> None:
    warnings.append(message)


def read(path: str) -> str:
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_separator(cells: list[str]) -> bool:
    """True for the |---|---| divider row of a markdown table."""
    return bool(cells) and all(set(cell) <= set("-: ") and "-" in cell for cell in cells)


def parse_index_tables(text: str) -> list[tuple[int, list[str]]]:
    """Return (line number, cells) for every data row of every index table.

    An index table is a markdown table whose header names both a "Repository"
    and a "Status" column. Detecting tables by their header rather than by
    the presence of a link matters: a row whose link was dropped by mistake
    must still be reported, not silently skipped.
    """
    lines = text.splitlines()
    rows: list[tuple[int, list[str]]] = []

    index = 0
    while index < len(lines):
        if not lines[index].strip().startswith("|"):
            index += 1
            continue

        # Collect the contiguous block of table lines.
        start = index
        block: list[tuple[int, str]] = []
        while index < len(lines) and lines[index].strip().startswith("|"):
            block.append((index + 1, lines[index]))
            index += 1

        if not block:
            continue

        header = [cell.lower() for cell in split_row(block[0][1])]
        is_index_table = "repository" in header and "status" in header
        if not is_index_table:
            continue

        for number, line in block[1:]:
            cells = split_row(line)
            if is_separator(cells):
                continue
            rows.append((number, cells))

    return rows


def check_tables(text: str) -> list[tuple[str, str, int]]:
    """Validate every index table row. Returns (repo slug, status, line)."""
    found = []
    for number, cells in parse_index_tables(text):
        if len(cells) != 3:
            fail(
                f"README.md:{number}: index row has {len(cells)} columns, expected 3 "
                f"(| Device | Repository | Status |): {cells}"
            )
            continue

        device, repository_cell, status = cells

        if not device:
            fail(f"README.md:{number}: index row has an empty device name")
        if not status:
            fail(f"README.md:{number}: index row has an empty status")
        elif status not in VALID_STATUSES and status != "external":
            fail(
                f"README.md:{number}: unknown status {status!r}; expected one of "
                f"{', '.join(VALID_STATUSES)}"
            )

        links = GITHUB_LINK_RE.findall(repository_cell)
        if not links:
            fail(
                f"README.md:{number}: repository cell has no github.com link: "
                f"{repository_cell!r}"
            )
            continue
        if len(links) > 1:
            fail(
                f"README.md:{number}: repository cell has {len(links)} links, expected 1: "
                f"{repository_cell!r}"
            )
            continue

        owner, repo = links[0]
        if owner != "ami3go" and status != "external":
            fail(
                f"README.md:{number}: repository {owner}/{repo} is not owned by "
                f"ami3go but is indexed as {status!r}"
            )
        found.append((f"{owner}/{repo}", status, number))
    return found


def check_duplicate_repos(found: list[tuple[str, str, int]]) -> None:
    seen: dict[str, int] = {}
    for slug, _status, number in found:
        if slug in seen:
            fail(
                f"README.md:{number}: {slug} is already indexed on line {seen[slug]}; "
                f"the same repository must not appear twice"
            )
        else:
            seen[slug] = number


def check_guides_index() -> None:
    """Every LPDS document on disk must be indexed, and vice versa."""
    if not os.path.isdir(GUIDES_DIR):
        fail(f"missing directory: {GUIDES_DIR}")
        return

    on_disk = {
        name
        for name in os.listdir(GUIDES_DIR)
        if LPDS_FILE_RE.match(name) and name != "README.md"
    }

    index_text = read(GUIDES_INDEX)
    indexed: dict[str, str] = {}
    for doc_id, filename in LPDS_LINK_RE.findall(index_text):
        if filename in indexed:
            fail(
                f"AI_Guides/README.md: {doc_id} is indexed more than once "
                f"({indexed[doc_id]} and {filename})"
            )
        indexed[filename] = doc_id

    for filename in sorted(on_disk - set(indexed)):
        fail(f"AI_Guides/{filename} exists on disk but is not listed in AI_Guides/README.md")
    for filename in sorted(set(indexed) - on_disk):
        fail(
            f"AI_Guides/README.md links to {filename}, which does not exist in AI_Guides/"
        )

    # The index must not advertise retired document numbers.
    for filename, doc_id in sorted(indexed.items(), key=lambda item: item[1]):
        disk_id = LPDS_FILE_RE.match(filename).group(1)
        if disk_id != doc_id:
            fail(
                f"AI_Guides/README.md indexes {filename} as LPDS-{doc_id}, but the "
                f"file itself is LPDS-{disk_id}"
            )


def check_relative_links() -> None:
    """Every relative markdown link in the repository must resolve."""
    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "__pycache__")]
        for name in files:
            if not name.endswith(".md"):
                continue
            path = os.path.join(root, name)
            relative = os.path.relpath(path, REPO_ROOT)
            text = read(path)
            for match in MD_LINK_RE.finditer(text):
                link = match.group(1)
                if link.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                target = os.path.normpath(os.path.join(root, link.split("#")[0]))
                if not os.path.exists(target):
                    fail(f"{relative}: broken relative link -> {link}")


# A GitHub API hiccup is not a broken index entry. Only a definitive
# answer ("404", "archived", "private") is a failure; a transport error is
# retried, and if it persists it is reported as a warning so that a network
# outage cannot block an unrelated pull request.
MISSING = "missing"
FORBIDDEN = "forbidden"
TRANSIENT = "transient"
RATE_LIMITED = "rate_limited"

RETRY_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = 2.0

# The unauthenticated GitHub API allows 60 requests per hour per address,
# which a full index sweep exceeds. Set GITHUB_TOKEN to raise the limit.
RATE_LIMIT_HINT = (
    "GitHub API rate limit reached (unauthenticated requests are limited to "
    "60/hour) -- set GITHUB_TOKEN or GH_TOKEN and try again"
)


def classify_http_error(code: int, body: str = "", headers: dict | None = None) -> str:
    """Map an HTTP status code to MISSING, FORBIDDEN, TRANSIENT or RATE_LIMITED."""
    headers = headers or {}
    if code == 404:
        return MISSING
    if code == 429:
        return RATE_LIMITED
    if code == 403:
        remaining = headers.get("x-ratelimit-remaining")
        if remaining == "0" or "rate limit" in body.lower():
            return RATE_LIMITED
        return FORBIDDEN
    if code == 401:
        return FORBIDDEN
    return TRANSIENT


def fetch_repo(slug: str, headers: dict[str, str]) -> tuple[dict | None, str, str]:
    """Fetch a repository's metadata.

    Returns (payload, kind, detail) where kind is one of "", MISSING,
    FORBIDDEN, RATE_LIMITED or TRANSIENT. An empty kind means the fetch
    succeeded.
    """
    owner, repo = slug.split("/", 1)
    url = f"https://api.github.com/repos/{owner}/{repo}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.load(response), "", ""
    except urllib.error.HTTPError as error:
        body = ""
        try:
            body = error.read().decode("utf-8", "replace")
        except Exception:  # pragma: no cover - the body is best effort only
            pass
        response_headers = dict(error.headers or {})
        kind = classify_http_error(error.code, body, response_headers)
        return None, kind, f"HTTP {error.code}"
    except urllib.error.URLError as error:
        return None, TRANSIENT, f"could not reach GitHub: {error.reason}"
    except (TimeoutError, json.JSONDecodeError, OSError) as error:
        return None, TRANSIENT, str(error)


def check_remote(found: list[tuple[str, str, int]]) -> None:
    """Confirm that every indexed GitHub repository still resolves."""
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    for slug, status, number in found:
        payload = None
        kind = ""
        detail = ""

        for attempt in range(1, RETRY_ATTEMPTS + 1):
            payload, kind, detail = fetch_repo(slug, headers)
            if kind != TRANSIENT:
                break
            if attempt < RETRY_ATTEMPTS:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)

        if kind == MISSING:
            fail(f"README.md:{number}: {slug} does not exist on GitHub")
            continue
        if kind == RATE_LIMITED:
            warn(f"{RATE_LIMIT_HINT} -- skipping the remaining remote checks")
            return
        if kind == FORBIDDEN:
            fail(
                f"README.md:{number}: could not read {slug} from GitHub ({detail}); "
                f"check the token's permissions or the rate limit"
            )
            continue
        if kind == TRANSIENT:
            warn(
                f"README.md:{number}: could not verify {slug} -- {detail}. "
                f"Treating this as a network problem, not a broken index entry."
            )
            continue

        if payload.get("archived"):
            fail(f"README.md:{number}: {slug} is archived on GitHub")
        if payload.get("private") and status != "external":
            fail(
                f"README.md:{number}: {slug} is private but is listed as {status!r}; "
                f"a private repo cannot be used as an index entry"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-remote",
        action="store_true",
        help="also resolve every indexed GitHub repository over the network",
    )
    args = parser.parse_args()

    if not os.path.exists(README):
        print(f"error: {README} not found", file=sys.stderr)
        return 1

    readme_text = read(README)
    found = check_tables(readme_text)
    if not found:
        fail("README.md: no index rows found -- the driver table looks empty")

    check_duplicate_repos(found)
    check_guides_index()
    check_relative_links()

    if args.check_remote:
        check_remote(found)

    if problems:
        print(f"index check FAILED ({len(problems)} problem(s)):")
        for problem in problems:
            print(f"  - {problem}")
        for warning in warnings:
            print(f"  warning: {warning}")
        return 1

    print(
        f"index check OK: {len(found)} index rows, "
        f"{len([n for n in os.listdir(GUIDES_DIR) if LPDS_FILE_RE.match(n)])} "
        f"LPDS documents indexed"
    )
    for warning in warnings:
        print(f"  warning: {warning}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
