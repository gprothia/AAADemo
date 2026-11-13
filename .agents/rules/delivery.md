# Rules: branches, sandbox runs and pull requests

## Branches and commits
- Never commit to `main`. Branch per spec: `feat/<id-lower>-<short-name>`,
  e.g. `feat/ord-002-cancel-order`, from an up-to-date `main`.
- Commit messages: `<ID>: <what changed>`, e.g. `ORD-002: add cancel endpoint and tests`.
- Spec, tests and code for one spec go in the same branch and PR.

## Before opening a PR (all must pass)
1. `python scripts/check_spec.py` — specs are well-formed.
2. `python scripts/check_traceability.py` — every criterion has a test.
3. Local run: API and UI suites green against the app running on this machine.
4. Sandbox run: `scripts/sandbox.sh all` — images built with Cloud Build, deployed to the
   developer's GKE namespace, both suites green there. Read the summary it prints.
   If it fails, fix and re-run; do not open a PR on a red sandbox run.
5. Delete the sandbox when green: `scripts/sandbox.sh down`. Keep it when red, for debugging.

## Pull request
- Create with `gh pr create --base main` and a body that follows
  `.github/pull_request_template.md`: spec link, `Closes #<issue>`, criteria covered, the
  sandbox result (tests passed / total, namespace, image tag), and anything deferred.
- Never merge, approve, or force-push. A person reviews: spec diff, then tests, then code.
- After opening it, print the PR URL and the CI checks that will run.
