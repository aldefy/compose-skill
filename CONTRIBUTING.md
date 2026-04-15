# Contributing

## Cutting a release

Five version locations must agree on every release. The
`scripts/check-versions.sh` script enforces this and is run by CI on every
tag push. Maintainer flow:

1. **Bump the five version locations** to the new semver string (e.g. `2.2.0`):
   - `.claude-plugin/plugin.json` → `version`
   - `.copilot/plugin.yaml` → `version`
   - `jetpack-compose-expert-skill/SKILL.md` → frontmatter `version:`
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
