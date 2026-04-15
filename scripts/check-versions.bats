#!/usr/bin/env bats

setup() {
  TEST_DIR=$(mktemp -d)
  cp -R "$BATS_TEST_DIRNAME/.." "$TEST_DIR/repo"
  cd "$TEST_DIR/repo"
}

teardown() {
  rm -rf "$TEST_DIR"
}

@test "passes when all five versions match (tag passed as arg)" {
  run bash scripts/check-versions.sh v2.1.2
  [ "$status" -eq 0 ]
  [[ "$output" == *"versions aligned"* ]]
}

@test "fails when plugin.json version diverges" {
  sed -i.bak 's/"version": "2.1.2"/"version": "2.0.1"/' .claude-plugin/plugin.json
  run bash scripts/check-versions.sh v2.1.2
  [ "$status" -ne 0 ]
  [[ "$output" == *"plugin.json"* ]]
}

@test "fails when SKILL.md frontmatter version diverges" {
  sed -i.bak 's/^version: 2.1.2$/version: 2.0.1/' skills/compose-expert/SKILL.md
  run bash scripts/check-versions.sh v2.1.2
  [ "$status" -ne 0 ]
  [[ "$output" == *"SKILL.md"* ]]
}

@test "fails when CHANGELOG missing version heading" {
  run bash scripts/check-versions.sh v9.9.9
  [ "$status" -ne 0 ]
  [[ "$output" == *"CHANGELOG"* ]]
}
