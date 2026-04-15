#!/usr/bin/env bash
set -euo pipefail

# Validates .claude-plugin/plugin.json against the schema Claude Code actually enforces.
# Derived from the validator's observed error messages (v1 Claude Code) and cross-checked
# against the shipping superpowers plugin. Catches the bugs that got past human review in
# v2.1.0 and v2.1.1.

FILE=".claude-plugin/plugin.json"

fail=0
err() { echo "FAIL: $1"; fail=1; }

[[ -f $FILE ]] || { echo "FAIL: $FILE missing"; exit 1; }
jq . "$FILE" > /dev/null || { echo "FAIL: invalid JSON"; exit 1; }

# Required fields
for field in name version description; do
  jq -e ".${field}" "$FILE" > /dev/null 2>&1 || err "missing required field: $field"
done

# repository MUST be a string, not an object (this is what Claude Code rejects)
repo_type=$(jq -r '.repository | type' "$FILE")
if [[ "$repo_type" != "string" ]]; then
  err "repository must be a string URL, got: $repo_type"
fi

# skills field MUST NOT exist — Claude Code auto-discovers from skills/ directory
if jq -e '.skills' "$FILE" > /dev/null 2>&1; then
  err "plugin.json must not declare 'skills' — skills are auto-discovered from the skills/ directory"
fi

# homepage, if present, must be a string
if jq -e '.homepage' "$FILE" > /dev/null 2>&1; then
  ht=$(jq -r '.homepage | type' "$FILE")
  [[ "$ht" == "string" ]] || err "homepage must be a string, got: $ht"
fi

# author, if present, must be an object with name
if jq -e '.author' "$FILE" > /dev/null 2>&1; then
  at=$(jq -r '.author | type' "$FILE")
  [[ "$at" == "object" ]] || err "author must be an object, got: $at"
  jq -e '.author.name' "$FILE" > /dev/null 2>&1 || err "author.name required"
fi

# version must look like semver
ver=$(jq -r '.version' "$FILE")
if ! [[ "$ver" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.]+)?$ ]]; then
  err "version '$ver' is not valid semver"
fi

# Skills MUST be auto-discoverable: skills/<name>/SKILL.md must exist
shopt -s nullglob
skill_files=(skills/*/SKILL.md)
if [[ ${#skill_files[@]} -eq 0 ]]; then
  err "no skills found — expected at least one skills/<name>/SKILL.md"
fi

# Each SKILL.md must have YAML frontmatter with name + description
for sf in "${skill_files[@]}"; do
  head -1 "$sf" | grep -q '^---$' || err "$sf: missing YAML frontmatter opening"
  awk '/^---$/{c++; if (c==2) exit} c==1 && /^name:/{found=1} END{exit !found}' "$sf" \
    || err "$sf: frontmatter missing 'name:' field"
  awk '/^---$/{c++; if (c==2) exit} c==1 && /^description:/{found=1} END{exit !found}' "$sf" \
    || err "$sf: frontmatter missing 'description:' field"
done

if [[ $fail -ne 0 ]]; then
  exit 1
fi

echo "OK: plugin manifest valid ($FILE)"
