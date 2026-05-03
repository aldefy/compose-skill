#!/usr/bin/env bash
set -euo pipefail

# Asserts the SKILL.md frontmatter `description:` field is <= 1024 characters.
# Codex CLI and Copilot CLI both reject the manifest when this field exceeds
# 1024 characters (see issue #12). Claude Code does not enforce the cap, so
# without this check a regression ships green on Claude and breaks downstream.

SKILL_FILE="${1:-skills/compose-expert/SKILL.md}"
LIMIT=1024

if [[ ! -f "$SKILL_FILE" ]]; then
  echo "FAIL: $SKILL_FILE not found"
  exit 1
fi

# Extract the description: block from the frontmatter (between first two `---`).
# Handles both inline (`description: ...`) and folded (`description: >\n  ...`)
# YAML forms. Stops at the next top-level frontmatter key.
desc=$(awk '
  /^---$/ { c++; next }
  c == 1 && /^description:/ {
    flag = 1
    sub(/^description: */, "")
    print
    next
  }
  c == 1 && flag && /^[a-zA-Z_]+:/ { exit }
  c == 1 && flag { print }
' "$SKILL_FILE")

len=${#desc}

if (( len > LIMIT )); then
  echo "FAIL: description is $len chars, exceeds $LIMIT-char Codex/Copilot limit"
  echo "      file: $SKILL_FILE"
  echo "      issue: https://github.com/aldefy/compose-skill/issues/12"
  exit 1
fi

echo "OK: description is $len chars (limit $LIMIT)"
