---
description: Turn a plain-language idea into a GitHub feature-request issue in Feature Spec format
---

# /feature-request

Usage: `/feature-request <the idea, in any words>`
Example: `/feature-request customers want to cancel an order before it ships`

Follow `.agents/rules/feature-requests.md` exactly.

1. Read `.github/ISSUE_TEMPLATE/feature-spec.yml` and `.agents/rules/feature-requests.md`.
// turbo
2. Find the next free Spec ID for the area: `ls specs/` and `gh issue list --label spec --state all --limit 100`.
3. Read the specs in the same area (e.g. all `ORD-*`) so the draft fits what already exists
   (field names, error-code style, pages).
4. Write the issue body to `.tmp/feature-request.md` with the five headings from the rules.
   Put every decision the user did not state under **Open questions** as `- [ ]`.
5. Show the user the title and body. Stop and wait for "create it" or edits.
6. Create it: `gh issue create --title "[Spec] <name>" --label spec --body-file .tmp/feature-request.md`
7. Print the issue number and URL, and the next step: `/write-spec #<number>`.
