# Rules: feature requests (GitHub issues)

A feature request is a GitHub issue that will later become a spec. People create them with the
"Feature spec" form; agents create them with `gh issue create`, which ignores forms, so agents
must reproduce the form's shape exactly.

## Format (must match .github/ISSUE_TEMPLATE/feature-spec.yml)
- Title: `[Spec] <feature name in plain words>`
- Label: `spec`
- Body: these headings, in this order, each `###` level:
  1. `### Spec ID` — next free ID in the area, e.g. `ORD-002`. Find it by listing `specs/` and
     open `spec`-labelled issues (`gh issue list --label spec --state all`). Never reuse an ID.
  2. `### Why` — the user problem and the outcome, 1–3 sentences, no solution details.
  3. `### Acceptance criteria (Given / When / Then)` — a first draft, one block per criterion:
     `### <ID>-AC<n> [api|ui|api,ui]` with Given / When / Then bullets.
  4. `### Edge cases & errors`
  5. `### Open questions` — checkboxes `- [ ]`. Every decision you could not take from the
     requester's words goes here. Never fill a business decision in yourself.

## Behaviour
- Draft the issue body to a file first and show it to the user. Create the issue only after
  they say so.
- Keep the requester's intent; do not add features they didn't ask for. Put ideas under
  Open questions instead.
- After creating it, print the issue number and URL.
