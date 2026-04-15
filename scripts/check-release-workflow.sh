#!/usr/bin/env bash
set -euo pipefail
FILE=.github/workflows/release.yml
[[ -f $FILE ]] || { echo "FAIL: $FILE missing"; exit 1; }
command -v yq > /dev/null || { echo "FAIL: yq not installed"; exit 1; }
yq . "$FILE" > /dev/null || { echo "FAIL: invalid YAML"; exit 1; }
grep -q 'tags:' "$FILE" || { echo "FAIL: no tags trigger"; exit 1; }
grep -q "check-versions.sh" "$FILE" || { echo "FAIL: does not invoke check-versions.sh"; exit 1; }
grep -q "softprops/action-gh-release" "$FILE" || { echo "FAIL: no release action"; exit 1; }
echo "OK: release.yml valid"
