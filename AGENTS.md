# Project rules for coding agents (Antigravity, Gemini CLI, others)

## Specs are the source of truth
- Feature specs live in `specs/*.md`. Each acceptance criterion has a stable ID like `ORD-001-AC3`
  and a tag: `[api]`, `[ui]` or `[api,ui]`.
- Never change a spec's acceptance criteria to make a test pass. If the spec looks wrong,
  stop and say so in the plan.
- Spec changes and test changes go in the same PR as the code they describe.

## Tests are generated from specs
- API tests: `tests/api/`, pytest + httpx. Every test is marked `@pytest.mark.ac("<AC-ID>")`.
- UI tests: `tests/ui/`, Playwright (TypeScript). Every test carries the tag `@<AC-ID>`
  via `test('...', { tag: '@ORD-001-AC4' }, ...)`.
- One AC can have several tests; every non-retired AC must have at least one test in each
  suite its tag names.
- Base URLs come from env vars only: `API_BASE_URL`, `WEB_BASE_URL`. Never hard-code hosts.
- Tests must be independent and safe to run in parallel against a fresh sandbox:
  create their own data, never depend on order, never call real third-party services.
- Prefer role/label locators in Playwright (`getByRole`, `getByLabel`); no CSS-path selectors,
  no fixed `waitForTimeout` sleeps.

## Before you finish
- Run `python scripts/check_traceability.py` and fix anything it reports.
- Run the suites locally (see `.agents/workflows/generate-tests.md`).
