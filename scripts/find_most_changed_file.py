#!/usr/bin/env python3
"""
Find the most frequently changed file(s) in this repository.

Usage:
    python scripts/find_most_changed_file.py [--limit N] [--include-merges]

Options:
    --limit N          Limit the number of commits to scan (speeds up).
    --include-merges   Include merge commits (default: excluded).

Notes:
- This scans `git log --name-only` output and counts file path occurrences.
- Empty lines and commit metadata are ignored.
- Paths are normalized; only files tracked by git history are counted.
"""

from __future__ import annotations

import argparse
import os
import subprocess
from collections import Counter
from typing import List


def run_git_log(limit: int | None, include_merges: bool) -> List[str]:
    cmd = [
        "git",
        "log",
        "--pretty=format:",
        "--name-only",
    ]
    if not include_merges:
        cmd.insert(2, "--no-merges")
    if limit is not None:
        cmd.extend([f"-n{limit}"])

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout.splitlines()


def most_frequently_changed(limit: int | None, include_merges: bool) -> tuple[list[tuple[str, int]], int]:
    lines = run_git_log(limit=limit, include_merges=include_merges)
    counter: Counter[str] = Counter()

    for line in lines:
        path = line.strip()
        if not path:
            continue
        # Skip non-path lines (defensive; format already suppresses commit messages)
        if path.startswith("commit "):
            continue
        # Skip deletions shown as "path (deleted)" if any
        if path.endswith(" (deleted)"):
            path = path[: -len(" (deleted)")]
        counter[path] += 1

    if not counter:
        return [], 0

    max_count = max(counter.values())
    top = [(p, c) for p, c in counter.items() if c == max_count]
    top.sort(key=lambda x: x[0])
    return top, sum(counter.values())


def main() -> int:
    parser = argparse.ArgumentParser(description="Find the most frequently changed file(s) in the repo")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of commits to scan")
    parser.add_argument("--include-merges", action="store_true", help="Include merge commits")
    args = parser.parse_args()

    # Ensure we run inside a git repo
    if not os.path.isdir(os.path.join(os.getcwd(), ".git")):
        print("Error: Not inside a git repository")
        return 1

    try:
        top, total = most_frequently_changed(limit=args.limit, include_merges=args.include_merges)
    except subprocess.CalledProcessError as e:
        print(f"Error invoking git: {e}")
        return 1

    if not top:
        print("No changed files found in git history.")
        return 0

    print("Most frequently changed file(s):")
    for path, count in top:
        print(f"- {path}: {count} changes")
    print(f"Total file-change entries scanned: {total}")
    if args.limit:
        print(f"Commit limit applied: {args.limit}")
    print(f"Merge commits included: {args.include_merges}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
