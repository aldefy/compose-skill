# Changelog

All notable changes to this project will be documented in this file.

## [2.3.1] - 2026-05-03

### Fixed

- **`SKILL.md` `description:` frontmatter no longer exceeds Codex / Copilot
  CLI's 1024-character cap** (issue #12). Both hosts rejected the manifest
  with `invalid description: exceeds maximum length of 1024 characters`. The
  field is now 843 chars; Claude Code continues to load it identically.

### Changed

- Long trigger-keyword surface previously packed into the `description:`
  field (TV phrases, casual phrasings, Compose Multiplatform symbol lists,
  Review Mode triggers) is preserved in a new **`## When this skill applies`**
  section in the SKILL.md body. Body content is not subject to the 1024-char
  cap, so the keyword surface remains available to Claude after the skill
  loads.

### Added

- **`scripts/check-description-length.sh`** — a regression check that
  asserts the SKILL.md frontmatter `description:` is ≤ 1024 chars.
- Wired the new check into both `.github/workflows/ci.yml` (every PR) and
  `.github/workflows/release.yml` (every tag push) so a future regression
  fails CI loudly instead of shipping green on Claude Code and breaking
  Codex / Copilot installs.

## [2.3.0] - 2026-05-03

### Added

- **Quick Routing section in `SKILL.md`**. A signal-to-file table at the top of
  the skill so Claude lands on the right reference in one read instead of
  scanning the full topic table. Every reference file is reachable from at
  least one routing entry.
- **Paging 3 references** (3 new files):
  - `references/paging.md` — core setup (`PagingSource`, `Pager`,
    `PagingConfig`, `LazyPagingItems`, `LoadState`, transformations,
    `flatMapLatest` for filter/query reactivity).
  - `references/paging-offline.md` — offline-first with `RemoteMediator`,
    `loadState.source.refresh` vs `loadState.refresh` gotcha. Includes a
    Compose Multiplatform note pointing at SQLDelight as the `commonMain`
    equivalent of Room.
  - `references/paging-mvi-testing.md` — dual-flow MVI pattern (PagingData
    as its own Flow, never inside UiState), `asSnapshot` and `TestPager`
    test recipes, the full anti-pattern table.
- **`references/navigation-migration.md`** — Nav 2 → Nav 3 conceptual shifts,
  mechanical migration steps (`NavKey`, `rememberNavBackStack`, `NavDisplay`,
  entry-scoped ViewModels, deep-link parsing), plus an original
  "Choosing Nav 2 vs Nav 3" decision guide grounded in JetBrains'
  Compose Multiplatform 1.10+ Nav 3 support and the polymorphic-serialisation
  caveat for iOS/web targets.

### Changed

- **Compose Multiplatform equivalents added to Android-leaning examples**:
  - `production-crash-playbook.md` Section 1: `LocalConfiguration` is
    Android-only — added a `commonMain` snippet using
    `LocalWindowInfo.containerSize` plus `LocalDensity`.
  - `production-crash-playbook.md` Rule 3: `rememberSaveable` works in
    `commonMain` via `SaveableStateRegistry`; the ~1 MB `Bundle` limit is
    Android's binder limit, not a CMP property — the per-item-state rule
    still holds across desktop/iOS/web.
  - `paging-offline.md`: top-of-file note clarifying Room is Android-only;
    SQLDelight (`app.cash.sqldelight:androidx-paging3-extensions`) is the
    `commonMain` equivalent. The `LoadState` rule applies identically because
    it's a Paging 3 contract, not a Room property.
  - `navigation.md`: top-of-file callout pointing CMP readers at
    `navigation-migration.md` and Nav 3.

### Source citations

- All `<!-- source: -->` comments in new files were verified against the
  bundled `references/source-code/*.md` receipts. Where a Paging API
  (`LazyPagingItems`, `PagingSource`, `RemoteMediator`, `TestPager`) is **not**
  bundled — it lives in `androidx.paging:*`, a separate library — the file
  notes this explicitly rather than fabricating a citation.

## [2.1.2] - 2026-04-15

### Added

- **Pre-release manifest schema validator** (`scripts/validate-plugin-manifest.sh`
  plus BATS tests) that catches the two bugs that slipped through v2.1.0 and
  v2.1.1: non-string `repository` field, and illegal `skills` field. Also
  asserts that `skills/<name>/SKILL.md` exists with the required frontmatter.
- **CI workflow** (`.github/workflows/ci.yml`) that runs the validator and all
  BATS suites on every PR + push to master. No more shipping broken manifests.
- Release workflow now runs the manifest validator before the version-
  consistency check.

### Install troubleshooting

If `/plugin install` fails with "invalid manifest" after you've already
attempted an install with a broken version (2.1.0 or 2.1.1-pre-rename), Claude
Code's local cache may still hold the bad copy. Clear it:

```
/plugin marketplace remove aldefy/compose-skill
rm -rf ~/.claude/plugins/cache/temp_local_*
/plugin marketplace add aldefy/compose-skill
/plugin install compose-expert
```

## [2.1.1] - 2026-04-15

### Fixed

- **Plugin manifest schema**: `.claude-plugin/plugin.json` was rejected by Claude
  Code's validator. `repository` is now a string URL (was an object), and the
  incorrect `skills` field has been removed — Claude Code auto-discovers skills
  from the top-level `skills/` directory.
- Skill directory moved from `jetpack-compose-expert-skill/` to
  `skills/compose-expert/` to match Claude Code's plugin auto-discovery
  convention.

