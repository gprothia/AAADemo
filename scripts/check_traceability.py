#!/usr/bin/env python3
"""Deterministic spec -> test traceability gate.

For every spec in specs/ whose status is `approved` or `implemented`, every
non-retired acceptance criterion must be covered by:
  - a pytest marked @pytest.mark.ac("<AC-ID>") under tests/api   if tagged [api]
  - a Playwright test tagged '@<AC-ID>' under tests/ui            if tagged [ui]

Also reports test references to AC IDs that don't exist in any spec (orphans).
Exit code 1 on any gap. Writes a Markdown summary to $GITHUB_STEP_SUMMARY if set.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPECS = ROOT / "specs"
API_DIR = ROOT / "tests" / "api"
UI_DIR = ROOT / "tests" / "ui"

FRONT_MATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)
STATUS = re.compile(r"^status:\s*(\w+)", re.M)
# "### ORD-001-AC1 [api]"  or retired: "### ~~ORD-001-AC1 [api]~~"
AC_HEADING = re.compile(r"^###\s+(~~)?\s*([A-Z]+-\d{3}-AC\d+)\s*\[([a-z, ]+)\]", re.M)
API_REF = re.compile(r"""@pytest\.mark\.ac\(\s*["']([A-Z]+-\d{3}-AC\d+)["']""")
UI_REF = re.compile(r"""['"]@([A-Z]+-\d{3}-AC\d+)['"]""")


def scan(directory: Path, pattern: re.Pattern, globs: tuple[str, ...]) -> set[str]:
    found: set[str] = set()
    for g in globs:
        for f in directory.rglob(g):
            if "node_modules" in f.parts:
                continue
            found.update(pattern.findall(f.read_text(encoding="utf-8")))
    return found


def main() -> int:
    api_refs = scan(API_DIR, API_REF, ("*.py",))
    ui_refs = scan(UI_DIR, UI_REF, ("*.ts", "*.js"))

    gaps: list[tuple[str, str, str]] = []
    all_ids: set[str] = set()
    checked = 0

    for spec in sorted(SPECS.glob("*.md")):
        if spec.name.startswith("_"):
            continue
        text = spec.read_text(encoding="utf-8")
        fm = FRONT_MATTER.match(text)
        status = STATUS.search(fm.group(1)).group(1) if fm and STATUS.search(fm.group(1)) else "draft"
        for retired, ac_id, tags in AC_HEADING.findall(text):
            all_ids.add(ac_id)
            if retired or status not in ("approved", "implemented"):
                continue
            checked += 1
            tagset = {t.strip() for t in tags.split(",")}
            if "api" in tagset and ac_id not in api_refs:
                gaps.append((spec.name, ac_id, "missing API test"))
            if "ui" in tagset and ac_id not in ui_refs:
                gaps.append((spec.name, ac_id, "missing UI test"))

    orphans = sorted((api_refs | ui_refs) - all_ids)

    lines = [f"### Spec traceability: {checked} acceptance criteria checked", ""]
    if gaps:
        lines += ["| Spec | Criterion | Problem |", "|---|---|---|"]
        lines += [f"| {s} | `{a}` | {p} |" for s, a, p in gaps]
    else:
        lines.append("All approved acceptance criteria have tests. ✅")
    if orphans:
        lines += ["", "Tests reference unknown criteria: " + ", ".join(f"`{o}`" for o in orphans)]
    report = "\n".join(lines)

    print(report)
    if summary := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write(report + "\n")
    return 1 if gaps or orphans else 0


if __name__ == "__main__":
    sys.exit(main())
