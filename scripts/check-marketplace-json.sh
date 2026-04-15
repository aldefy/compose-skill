#!/usr/bin/env bash
set -euo pipefail
FILE=.claude-plugin/marketplace.json
[[ -f $FILE ]] || { echo "FAIL: $FILE missing"; exit 1; }
jq . "$FILE" > /dev/null || { echo "FAIL: invalid JSON"; exit 1; }
[[ $(jq -r .name "$FILE") == "aldefy-compose-skill" ]] || { echo "FAIL: marketplace name wrong"; exit 1; }
[[ $(jq -r '.plugins | length' "$FILE") == "1" ]] || { echo "FAIL: expected 1 plugin"; exit 1; }
[[ $(jq -r '.plugins[0].name' "$FILE") == "compose-expert" ]] || { echo "FAIL: plugin ref wrong"; exit 1; }
[[ $(jq -r '.plugins[0].source' "$FILE") == "./" ]] || { echo "FAIL: plugin source path wrong"; exit 1; }
echo "OK: marketplace.json valid"
