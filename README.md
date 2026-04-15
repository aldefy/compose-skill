<p align="center">
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/jetpackcompose/jetpackcompose-original.svg" width="80" alt="Jetpack Compose logo"/>
</p>

<h1 align="center">Compose Agent Skill</h1>

<p align="center">
  Make your AI coding tool actually understand Compose — Android, Desktop, iOS, and Web.<br/>
  Backed by real source code from <code>androidx/androidx</code> and <code>compose-multiplatform-core</code> — not vibes.
</p>

<p align="center">
  <a href="#setup"><img src="https://img.shields.io/badge/setup-5%20min-brightgreen" alt="Setup time"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License"/></a>
  <a href="https://developer.android.com/jetpack/compose"><img src="https://img.shields.io/badge/Jetpack%20Compose-1.7+-4285F4" alt="Compose version"/></a>
  <a href="https://www.jetbrains.com/lp/compose-multiplatform/"><img src="https://img.shields.io/badge/Compose%20Multiplatform-1.8+-7F52FF" alt="CMP version"/></a>
  <a href="https://kotlinlang.org"><img src="https://img.shields.io/badge/Kotlin-2.0+-7F52FF" alt="Kotlin version"/></a>
</p>

---

## Install

This skill is distributed as a plugin. See **[docs/INSTALL.md](docs/INSTALL.md)** for per-host instructions:

- **Claude Code:** `/plugin marketplace add aldefy/compose-skill` → `/plugin install compose-expert`
- **Copilot CLI:** `copilot plugin install aldefy/compose-skill`
- **Codex CLI:** manual install — see INSTALL.md.

Already installed manually? See **[docs/MIGRATION.md](docs/MIGRATION.md)**.

## Updates

