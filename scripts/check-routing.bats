#!/usr/bin/env bats
# Mutation tests: the routing eval must fail when routing/budgets are broken.

setup() {
  REPO="$(cd "$BATS_TEST_DIRNAME/.." && pwd)"
  WORK="$BATS_TEST_TMPDIR/repo"
  mkdir -p "$WORK"
  cp -R "$REPO/skills" "$REPO/evals" "$REPO/scripts" "$WORK/"
  export ROUTING_ROOT="$WORK"
}

run_check() { run python3 "$WORK/scripts/check-routing.py"; }

@test "passes on current repo state" {
  run_check
  [ "$status" -eq 0 ]
}

@test "fails when a reference is orphaned from SKILL.md" {
  echo "# orphan" > "$WORK/skills/compose-expert/references/orphan-topic.md"
  run_check
  [ "$status" -ne 0 ]
  [[ "$output" == *"orphan reference"* ]]
}

@test "fails when SKILL.md routes to a missing reference" {
  rm "$WORK/skills/compose-expert/references/ink.md"
  run_check
  [ "$status" -ne 0 ]
  [[ "$output" == *"missing reference"* ]]
}

@test "fails when a routing row loses its trigger terms" {
  sed -i.bak 's/`MeshGradientPainter`, //; s/`PolygonShape`, `MorphPolygonShape`, //' "$WORK/skills/compose-expert/SKILL.md"
  sed -i.bak 's/^- \*\*Mesh gradients.*→/- **Gradients** →/' "$WORK/skills/compose-expert/SKILL.md"
  run_check
  [ "$status" -ne 0 ]
  [[ "$output" == *"graphics-modern.md"* ]]
}

@test "fails when an out-of-scope query starts matching a row" {
  sed -i.bak 's/^- \*\*Accessibility,/- **CameraX preview, Accessibility,/' "$WORK/skills/compose-expert/SKILL.md"
  run_check
  [ "$status" -ne 0 ]
  [[ "$output" == *"out-of-scope query matched"* ]]
}

@test "fails when a reference exceeds the byte budget" {
  REF_BUDGET=100 run python3 "$WORK/scripts/check-routing.py"
  [ "$status" -ne 0 ]
  [[ "$output" == *"budget"* ]]
}

@test "fails when SKILL.md exceeds its budget" {
  SKILL_BUDGET=1000 run python3 "$WORK/scripts/check-routing.py"
  [ "$status" -ne 0 ]
  [[ "$output" == *"SKILL.md is"* ]]
}
