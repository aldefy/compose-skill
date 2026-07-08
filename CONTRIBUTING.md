# Contributing

## Cutting a release

Five version locations must agree on every release. The
`scripts/check-versions.sh` script enforces this and is run by CI on every
tag push. Maintainer flow:

1. **Bump the five version locations** to the new semver string (e.g. `2.2.0`):
   - `.claude-plugin/plugin.json` → `version`
   - `.copilot/plugin.yaml` → `version`
   - `skills/compose-expert/SKILL.md` → frontmatter `version:`
   - The git tag you will push (e.g. `v2.2.0`)
   - `CHANGELOG.md` → new `## [2.2.0] - YYYY-MM-DD` heading
2. **Update `CHANGELOG.md`** with an entry that includes, for any breaking
   change, a `### Migration notes` subsection.
3. **Run the version check locally** before tagging:

   ```
   bash scripts/check-versions.sh v2.2.0
   ```

   Expected: `OK: versions aligned at 2.2.0`.
4. **Commit, tag, and push**:

   ```
   git add -A
   git commit -m "release: v2.2.0"
   git tag v2.2.0
   git push && git push --tags
   ```
5. **Verify the GitHub Release** was created by the `release.yml` workflow.
   It should contain the CHANGELOG section plus the install/update header.

## Semver rules for skill content

| Change type | Bump |
|---|---|
| Typo fix, link fix, small rewording | patch |
| New reference file, new example, clarifying text | minor |
| Plugin manifest schema change (new host, new field) | minor |
| Removed/renamed reference, changed trigger routing, banner escalation | major |

## Pre-release validation checklist

Run before tagging a release:

- [ ] Fresh Claude Code install: marketplace add + install works; SKILL.md loads.
- [ ] `/plugin update` picks up a trivial change tagged as the next patch.
- [ ] Copilot CLI install works.
- [ ] Codex symlink install works.
- [ ] Stale-install banner surfaces when old-format SKILL.md (no `version:`) is loaded.

## Verifiable layout claims

Reference docs can assert Compose layout behavior that CI executes. For measured
layout claims, mark a fenced block `kotlin verify`, give it a unique `// name:`,
declare `// assert: width = N.dp` / `// assert: height = N.dp`, and define
`@Composable fun Subject()`:

    ```kotlin verify
    // name: my-claim
    // assert: width = 100.dp
    @Composable fun Subject() { Box(Modifier.size(100.dp)) }
    ```

For snippets that should compile but do not need a measured assertion, use
`kotlin compile` with the same `// name:` and `@Composable fun Subject()`
contract:

    ```kotlin compile
    // name: material-theme-provides-tokens
    @Composable fun Subject() {
        MaterialTheme { Text("Hello") }
    }
    ```

`./gradlew :verify-claims:testDebugUnitTest` generates one Robolectric test per
`kotlin verify` block and compile-only subjects for each `kotlin compile` block
(via the `generateClaimTests` task, which harvests top-level files from
`skills/compose-expert/references/`) on a headless JVM — no emulator. A wrong
number fails CI; a missing or stale API in an opt-in compile block fails
compilation. Plain ` ```kotlin ` blocks are illustrative and are not executed.

The executable claim format supports a few trust-oriented knobs:

- `// repeat: N` runs the same claim `N` times to catch flaky or unstable rules.
- `// assert-not: text = "..."` checks that a string is absent from the rendered semantics tree.
- `// assert: has-click-action = "..."` checks clickable semantics on a node with matching text.

The `verify-claims` CI job runs this on every PR and master push.