New versions are published as [GitHub Releases](https://github.com/aldefy/compose-skill/releases) with migration notes. Run `/plugin update` (Claude Code) or `copilot plugin update aldefy/compose-skill` (Copilot) to pick them up.

---

## The problem

AI coding tools generate Compose code that compiles but gets the details wrong. Incorrect `remember` usage, unstable recompositions, broken modifier ordering, deprecated navigation patterns, hallucinated APIs that don't exist. They guess at behavior instead of knowing it.

This skill fixes that by giving your AI assistant two things:

1. **20 reference guides** covering every major Compose topic — including Compose Multiplatform, Android TV, Material 3 motion, atomic design systems, design-to-code workflows, animation recipes, and production crash patterns
2. **6 source code files** pulled directly from [`androidx/androidx`](https://github.com/androidx/androidx/tree/androidx-main/compose) and [`compose-multiplatform-core`](https://github.com/JetBrains/compose-multiplatform-core) so the agent can check how things actually work

## What changes when you install it

| Area | Without the skill | With it |
|---|---|---|
| State | Uses `remember { mutableStateOf() }` everywhere, even when `derivedStateOf` or `rememberSaveable` is the right call | Picks the right state primitive for each situation |
| Performance | Generates code that recomposes every frame | Applies stability annotations, deferred reads, `key {}` on lists |
| Navigation | String-based routes (deprecated) | Type-safe routes with `@Serializable` route classes |
| Modifiers | Random ordering, misses `clickable` before `padding` bugs | Correct ordering with reasoning |
| Side effects | Wrong coroutine scope, bad `LaunchedEffect` keys | Correct effect selection and lifecycle-aware keys |
| APIs | Hallucinates parameters that don't exist | Checks against actual source before suggesting |
| Multiplatform | Uses Android-only APIs in shared code | Uses `expect`/`actual`, `Res.*` resources, platform-correct patterns |
| Design-to-code | Literal Figma node translation, wrong modifier ordering | Semantic M3 components, correct ordering, theme tokens |
| Crash safety | No defensive patterns | Guards against zero-size DrawScope, duplicate keys, stale `derivedStateOf` |

## What's covered

| Topic | What the agent learns |
|---|---|
| State management | `remember`, `mutableStateOf`, `derivedStateOf`, `rememberSaveable`, state hoisting, `snapshotFlow` |
| View composition | Structuring composables, slot APIs, `@Preview` patterns, extraction rules |
| Performance | Recomposition skipping, `@Stable`/`@Immutable`, deferred reads, baseline profiles, benchmarking |
| Navigation | Type-safe routes, `NavHost`, deep links, shared element transitions, back stack |
| Animation | `animate*AsState`, `AnimatedVisibility`, `Crossfade`, `updateTransition`, shared transitions, 9 recipes (shimmer, swipe-to-dismiss, etc.), gesture-driven patterns, Figma curve mapping |
| Lists and scrolling | `LazyColumn`/`LazyRow`/`LazyGrid`, `Pager`, `key {}`, `contentType`, scroll state |
| Side effects | `LaunchedEffect`, `DisposableEffect`, `SideEffect`, `rememberCoroutineScope` |
| Modifiers | Ordering rules, custom modifiers, `Modifier.Node` migration |
| Theming | `MaterialTheme`, `ColorScheme`, dynamic color, `Typography`, shapes, dark theme |
| Accessibility | Semantics, content descriptions, traversal order, touch targets, TalkBack |
| CompositionLocals | `LocalContext`, `LocalDensity`, custom locals, when to use vs. parameter passing |
| Deprecated patterns | Removed APIs, migration paths from older Compose versions |
| **Styles API (experimental)** | `Style {}`, `MutableStyleState`, `Modifier.styleable()`, composition, theme integration, alpha06 gotchas |
| **Design-to-code** | Composable decomposition algorithm, Figma property mapping, spacing ownership, modifier ordering, design tokens |
| **Production crash playbook** | 6 crash patterns with root cause + fix, defensive patterns, production state/performance rules |
| **Compose Multiplatform** | CMP architecture, `expect`/`actual`, `Res.*` resources, API availability matrix, migration guide |
| **Platform specifics** | Desktop (Window, Tray, MenuBar), iOS (UIKitView, gotchas), Web/WASM (canvas limitations) |
| **TV Compose** | TV Material3 (Surface, Cards, Carousel, NavigationDrawer, TabRow), focus system, D-pad navigation, theming, immersive list, TVProvider |
| **M3 Motion** | All duration tokens (`DurationShort1–4`, `DurationMedium1–4`, `DurationLong1–4`, `DurationExtraLong1–4`), easing tokens with CubicBezierEasing values, `MotionScheme` API (`defaultSpatialSpec`, `defaultEffectsSpec`), Compose API mapping, decision tree, PR review flags |
| **Atomic design** | 5-level hierarchy (tokens, atoms, molecules, organisms, templates) mapped to Compose, M3 wrapper patterns, custom atom patterns, slot API contracts, token layer, anti-patterns |
| Source code | Actual `.kt` from `androidx/androidx` and `compose-multiplatform-core` for runtime, UI, foundation, material3, navigation, CMP |

## How it works

```
You ask about Compose
        |
        v
  AI reads SKILL.md (workflow + checklists)
        |
        v
  Consults the right reference file
        |
        +-- state-management.md
        +-- performance.md
        +-- navigation.md
        +-- design-to-compose.md
        +-- production-crash-playbook.md
        +-- multiplatform.md
        +-- platform-specifics.md
        +-- tv-compose.md
        +-- ... (20 guides total)
        |
        +-- source-code/
              +-- runtime-source.md
              +-- material3-source.md
              +-- cmp-source.md
              +-- ... (6 source files)
```

**Layer 1: guidance docs** (19 files) — practical references with patterns, pitfalls, and do/don't examples. This is what the agent reads first.

**Layer 2: source code receipts** (6 files) — the actual Kotlin source from `androidx/androidx` and `compose-multiplatform-core`. When the agent needs to verify an implementation detail rather than guess, it reads these.

## File structure

```
jetpack-compose-expert-skill/
├── SKILL.md                              # Main workflow + checklists
└── references/
    ├── state-management.md               # State, remember, hoisting, derivedStateOf
    ├── view-composition.md               # Structuring composables, slots, previews
    ├── modifiers.md                      # Modifier ordering, custom modifiers, Modifier.Node
    ├── side-effects.md                   # LaunchedEffect, DisposableEffect, SideEffect
    ├── composition-locals.md             # CompositionLocal, LocalContext, custom locals
    ├── lists-scrolling.md                # LazyColumn/Row/Grid, Pager, keys, contentType
    ├── navigation.md                     # NavHost, type-safe routes, deep links
    ├── animation.md                      # animate*AsState, AnimatedVisibility, transitions
    ├── theming-material3.md              # MaterialTheme, ColorScheme, dynamic color
    ├── performance.md                    # Recomposition, stability, benchmarking
    ├── accessibility.md                  # Semantics, content descriptions, testing
    ├── deprecated-patterns.md            # Removed APIs, migration paths
    ├── styles-experimental.md           # Styles API (@ExperimentalFoundationStyleApi)
    ├── design-to-compose.md             # Figma/screenshot decomposition, property mapping
    ├── production-crash-playbook.md     # Crash patterns, defensive coding, production rules
    ├── multiplatform.md                 # CMP architecture, expect/actual, Res.*, migration
    ├── platform-specifics.md            # Desktop, iOS, Web/WASM platform APIs and gotchas
    ├── tv-compose.md                    # Android TV: tv-material, Carousel, focus, D-pad
    ├── atomic-design.md                 # Atomic design system: tokens, atoms, molecules, organisms, templates
    └── source-code/                      # Actual .kt source
        ├── runtime-source.md             # Composer, Recomposer, State, Effects
        ├── ui-source.md                  # AndroidCompositionLocals, Modifier, Layout
        ├── foundation-source.md          # LazyList, BasicTextField, Gestures
        ├── material3-source.md           # MaterialTheme, all M3 components
        ├── navigation-source.md          # NavHost, ComposeNavigator
        └── cmp-source.md                # Window, UIKitView, ComposeViewport, Resources
```

## Setup

The skill is just markdown files. Every tool below reads the same content. Pick yours.

---

### Claude Code

Skills are file-based — Claude Code discovers them automatically from `~/.claude/skills/` (personal) or `.claude/skills/` (project-specific).

**Personal skill (available in all your projects):**
> Clone the repo and copy the skill into your personal skills directory:

```bash
git clone https://github.com/aldefy/compose-skill.git /tmp/compose-skill
mkdir -p ~/.claude/skills
cp -r /tmp/compose-skill/jetpack-compose-expert-skill ~/.claude/skills/
```

**Project-specific skill (just one project):**

> Clone the repo and copy the skill into your project's `.claude/skills` directory:

```bash
git clone https://github.com/aldefy/compose-skill.git /tmp/compose-skill
mkdir -p .claude/skills
cp -r /tmp/compose-skill/jetpack-compose-expert-skill .claude/skills/
```

No CLI command or config file needed. Claude Code picks up `SKILL.md` from these directories automatically and triggers when you mention Compose, `@Composable`, `remember`, `LazyColumn`, `NavHost`, etc.

---

### Codex CLI (OpenAI)

Add an `AGENTS.md` file to your project root:

```markdown
# AGENTS.md

## Jetpack Compose
For all Compose/Android UI tasks, follow the instructions in
`jetpack-compose-expert-skill/SKILL.md` and consult the reference
files in `jetpack-compose-expert-skill/references/` before answering.
```

Add the skill to your project as a submodule:

```bash
git submodule add https://github.com/aldefy/compose-skill.git .compose-skill
```

Codex discovers `AGENTS.md` files automatically from the git root down to the current directory.

---

### Gemini CLI (Google)

Add to `GEMINI.md` in your project root:

```markdown
# GEMINI.md

## Jetpack Compose Expert
For all Jetpack Compose tasks, follow the workflow and checklists in
`jetpack-compose-expert-skill/SKILL.md`.

Before answering any Compose question, consult the relevant reference:
- State management -> `jetpack-compose-expert-skill/references/state-management.md`
- Performance -> `jetpack-compose-expert-skill/references/performance.md`
- Navigation -> `jetpack-compose-expert-skill/references/navigation.md`
- (see SKILL.md for the full topic -> file mapping)

For implementation details, check actual source code in
`jetpack-compose-expert-skill/references/source-code/`.
```

Add as a submodule:

```bash
git submodule add git@github.com:aldefy/compose-skill.git .compose-skill
```

---

### Google Antigravity

Antigravity automatically discovers skills from workspace or global skill folders. The `jetpack-compose-expert-skill` directory acts as a complete, ready-to-use Antigravity skill since it contains the needed `SKILL.md` file with a YAML frontmatter description.

**Workspace skill (project-specific):**

```bash
# Clone the repo
git clone https://github.com/aldefy/compose-skill.git /tmp/compose-skill

# Copy into your project's .agents/skills directory
mkdir -p .agents/skills
cp -r /tmp/compose-skill/jetpack-compose-expert-skill .agents/skills/compose-expert
```

**Global skill (available in all your projects):**

```bash
# Clone the repo
git clone https://github.com/aldefy/compose-skill.git /tmp/compose-skill

# Copy into your global Antigravity skills directory
mkdir -p ~/.gemini/antigravity/skills
cp -r /tmp/compose-skill/jetpack-compose-expert-skill ~/.gemini/antigravity/skills/compose-expert
```

---

### Cursor

Create `.cursor/rules/compose-skill.mdc`:

```markdown
---
description: Jetpack Compose expert guidance
globs: **/*.kt
---

Follow the instructions in `jetpack-compose-expert-skill/SKILL.md`
for all Compose-related code. Consult reference files in
`jetpack-compose-expert-skill/references/` before suggesting patterns.
```

Or paste the contents of `SKILL.md` into **Settings > Rules for AI**.

---

### GitHub Copilot

Add to `.github/copilot-instructions.md`:

```markdown
## Jetpack Compose
For Compose/Android UI work, follow the skill instructions in
`jetpack-compose-expert-skill/SKILL.md`. Consult reference files in
`jetpack-compose-expert-skill/references/` for patterns, pitfalls,
and source-code-backed guidance.
```

---

### Windsurf

Create `.windsurf/rules/compose-skill.md` in your project root:

```markdown
For all Jetpack Compose tasks, follow the workflow in
`jetpack-compose-expert-skill/SKILL.md` and consult the reference
files in `jetpack-compose-expert-skill/references/` before answering.
```

> **Note:** The legacy `.windsurfrules` file also works but `.windsurf/rules/` is the current approach.

---

### Amazon Q Developer

Add to `.amazonq/rules/compose.md`:

```markdown
For all Jetpack Compose tasks, follow the workflow in
`jetpack-compose-expert-skill/SKILL.md` and consult the reference
files in `jetpack-compose-expert-skill/references/` before answering.
```

---

### Any other AI coding tool

It's just markdown. Clone this repo into your project (or add as a submodule), then point your tool's instruction file at `jetpack-compose-expert-skill/SKILL.md`. The agent reads `SKILL.md` for the workflow and pulls from `references/` as needed.

## Quick example

After setup, just talk to your AI assistant normally:

```
"My LazyColumn is janky when scrolling — help me fix it"
```

What happens:
1. Agent reads `SKILL.md` for the workflow
2. Pulls in `references/lists-scrolling.md` and `references/performance.md`
3. Checks your code for missing `key {}`, unstable item types, heavy compositions in item blocks
4. If something's unclear, verifies against `references/source-code/foundation-source.md`
5. Gives you a fix based on the actual `LazyList` implementation

No hallucinated APIs. No guessed behavior.

## Source

Source code comes from [`androidx/androidx`](https://github.com/androidx/androidx/tree/androidx-main/compose) and [`JetBrains/compose-multiplatform-core`](https://github.com/JetBrains/compose-multiplatform-core) under Apache License 2.0. The guidance docs are original analysis of those sources plus official documentation.

## Contributing

PRs welcome, especially:
- Additional platform-specific gotchas and workarounds
- New animation recipes for common UI patterns
- Production crash patterns from real apps
- Corrections based on newer Compose/CMP releases
- Auto-update tooling for tracking new releases

## License

MIT — see [LICENSE](LICENSE).

Source code from `androidx/androidx` is Apache License 2.0, copyright The Android Open Source Project. Source code from `compose-multiplatform-core` is Apache License 2.0, copyright JetBrains s.r.o.
