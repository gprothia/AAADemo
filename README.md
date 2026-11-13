# Spec → tests → ephemeral GKE sandbox, on every PR

GitHub-native spec-driven testing. Specs are Markdown files in this repo. Antigravity (AGY)
and Gemini turn them into API and UI test suites. GitHub Actions runs those suites against a
throwaway copy of the app in a per-PR namespace on GKE Autopilot.

```
GitHub Issue (feature-spec form)
        │  agreed
        ▼
specs/ORD-001-*.md  ──►  Antigravity: /generate-tests  ──►  tests/api/*.py  + tests/ui/*.spec.ts
   (AC IDs + tags)        (plan → review → write → run)     (each test tagged with its AC ID)
        │                                                          │
        └──────────────── one PR: spec + tests + code ─────────────┘
                                   │
          ┌────────────────────────┼─────────────────────────────┐
          ▼                        ▼                             ▼
  traceability gate        Gemini spec review              build images (SHA)
  (deterministic,          (advisory PR comment:                 │
   blocks merge)            weak tests, spec gaps)               ▼
                                                    namespace pr-<N> on GKE Autopilot
                                                    deploy api + web → run test-runner pod
                                                    → JUnit check + reports artifact
                                   │
                      PR closed / 48h stale → namespace deleted
```

## Why it's split this way

- **Tests are generated at authoring time, in Antigravity, and committed.** They're reviewed
  in the PR like any code. CI never generates tests on the fly and then trusts them, because
  that makes results non-reproducible and lets a model grade its own work.
- **Two checks, different jobs.** `check_traceability.py` is deterministic: every approved
  acceptance criterion must have a tagged test, or the PR fails. Gemini is advisory: it reads
  spec + tests and comments when a test exists but doesn't really check what the spec says.
- **One shared Autopilot cluster, one namespace per PR.** Creating a whole cluster per PR
  takes many minutes. A namespace is created in seconds, and Autopilot only bills for the pods
  you run. Quota, default requests and a NetworkPolicy keep PRs from affecting each other.
- **Tests run inside the cluster.** The app is never exposed publicly. Tests reach it on
  in-namespace DNS (`http://api:8080`, `http://web:3000`).

## Repo layout

| Path | What it is |
|---|---|
| `specs/_TEMPLATE.md`, `specs/ORD-001-*.md` | Spec format + worked example |
| `.github/ISSUE_TEMPLATE/feature-spec.yml` | Issue form that collects a spec in the same shape |
| `.github/pull_request_template.md` | PR checklist linking spec ↔ tests |
| `AGENTS.md`, `.agents/rules/testing.md` | Rules Antigravity (and Gemini CLI) always follow |
| `.agents/workflows/generate-tests.md` | AGY workflow: `/generate-tests specs/<file>.md` |
| `scripts/check_traceability.py` | Deterministic AC → test gate |
| `tests/api`, `tests/ui` | pytest + Playwright suites (examples for ORD-001) |
| `tests/Dockerfile`, `tests/run.sh` | Test-runner image used inside the sandbox |
| `deploy/app` | Placeholder app manifests (swap in yours) |
| `deploy/sandbox` | Namespace, quota, defaults, NetworkPolicy, test-runner pod |
| `.github/workflows/pr-sandbox.yml` | Per-PR pipeline |
| `.github/workflows/pr-sandbox-cleanup.yml` | Teardown on close + stale sweep |
| `.github/gemini/spec-review-prompt.md` | Prompt for the Gemini review comment |

## Day-to-day flow

1. Open an issue with the **Feature spec** form. Discuss until it's agreed.
2. Branch, copy `specs/_TEMPLATE.md` to `specs/<ID>-<name>.md`, fill it in, set
   `status: approved`.
3. In Antigravity, open the repo and run `/generate-tests specs/<ID>-<name>.md`.
   Review its plan (and any "spec questions"), approve, let it write and run the tests.
4. Implement the feature (AGY or by hand) until the tests pass locally.
5. Open the PR. CI posts the Gemini review, deploys `pr-<N>`, runs both suites, and adds a
   "Spec acceptance tests" check with every test linked to its AC ID.
