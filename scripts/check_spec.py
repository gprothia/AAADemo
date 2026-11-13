#!/usr/bin/env python3
"""Check that spec files follow .agents/rules/specs.md.

Usage:
  python scripts/check_spec.py                  # all specs in specs/
  python scripts/check_spec.py specs/ORD-002-cancel-order.md

Errors fail the check (exit 1). Warnings point at wording a reviewer should look at.
Writes a Markdown summary to $GITHUB_STEP_SUMMARY when set.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPECS = ROOT / "specs"

FILENAME = re.compile(r"^([A-Z]+-\d{3})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
FRONT_MATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)
# value, then an optional YAML comment (a '#' preceded by whitespace and followed by a space)
FIELD = re.compile(r"^(\w+):\s*(.*?)(?:\s+#\s.*)?\s*$", re.M)
AC_HEADING = re.compile(r"^###\s+(~~)?\s*(\S+)\s*\[([^\]]*)\]\s*(~~)?\s*$", re.M)
REQUIRED_FIELDS = ("id", "title", "status", "owner", "issue")
STATUSES = {"draft", "approved", "implemented"}
REQUIRED_SECTIONS = ("## Why", "## Scope", "## Acceptance criteria", "## Open questions")
VAGUE = re.compile(
    r"\b(an? error|appropriate|correctly|properly|works|should work|as expected|etc\.?|"
    r"user[- ]friendly|fast|quickly|some)\b",
    re.I,
)


def check(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    text = path.read_text(encoding="utf-8")

    m = FILENAME.match(path.name)
    if not m:
        errors.append("file name must be <AREA>-<NNN>-<kebab-name>.md, e.g. ORD-002-cancel-order.md")
    file_id = m.group(1) if m else None

    fm = FRONT_MATTER.match(text)
    if not fm:
        return errors + ["missing front matter (--- block at the top)"], warnings
    fields = {k: v.strip().strip('"').strip("'") for k, v in FIELD.findall(fm.group(1))}
    for f in REQUIRED_FIELDS:
        if not fields.get(f):
            errors.append(f"front matter: '{f}' is missing or empty")
    spec_id = fields.get("id", "")
    status = fields.get("status", "")
    if file_id and spec_id and spec_id != file_id:
        errors.append(f"front matter id '{spec_id}' does not match file name '{file_id}'")
    if status and status not in STATUSES:
        errors.append(f"status '{status}' must be one of {sorted(STATUSES)}")
    if fields.get("issue") and not re.fullmatch(r"#\d+", fields["issue"]):
        errors.append("issue must look like \"#123\"")
    if fields.get("owner") and not fields["owner"].startswith("@"):
        errors.append("owner must be a GitHub handle like \"@octocat\"")

    body = text[fm.end():]
    if spec_id and not re.search(rf"^# {re.escape(spec_id)}: .+", body, re.M):
        errors.append(f"title heading must be '# {spec_id}: <title>'")
    for section in REQUIRED_SECTIONS:
        if not re.search(rf"^{re.escape(section)}\s*$", body, re.M):
            errors.append(f"missing section '{section}'")

    # Acceptance criteria block
    ac_start = body.find("## Acceptance criteria")
    ac_end = body.find("\n## ", ac_start + 1) if ac_start >= 0 else -1
    ac_block = body[ac_start: ac_end if ac_end > 0 else None] if ac_start >= 0 else ""
    headings = list(AC_HEADING.finditer(ac_block))
    if ac_start >= 0 and not headings:
        errors.append("no acceptance criteria found (### <ID>-AC1 [api] ...)")

    seen: set[str] = set()
    expected_prefix = f"{spec_id}-AC"
    for i, h in enumerate(headings):
        retired = bool(h.group(1))
        ac_id, tags = h.group(2), h.group(3)
        where = f"{ac_id}"
        if not re.fullmatch(rf"{re.escape(expected_prefix)}\d+", ac_id):
            errors.append(f"{where}: ID must be {expected_prefix}<n>")
        if ac_id in seen:
            errors.append(f"{where}: duplicate criterion ID")
        seen.add(ac_id)
        tagset = {t.strip() for t in tags.split(",") if t.strip()}
        if not tagset or not tagset <= {"api", "ui"}:
            errors.append(f"{where}: tag must be [api], [ui] or [api,ui], got [{tags}]")
        if retired:
            continue
        end = headings[i + 1].start() if i + 1 < len(headings) else len(ac_block)
        chunk = ac_block[h.end():end]
        if not re.search(r"\*\*Given\*\*", chunk):
            errors.append(f"{where}: missing a **Given** line")
        then = re.search(r"\*\*Then\*\*(.*)", chunk)
        if not then:
            errors.append(f"{where}: missing a **Then** line")
        else:
            then_text = chunk[then.start():]
            if vague := VAGUE.search(then_text):
                warnings.append(f"{where}: 'Then' uses vague wording \"{vague.group(0)}\" - make it checkable")

    numbers = sorted(int(x.rsplit("AC", 1)[1]) for x in seen if re.fullmatch(r".+-AC\d+", x))
    if numbers and numbers != list(range(1, len(numbers) + 1)):
        warnings.append(f"criteria numbers are not 1..{len(numbers)} in sequence: {numbers}")

    oq = body.find("## Open questions")
    open_items = re.findall(r"^- \[ \]", body[oq:], re.M) if oq >= 0 else []
    if status in ("approved", "implemented") and open_items:
        errors.append(f"status is '{status}' but {len(open_items)} open question(s) are unticked")

    return errors, warnings


def main(argv: list[str]) -> int:
    paths = [Path(a) for a in argv] or sorted(p for p in SPECS.glob("*.md") if not p.name.startswith("_"))
    total_err = 0
    lines = ["### Spec format check", ""]
    for p in paths:
        errors, warnings = check(p)
        total_err += len(errors)
        rel = p.resolve().relative_to(ROOT) if p.resolve().is_relative_to(ROOT) else p
        mark = "❌" if errors else ("⚠️" if warnings else "✅")
        print(f"{mark} {rel}")
        lines.append(f"- {mark} `{rel}`")
        for e in errors:
            print(f"    error:   {e}")
            lines.append(f"  - error: {e}")
        for w in warnings:
            print(f"    warning: {w}")
            lines.append(f"  - warning: {w}")
    if summary := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
    return 1 if total_err else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
