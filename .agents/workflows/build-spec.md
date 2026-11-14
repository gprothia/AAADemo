---
description: Build an approved spec end to end - tests, code, local run, GKE sandbox run, pull request
---

# /build-spec

Usage: `/build-spec specs/<ID>-<name>.md`
Example: `/build-spec specs/ORD-002-cancel-order.md`

Read first and follow throughout: `AGENTS.md`, `.agents/rules/specs.md`,
`.agents/rules/testing.md`, `.agents/rules/delivery.md`.

## 0. Preconditions
// turbo
1. `python scripts/check_spec.py <spec>` passes and the spec says `status: approved`.
   If not, stop and tell the user to finish `/write-spec`.
2. You are on the spec's `feat/...` branch (create it from current `main` if not).

## 1. Plan (wait for approval)
3. List each acceptance criterion and the tests you will add (file + test name), and the
   code changes (API endpoints, pages, data). Note anything in the spec that is ambiguous.
   Stop and wait for the user to approve the plan.

## 2. Tests first
4. Write the tests as in `.agents/workflows/generate-tests.md`: pytest in `tests/api/`,
   Playwright in `tests/ui/`, each tagged with its AC ID.
// turbo
5. `python scripts/check_traceability.py` must pass.
6. Start the app locally and run the suites. New tests should FAIL now (feature not built).
   Show the user the failing list - this is the definition of done.
   - `cd services/api && uvicorn app:app --port 8080`
   - `cd services/web && API_URL=http://localhost:8080 uvicorn app:app --port 3000`
   - `API_BASE_URL=http://localhost:8080 pytest tests/api -q`
   - `cd tests/ui && WEB_BASE_URL=http://localhost:3000 API_BASE_URL=http://localhost:8080 npx playwright test`

## 3. Build the feature
7. Change `services/api` and `services/web` until ALL tests pass - new and existing.
   Never edit a test or the spec to make it pass; if one is wrong, stop and say why.
8. Use the browser to click through each [ui] criterion and show the user screenshots.
9. Commit: `<ID>: implement <feature>`.

## 4. Container build, GKE deploy, sandbox test
// turbo
10. `scripts/sandbox.sh all` - builds the three images with Cloud Build, deploys to your
    namespace on the GKE Autopilot cluster, runs both suites there, copies reports to
    `reports/<namespace>/`. Takes a few minutes on first run.
11. If it fails: read `reports/<namespace>/` and the printed logs, fix, commit, repeat step 10.
12. When green: `scripts/sandbox.sh down`.

## 5. Pull request
13. Set the spec's `status: implemented`, commit, and push: `git push -u origin HEAD`.
14. Write the PR body to `.tmp/pr.md` following `.github/pull_request_template.md`, including
    `Closes #<issue>` and the sandbox result line printed in step 10.
15. `gh pr create --base main --title "<ID>: <title>" --body-file .tmp/pr.md`
16. Print the PR URL. Tell the user CI will now run the same checks independently
    (traceability, Gemini review, build, PR sandbox) and that a person must review and merge.
