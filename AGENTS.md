# Project rules for coding agents (Antigravity, Claude Code, Gemini CLI, others)

Read this file first, then the rule file for the task in hand:

| Task | Rules | Saved command (Antigravity workflow) |
|---|---|---|
| Raise a feature request | `.agents/rules/feature-requests.md` | `/feature-request <idea>` |
| Write or change a spec | `.agents/rules/specs.md` | `/write-spec #<issue>` |
| Write tests from a spec | `.agents/rules/testing.md` | `/generate-tests specs/<file>` |
| Build a spec end to end, sandbox, PR | `.agents/rules/delivery.md` | `/build-spec specs/<file>` |

The cycle: **issue → spec (approved by a person) → tests → code → local run → GKE sandbox run
→ pull request → CI re-checks → a person merges.**

## Never
- Commit to `main`, merge, approve, or force-push.
- Change a spec's acceptance criteria, or a test, just to make something pass.
- Take a business decision the issue doesn't contain. Ask, or list it as an open question.
- Create issues, comments or PRs before showing the user the text.

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

## The app
- `services/api`: FastAPI, in-memory storage seeded at start (`SEED_TEST_DATA=true`).
  Errors are JSON `{"code": "...", "message": "..."}`; the caller is the `X-User` header.
- `services/web`: FastAPI-rendered pages; browser calls go to `/api/*`, proxied to the API.

## Before you finish
- `python scripts/check_spec.py` and `python scripts/check_traceability.py` pass.
- Both suites pass locally, then in the GKE sandbox (`scripts/sandbox.sh all`).
