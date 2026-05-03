#!/usr/bin/env bats

setup() {
  TEST_DIR=$(mktemp -d)
  cp -R "$BATS_TEST_DIRNAME/.." "$TEST_DIR/repo"
  cd "$TEST_DIR/repo"
  # Read the current version from plugin.json so the test does not rot at
  # every release. Tests verify the script's logic, not a fixed version.
  CURRENT=$(jq -r .version .claude-plugin/plugin.json)
}

teardown() {
  rm -rf "$TEST_DIR"
}

@test "passes when all five versions match (tag passed as arg)" {
  run bash scripts/check-versions.sh "v${CURRENT}"
  [ "$status" -eq 0 ]
  [[ "$output" == *"versions aligned"* ]]
}

@test "fails when plugin.json version diverges" {
  sed -i.bak "s/\"version\": \"${CURRENT}\"/\"version\": \"0.0.1\"/" .claude-plugin/plugin.json
  run bash scripts/check-versions.sh "v${CURRENT}"
  [ "$status" -ne 0 ]
  [[ "$output" == *"plugin.json"* ]]
}

@test "fails when SKILL.md frontmatter version diverges" {
  sed -i.bak "s/^version: ${CURRENT}$/version: 0.0.1/" skills/compose-expert/SKILL.md
  run bash scripts/check-versions.sh "v${CURRENT}"
  [ "$status" -ne 0 ]
  [[ "$output" == *"SKILL.md"* ]]
}

@test "fails when CHANGELOG missing version heading" {
  run bash scripts/check-versions.sh v9.9.9
  [ "$status" -ne 0 ]
  [[ "$output" == *"CHANGELOG"* ]]
}
