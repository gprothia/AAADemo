---
id: XXX-000            # unique spec ID, e.g. ORD-001. Prefix = area, number = sequence.
title: Short feature name
status: draft          # draft | approved | implemented   (CI enforces tests for approved/implemented)
owner: "@github-handle"
issue: "#123"          # the GitHub issue this spec came from
api: openapi/openapi.yaml   # optional: API contract the API tests should follow
ui_routes: ["/example"]     # optional: pages the UI tests should cover
---

# XXX-000: Short feature name

## Why
One or two sentences on the user problem and the outcome we want.

## Scope
- In: ...
- Out: ...

## Acceptance criteria
<!--
Each criterion gets a stable ID (<spec id>-AC<n>). Never renumber; retire with ~~strikethrough~~.
Tag each one [api], [ui] or [api,ui] so the agent knows which suite(s) must cover it.
Write them as Given / When / Then so they translate 1:1 into tests.
-->

### XXX-000-AC1 [api]
- **Given** ...
- **When** ...
- **Then** ...

### XXX-000-AC2 [ui]
- **Given** ...
- **When** ...
- **Then** ...

## Edge cases & errors
- ...

## Test data
Fixtures or seed data the tests may rely on (no real customer data).

## Open questions
- [ ] ...
