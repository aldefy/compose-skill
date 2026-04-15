#!/usr/bin/env bash
set -euo pipefail
FILE=CONTRIBUTING.md
[[ -f $FILE ]] || { echo "FAIL: $FILE missing"; exit 1; }
for keyword in "plugin.json" "plugin.yaml" "SKILL.md" "CHANGELOG.md" "git tag"; do
  grep -q "$keyword" "$FILE" || { echo "FAIL: missing reference to $keyword"; exit 1; }
done
grep -q "check-versions.sh" "$FILE" || { echo "FAIL: missing version-check reference"; exit 1; }
echo "OK: CONTRIBUTING.md valid"
