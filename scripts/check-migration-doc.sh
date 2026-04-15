#!/usr/bin/env bash
set -euo pipefail
FILE=docs/MIGRATION.md
[[ -f $FILE ]] || { echo "FAIL: $FILE missing"; exit 1; }
grep -q "How to tell" "$FILE" || { echo "FAIL: missing detection section"; exit 1; }
grep -q "How to migrate" "$FILE" || { echo "FAIL: missing migration section"; exit 1; }
grep -q "version:" "$FILE" || { echo "FAIL: missing frontmatter hint"; exit 1; }
echo "OK: MIGRATION.md valid"
