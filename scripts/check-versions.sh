#!/usr/bin/env bash
set -euo pipefail

# Usage: check-versions.sh <expected-version>
# <expected-version> may be "v2.0.0" (with leading v, as from a git tag) or "2.0.0".

EXPECTED="${1:?expected version required, e.g. v2.0.0 or 2.0.0}"
EXPECTED="${EXPECTED#v}"

fail=0

check() {
  local label="$1" actual="$2"
  if [[ "$actual" != "$EXPECTED" ]]; then
    echo "FAIL ($label): got '$actual', expected '$EXPECTED'"
    fail=1
  fi
}

pj=$(jq -r .version .claude-plugin/plugin.json 2>/dev/null || echo "missing")
check "plugin.json" "$pj"

py=$(yq -r .version .copilot/plugin.yaml 2>/dev/null || echo "missing")
check "plugin.yaml" "$py"

sm=$(awk '/^---$/{c++; next} c==1 && /^version:/{print $2; exit}' skills/compose-expert/SKILL.md)
check "SKILL.md" "$sm"

if ! grep -qE "^## \[${EXPECTED}\]" CHANGELOG.md; then
  echo "FAIL (CHANGELOG): no '## [${EXPECTED}]' heading found"
  fail=1
fi

if [[ $fail -ne 0 ]]; then
  exit 1
fi

echo "OK: versions aligned at ${EXPECTED}"
