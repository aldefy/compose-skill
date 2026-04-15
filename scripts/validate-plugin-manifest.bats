#!/usr/bin/env bats

setup() {
  TEST_DIR=$(mktemp -d)
  cp -R "$BATS_TEST_DIRNAME/.." "$TEST_DIR/repo"
  cd "$TEST_DIR/repo"
}

teardown() {
  rm -rf "$TEST_DIR"
}

@test "passes on current repo state" {
  run bash scripts/validate-plugin-manifest.sh
  [ "$status" -eq 0 ]
  [[ "$output" == *"plugin manifest valid"* ]]
}

@test "fails when repository is an object (the v2.1.0 bug)" {
  jq '.repository = {"type":"git","url":"https://x"}' .claude-plugin/plugin.json > tmp.json && mv tmp.json .claude-plugin/plugin.json
  run bash scripts/validate-plugin-manifest.sh
  [ "$status" -ne 0 ]
  [[ "$output" == *"repository must be a string"* ]]
}

@test "fails when skills field is present (the v2.1.0 bug)" {
  jq '.skills = ["../foo"]' .claude-plugin/plugin.json > tmp.json && mv tmp.json .claude-plugin/plugin.json
  run bash scripts/validate-plugin-manifest.sh
  [ "$status" -ne 0 ]
  [[ "$output" == *"must not declare 'skills'"* ]]
}

@test "fails when no skills/<name>/SKILL.md exists" {
  rm -rf skills
  run bash scripts/validate-plugin-manifest.sh
  [ "$status" -ne 0 ]
  [[ "$output" == *"no skills found"* ]]
}

@test "fails when SKILL.md has no name frontmatter" {
  sed -i.bak '/^name:/d' skills/compose-expert/SKILL.md
  run bash scripts/validate-plugin-manifest.sh
  [ "$status" -ne 0 ]
  [[ "$output" == *"missing 'name:'"* ]]
}

@test "fails when version is not semver" {
  jq '.version = "v2"' .claude-plugin/plugin.json > tmp.json && mv tmp.json .claude-plugin/plugin.json
  run bash scripts/validate-plugin-manifest.sh
  [ "$status" -ne 0 ]
  [[ "$output" == *"not valid semver"* ]]
}
