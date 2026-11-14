#!/usr/bin/env bash
# Developer sandbox on GKE Autopilot: build images with Cloud Build, deploy this branch to its
# own namespace, run the API + UI suites inside the cluster, and copy the reports back.
#
#   scripts/sandbox.sh all     build + up + test   (what /build-spec runs)
#   scripts/sandbox.sh build   build and push api, web and tests images (Cloud Build, no local Docker)
#   scripts/sandbox.sh up      create/refresh the namespace and deploy the app
#   scripts/sandbox.sh test    run the test-runner pod and fetch reports
#   scripts/sandbox.sh down    delete the namespace
#   scripts/sandbox.sh status  show what's running
#
# Needs: gcloud (logged in: `gcloud auth login`), kubectl, python3, git.
# Settings: deploy/sandbox/sandbox.env (PROJECT_ID, REGION, CLUSTER, AR_REPO).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# --- settings ---------------------------------------------------------------
if [[ -f deploy/sandbox/sandbox.env ]]; then
  while IFS='=' read -r key value; do
    [[ -z "$key" || "$key" =~ ^# ]] && continue
    [[ -z "${!key:-}" ]] && export "$key=$value"
  done < deploy/sandbox/sandbox.env
fi
for v in PROJECT_ID REGION CLUSTER AR_REPO; do
  if [[ -z "${!v:-}" || "${!v}" == your-* ]]; then
    echo "error: set $v in deploy/sandbox/sandbox.env (see README: Google Cloud setup)" >&2; exit 2
  fi
done
AR="${REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPO}"

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
SLUG="$(echo "$BRANCH" | tr '[:upper:]' '[:lower:]' | sed -E 's#[^a-z0-9]+#-#g; s#^-+|-+$##g' | cut -c1-40)"
export NS="${SANDBOX_NS:-dev-${SLUG}}"
TAG="dev-$(git rev-parse --short HEAD)"
if [[ -n "$(git status --porcelain -- services tests deploy)" ]]; then
  TAG="${TAG}-wip$(date +%s)"   # uncommitted changes: never reuse an image tag
fi
TAG_FILE="deploy/overlay-dev/.tag"
REPORTS="reports/${NS}"

render() { python3 -c 'import os,sys; sys.stdout.write(os.path.expandvars(sys.stdin.read()))'; }
log() { printf '\n\033[1m==> %s\033[0m\n' "$*"; }

credentials() {
  gcloud container clusters get-credentials "$CLUSTER" --region "$REGION" --project "$PROJECT_ID" >/dev/null
}

# --- steps -----------------------------------------------------------------
build() {
  log "Building images with Cloud Build (tag $TAG)"
  for svc in api web; do
    gcloud builds submit "services/$svc" --tag "$AR/$svc:$TAG" --project "$PROJECT_ID" --region "$REGION" --quiet
  done
  gcloud builds submit tests --tag "$AR/tests:$TAG" --project "$PROJECT_ID" --region "$REGION" --quiet
  mkdir -p deploy/overlay-dev && echo "$TAG" > "$TAG_FILE"
}

current_tag() {
  [[ -f "$TAG_FILE" ]] || { echo "error: no images built yet - run: scripts/sandbox.sh build" >&2; exit 3; }
  cat "$TAG_FILE"
}

up() {
  local tag; tag="$(current_tag)"
  credentials
  log "Deploying $BRANCH ($tag) to namespace $NS"
  SANDBOX_KIND=dev PR_NUMBER=none SHA="$tag" CREATED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    render < deploy/sandbox/namespace.yaml | kubectl apply -f -
  cat > deploy/overlay-dev/kustomization.yaml <<EOF
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: ${NS}
resources: ["../app"]
images:
  - { name: api, newName: ${AR}/api, newTag: "${tag}" }
  - { name: web, newName: ${AR}/web, newTag: "${tag}" }
EOF
  kubectl apply -k deploy/overlay-dev
  echo "Waiting for the app (Autopilot may need a few minutes to add capacity)..."
  kubectl -n "$NS" rollout status deploy/api --timeout=10m
  kubectl -n "$NS" rollout status deploy/web --timeout=10m
}

test_run() {
  local tag code=""; tag="$(current_tag)"
  credentials
  log "Running API + UI suites inside $NS"
  kubectl -n "$NS" delete pod test-runner --ignore-not-found --wait=true
  TEST_IMAGE="$AR/tests:$tag" render < deploy/sandbox/test-runner.yaml | kubectl apply -f -
  kubectl -n "$NS" wait pod/test-runner --for=condition=Ready --timeout=10m || true
  kubectl -n "$NS" logs -f pod/test-runner -c tests || true
  for _ in $(seq 1 60); do
    code="$(kubectl -n "$NS" get pod test-runner \
      -o jsonpath='{.status.containerStatuses[?(@.name=="tests")].state.terminated.exitCode}')"
    [[ -n "$code" ]] && break; sleep 5
  done
  rm -rf "$REPORTS" && mkdir -p "$REPORTS"
  kubectl -n "$NS" cp test-runner:/reports "$REPORTS" -c results >/dev/null 2>&1 || echo "warning: could not copy reports"
  summarize "$tag" "${code:-1}"
  [[ "${code:-1}" == "0" ]]
}

summarize() {
  python3 - "$REPORTS" "$NS" "$1" "$2" <<'EOF'
import glob, sys, xml.etree.ElementTree as ET
reports, ns, tag, code = sys.argv[1:]
total = failed = 0
fails = []
for f in glob.glob(f"{reports}/*-junit.xml"):
    for case in ET.parse(f).getroot().iter("testcase"):
        total += 1
        if case.find("failure") is not None or case.find("error") is not None:
            failed += 1
            fails.append(f"  - {case.get('classname','')}::{case.get('name')}")
status = "PASSED" if code == "0" and total else "FAILED"
print(f"\nSandbox result: {status} - {total - failed}/{total} tests passed "
      f"(namespace {ns}, images {tag}, reports in {reports}/)")
print("\n".join(fails))
EOF
}

down() {
  credentials
  log "Deleting namespace $NS"
  kubectl delete namespace "$NS" --ignore-not-found --wait=false
}

status() {
  credentials
  kubectl -n "$NS" get pods,svc 2>/dev/null || echo "namespace $NS does not exist"
}

case "${1:-}" in
  build) build ;;
  up) up ;;
  test) test_run ;;
  down) down ;;
  status) status ;;
  all) build; up; test_run ;;
  *) sed -n '2,13p' "$0"; exit 1 ;;
esac
