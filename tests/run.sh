#!/usr/bin/env bash
# Runs both suites inside the sandbox, writes reports to $REPORT_DIR, and records the
# combined exit code in $REPORT_DIR/exit_code so CI can read it after copying reports out.
set -u
mkdir -p "$REPORT_DIR"

python3 -m pytest /tests/api -q --junitxml="$REPORT_DIR/api-junit.xml"
api=$?

(cd /tests/ui && npx playwright test)
ui=$?

code=$(( api != 0 || ui != 0 ))
echo "$code" > "$REPORT_DIR/exit_code"
echo "api=$api ui=$ui -> exit $code"
exit "$code"