### Migration notes

- **Fresh installs via `/plugin install compose-expert` now work.**
- **Codex CLI manual-install users** need to update their symlink target:
  `~/.codex/skills-src/compose-skill/skills/compose-expert` instead of the old
  `jetpack-compose-expert-skill` path.

## [2.1.0] - 2026-04-15

### Changed (distribution)

- **Plugin distribution is now the supported install path.** Users who copied
  `jetpack-compose-expert-skill/` into `~/.claude/skills/` (or equivalent) are
  on an unmaintained path. See `docs/MIGRATION.md`.
- `SKILL.md` now carries a `version:` frontmatter field and a migration banner.
  The banner will remain through v2.x and escalate in v3.0.

### Added

- Claude Code plugin manifest (`.claude-plugin/plugin.json`) and marketplace
  entry (`.claude-plugin/marketplace.json`).
- Copilot CLI plugin manifest (`.copilot/plugin.yaml`).
- GitHub Actions release workflow that asserts version consistency across five
  locations and publishes a GitHub Release on every `v*` tag.
- `docs/INSTALL.md` and `docs/MIGRATION.md`.
- `CONTRIBUTING.md` documenting the release flow.

### Migration notes

- **Claude Code:** `/plugin marketplace add aldefy/compose-skill` →
  `/plugin install compose-expert`. Future updates: `/plugin update`.
- **Copilot CLI:** `copilot plugin install aldefy/compose-skill`.
- **Codex CLI:** no native plugin system — see `docs/INSTALL.md` for the
  git-clone + symlink path.

## [2.0.0] - 2026-04-04

### Added
- **Compose Multiplatform support**: CMP architecture guide, API availability matrix, expect/actual patterns, resource system (Res.*), migration from Android-only
- **Platform-specifics guide**: Desktop (Window, Tray, MenuBar, Swing interop), iOS (UIKitView, lifecycle gotchas, binary size), Web/WASM (canvas limitations, no SEO)
- **Design-to-compose guide**: Figma/screenshot decomposition algorithm, property mapping tables, spacing ownership rules, modifier ordering, design token mapping
- **Production crash playbook**: 6 crash patterns with root cause + fix, defensive patterns (SafeShimmerItem, zero-size DrawScope guard, dedup keys), production state/performance rules
- **CMP source code receipts**: Actual API signatures from `compose-multiplatform-core` for Desktop, iOS, Web entry points and interop
- **Animation recipes**: Shimmer, staggered list entrance, swipe-to-dismiss, expandable card, pull-to-refresh, FAB morph, bottom sheet drag, parallax header, animated tabs
- **Animation decision tree**: Which API for which scenario, rendering phase performance guidance
- **Gesture-driven animations**: Swipe-to-dismiss with Animatable, AnchoredDraggable, transformable (pinch/zoom/rotate)
- **Design-to-animation translation**: Figma easing curves to Compose, M3 motion tokens, spring parameter intuition, Figma spring conversion formula
- **Predictive back gesture animation**: NavHost transitions, PredictiveBackHandler, M3 automatic support

### Changed
- Rebranded from "Jetpack Compose" to "Compose" to reflect multiplatform scope
- SKILL.md: Updated name, description, triggers for CMP; added design-to-code workflow step; new reference routing entries; CMP source tree
- README.md: Updated title, badges, coverage table, file structure
- Animation guide: Fixed broken shared element transition code, added 9 recipes, gesture patterns, choreography, production spring specs, new anti-patterns
- State management guide: Added `produceState`, `rememberUpdatedState`, sealed UiState pattern, production state rules, CMP state notes
- Lists/scrolling guide: Added production crash patterns, collision prefix keys, dedupIndex, ReportDrawnWhen, device-specific pagination
- View composition guide: Added 5-step decomposition methodology, Scaffold/screen patterns, composite previews, fixed CompositionLocal explanation, adaptive layouts
- Performance guide: Added zero-size guard, composition tracing, movableContentOf, compiler report flags, production rules, CMP performance notes

### Fixed
- Shared element transition code now uses correct `SharedTransitionLayout` + `SharedTransitionScope` API
- CompositionLocal explanation corrected: `staticCompositionLocalOf` invalidates entire subtree (not "for rarely changing values")
- Removed incorrect `accompanist-permissions` deprecation claim (via PR #1 by @Daiji256)

## [1.1.0] - 2026-03-01

### Added
- Styles API (experimental) reference guide — covers `Style {}`, `MutableStyleState`, `Modifier.styleable()`, composition, theme integration, and alpha06 gotchas

### Fixed
- Claude Code setup: replaced non-existent `claude skill add` CLI command with correct file-based `~/.claude/skills/` and `.claude/skills/` approach
- Codex CLI setup: removed non-existent `--instructions` flag, now uses `AGENTS.md` only
- Windsurf setup: updated from legacy `.windsurfrules` to current `.windsurf/rules/*.md` approach
- Swapped logo to MIT-licensed devicon SVG

## [1.0.0] - 2026-02-28

### Added
- 13 reference guides covering state management, view composition, modifiers, side effects, composition locals, lists/scrolling, navigation, animation, theming (Material3), performance, accessibility, deprecated patterns
- 5 source code files from `androidx/androidx` (runtime, UI, foundation, material3, navigation)
- SKILL.md with workflow, checklists, and two-layer approach (guidance + source receipts)
- Setup instructions for Claude Code, Codex CLI, Gemini CLI, Cursor, GitHub Copilot, Windsurf, and Amazon Q Developer