6. Merge. The namespace is deleted automatically.

## One-time Google Cloud setup

Replace the values in the first block, then run the rest in Cloud Shell.

```bash
PROJECT_ID=my-project
REGION=us-west1
GH_REPO=my-org/my-repo
CLUSTER=pr-sandboxes
AR_REPO=pr-sandbox
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')

gcloud services enable container.googleapis.com artifactregistry.googleapis.com \
  aiplatform.googleapis.com iamcredentials.googleapis.com sts.googleapis.com --project $PROJECT_ID

# Shared Autopilot cluster for all PR sandboxes
gcloud container clusters create-auto $CLUSTER --region $REGION --project $PROJECT_ID

# Image registry, with old PR images cleaned up automatically
gcloud artifacts repositories create $AR_REPO --repository-format=docker \
  --location=$REGION --project $PROJECT_ID
#   (add a cleanup policy deleting images older than ~14 days in the console or via
#    `gcloud artifacts repositories set-cleanup-policies`)

# Service account CI impersonates
gcloud iam service-accounts create gh-pr-sandbox --project $PROJECT_ID
SA=gh-pr-sandbox@$PROJECT_ID.iam.gserviceaccount.com
for role in roles/container.developer roles/artifactregistry.writer roles/aiplatform.user; do
  gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA" --role=$role
done

# Workload Identity Federation: GitHub OIDC -> that SA, limited to this repo
gcloud iam workload-identity-pools create github --location=global --project $PROJECT_ID
gcloud iam workload-identity-pools providers create-oidc github \
  --location=global --workload-identity-pool=github --project $PROJECT_ID \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository=='$GH_REPO'"
gcloud iam service-accounts add-iam-policy-binding $SA --project $PROJECT_ID \
  --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github/attribute.repository/$GH_REPO"
```

`roles/container.developer` lets CI create and delete namespaces in the cluster. If you want
tighter control, grant cluster-scoped Kubernetes RBAC to the SA instead and drop that role.

### GitHub repository variables (Settings → Secrets and variables → Actions → Variables)

| Variable | Example |
|---|---|
| `GCP_PROJECT_ID` | `my-project` |
| `GCP_REGION` | `us-west1` |
| `GKE_CLUSTER` | `pr-sandboxes` |
| `AR_REPO` | `pr-sandbox` |
| `WIF_PROVIDER` | `projects/123456789/locations/global/workloadIdentityPools/github/providers/github` |
| `CI_SERVICE_ACCOUNT` | `gh-pr-sandbox@my-project.iam.gserviceaccount.com` |

No secrets are needed: auth is keyless via OIDC.

Then in **Settings → Branches**, make `traceability` and `sandbox-test` required checks.

## Adapting to your app

- Point the `docker build` lines in `pr-sandbox.yml` at your service directories.
- Replace `deploy/app/*.yaml` with your manifests, or swap the deploy step for `helm upgrade
  --install -n $NS`. Keep resource requests set: Autopilot bills on them.
- Databases: run a throwaway Postgres/Redis pod in the namespace (simplest), or create a
  per-PR database on a shared Cloud SQL instance and drop it in the cleanup workflow.
- Seed data: the example expects the API to load `TEST-SKU-1` when `SEED_TEST_DATA=true`.

## Things to know

- **Fork PRs** get no OIDC token, so the Gemini and sandbox jobs skip them. Run those
  manually after review if you accept outside contributions.
- **First run after idle** can take a few extra minutes while Autopilot provisions nodes.
- **Gemini reads PR content.** Its prompt treats the input as data, and its only output is a
  comment, so a malicious spec can at worst produce a misleading comment, never an action.
- **Antigravity paths:** current docs use `.agents/rules/` and `AGENTS.md`/`GEMINI.md`.
  Older AGY builds read `.agent/` (singular); rename the folder if your version doesn't pick
  the rules up.
- Gemini in CI uses the Gemini CLI headless (`gemini -p`) on Vertex AI. You can swap in the
  `google-github-actions/run-gemini-cli` action if you want an interactive `@gemini-cli` bot
  on PRs as well.
