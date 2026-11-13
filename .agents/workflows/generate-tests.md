---
description: Turn a spec in specs/ into API (pytest) and UI (Playwright) tests with AC traceability
---

Run this as `/generate-tests specs/<ID>-<name>.md`.

1. Read the spec file given by the user, `AGENTS.md`, and `.agents/rules/testing.md`.
   If the spec's `api:` front matter points at an OpenAPI file, read it too.
2. List every acceptance criterion with its ID and tag ([api], [ui], [api,ui]).
   Skip criteria that are struck through (retired).
3. Check for ambiguity. If any criterion is missing an exact status code, error code,
   field name or visible text, list it under "Spec questions" in your plan and stop for review.
4. Produce an implementation plan: for each AC, the test file and test names you will
   add or change. Wait for approval.
5. Write API tests in `tests/api/test_<spec-id-lower>.py`, each marked
   `@pytest.mark.ac("<AC-ID>")`, using the `api` fixture from `tests/api/conftest.py`.
6. Write UI tests in `tests/ui/<spec-id-lower>.spec.ts`, each tagged `{ tag: '@<AC-ID>' }`.
7. Check traceability:
// turbo
8. `python scripts/check_traceability.py`
9. Run the suites against your local or dev environment:
   `API_BASE_URL=http://localhost:8080 pytest tests/api -q`
   `cd tests/ui && WEB_BASE_URL=http://localhost:3000 npx playwright test`
10. Report: ACs covered, tests added, anything failing and whether it's a code bug,
    a test bug or a spec gap. Use the browser to show the UI flow for any [ui] AC.
