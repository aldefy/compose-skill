<p align="center">
  <img src="https://developer.android.com/static/images/jetpack/compose/compose-logo.svg" width="80" alt="Jetpack Compose logo"/>
</p>

<h1 align="center">Jetpack Compose Agent Skill</h1>

<p align="center">
  Make your AI coding tool actually understand Compose.<br/>
  Backed by real <code>androidx/androidx</code> source code — not vibes.
</p>

<p align="center">
  <a href="#setup"><img src="https://img.shields.io/badge/setup-5%20min-brightgreen" alt="Setup time"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License"/></a>
  <a href="https://developer.android.com/jetpack/compose"><img src="https://img.shields.io/badge/Jetpack%20Compose-1.7+-4285F4" alt="Compose version"/></a>
  <a href="https://kotlinlang.org"><img src="https://img.shields.io/badge/Kotlin-2.0+-7F52FF" alt="Kotlin version"/></a>
</p>

---

## The problem

AI coding tools generate Compose code that compiles but gets the details wrong. Incorrect `remember` usage, unstable recompositions, broken modifier ordering, deprecated navigation patterns, hallucinated APIs that don't exist. They guess at behavior instead of knowing it.

This skill fixes that by giving your AI assistant two things:

1. **12 reference guides** covering every major Compose topic with do/don't examples and common pitfalls
2. **5 source code files** pulled directly from [`androidx/androidx`](https://github.com/androidx/androidx/tree/androidx-main/compose) so the agent can check how things actually work

Think of it as the Compose equivalent of [AvdLee/SwiftUI-Agent-Skill](https://github.com/AvdLee/SwiftUI-Agent-Skill) — same idea, Android/Kotlin world.

## What changes when you install it

| Area | Without the skill | With it |
|---|---|---|
| State | Uses `remember { mutableStateOf() }` everywhere, even when `derivedStateOf` or `rememberSaveable` is the right call | Picks the right state primitive for each situation |
| Performance | Generates code that recomposes every frame | Applies stability annotations, deferred reads, `key {}` on lists |
| Navigation | String-based routes (deprecated) | Type-safe routes with `@Serializable` route classes |
| Modifiers | Random ordering, misses `clickable` before `padding` bugs | Correct ordering with reasoning |
| Side effects | Wrong coroutine scope, bad `LaunchedEffect` keys | Correct effect selection and lifecycle-aware keys |
| APIs | Hallucinates parameters that don't exist | Checks against actual source before suggesting |

## What's covered

| Topic | What the agent learns |
|---|---|
| State management | `remember`, `mutableStateOf`, `derivedStateOf`, `rememberSaveable`, state hoisting, `snapshotFlow` |
| View composition | Structuring composables, slot APIs, `@Preview` patterns, extraction rules |
| Performance | Recomposition skipping, `@Stable`/`@Immutable`, deferred reads, baseline profiles, benchmarking |
| Navigation | Type-safe routes, `NavHost`, deep links, shared element transitions, back stack |
| Animation | `animate*AsState`, `AnimatedVisibility`, `Crossfade`, `updateTransition`, shared transitions |
| Lists and scrolling | `LazyColumn`/`LazyRow`/`LazyGrid`, `Pager`, `key {}`, `contentType`, scroll state |
| Side effects | `LaunchedEffect`, `DisposableEffect`, `SideEffect`, `rememberCoroutineScope` |
| Modifiers | Ordering rules, custom modifiers, `Modifier.Node` migration |
| Theming | `MaterialTheme`, `ColorScheme`, dynamic color, `Typography`, shapes, dark theme |
| Accessibility | Semantics, content descriptions, traversal order, touch targets, TalkBack |
| CompositionLocals | `LocalContext`, `LocalDensity`, custom locals, when to use vs. parameter passing |
| Deprecated patterns | Removed APIs, migration paths from older Compose versions |
| Source code | Actual `.kt` from `androidx/androidx` for runtime, UI, foundation, material3, navigation |

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
        +-- ... (12 guides total)
        |
        +-- source-code/
              +-- runtime-source.md
              +-- material3-source.md
              +-- ... (5 source files)
```

**Layer 1: guidance docs** (12 files, ~120KB) — practical references with patterns, pitfalls, and do/don't examples. This is what the agent reads first.

**Layer 2: source code receipts** (5 files, ~2.3MB) — the actual Kotlin source from `androidx/androidx` (branch: `androidx-main`). When the agent needs to verify an implementation detail rather than guess, it reads these.

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
    └── source-code/                      # Actual .kt source from androidx/androidx
        ├── runtime-source.md             # Composer, Recomposer, State, Effects
        ├── ui-source.md                  # AndroidCompositionLocals, Modifier, Layout
        ├── foundation-source.md          # LazyList, BasicTextField, Gestures
        ├── material3-source.md           # MaterialTheme, all M3 components
        └── navigation-source.md          # NavHost, ComposeNavigator
```

## Setup

The skill is just markdown files. Every tool below reads the same content. Pick yours.

---

### Codex CLI (OpenAI)

Point to the skill file directly:

```bash
codex --instructions jetpack-compose-expert-skill/SKILL.md
```

Or reference it from `AGENTS.md` in your project root:

```markdown
# AGENTS.md

## Jetpack Compose
For all Compose/Android UI tasks, follow the instructions in
`jetpack-compose-expert-skill/SKILL.md` and consult the reference
files in `jetpack-compose-expert-skill/references/` before answering.
```

Add to your project as a submodule:

```bash
git submodule add git@github.com:aldefy/compose-skill.git .compose-skill
```

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

Add to `.windsurfrules` in your project root:

```markdown
For all Jetpack Compose tasks, follow the workflow in
`jetpack-compose-expert-skill/SKILL.md` and consult the reference
files in `jetpack-compose-expert-skill/references/` before answering.
```

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

All source code comes from [`androidx/androidx`](https://github.com/androidx/androidx/tree/androidx-main/compose) under Apache License 2.0. The guidance docs are original analysis of those sources plus official Android documentation.

## Contributing

PRs welcome, especially:
- Coverage for new Compose APIs or patterns
- Corrections based on newer Compose releases
- Additional source files for gaps
- Compose Multiplatform (Desktop, iOS, Web) guidance
- Auto-update tooling for tracking new `androidx` releases

## License

MIT — see [LICENSE](LICENSE).

Source code from `androidx/androidx` is Apache License 2.0, copyright The Android Open Source Project.
