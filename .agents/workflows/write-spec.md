---
description: Turn a feature-request issue into a spec file that passes the spec rules
---

# /write-spec

Usage: `/write-spec #<issue number>`
Example: `/write-spec #4`

Follow `.agents/rules/specs.md` exactly.

// turbo
1. Read the issue and every comment: `gh issue view <n> --comments`.
2. Read `specs/_TEMPLATE.md`, `.agents/rules/specs.md`, and the existing specs in the same area.
// turbo
3. Make sure `main` is current: `git checkout main && git pull`. Create the branch
   `feat/<id-lower>-<short-name>` (see `.agents/rules/delivery.md`).
4. Write `specs/<ID>-<short-name>.md` from the template:
   - decisions come only from the issue and its comments;
   - each acceptance criterion has an exact, checkable **Then**;
   - anything undecided goes under **Open questions** and `status: draft`.
// turbo
5. Validate: `python scripts/check_spec.py specs/<file>`. Fix every error; review every warning.
6. Show the user the spec and list the open questions, if any. Wait for answers.
7. Apply the answers, tick the questions, re-run step 5. When the user says it's agreed, set
   `status: approved` and commit: `<ID>: add spec`.
8. Optionally post the open questions on the issue: `gh issue comment <n> --body-file ...`
   (only if the user asks).
9. Print the next step: `/build-spec specs/<file>`.
