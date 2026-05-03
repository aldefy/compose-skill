---
name: compose-expert
description: >
  Compose and Compose Multiplatform expert for UI development across Android, Desktop,
  iOS, and Web. Use whenever the user mentions Compose APIs (@Composable, remember,
  LaunchedEffect, NavHost, MaterialTheme, LazyColumn, Modifier, recomposition),
  Compose Multiplatform (commonMain, expect/actual, Res.*, ComposeUIViewController,
  UIKitView, ComposeViewport), Android TV (tv-material, D-pad, focus, Carousel),
  Material 3 motion, atomic design systems, design-to-code workflows, Paging 3, or
  navigation. Activates Review Mode on GitHub PR URLs and review phrases ("review
  this PR", "what's wrong with this"). Auto-detects Compose projects on
  session_start. Backed by actual androidx/androidx and JetBrains/compose-multiplatform-core
  source receipts. See "## When this skill applies" in SKILL.md for the full trigger
  surface.
version: 2.3.1
---

> **Installation notice:** This skill is now distributed as a plugin.
> If you copied files into `~/.claude/skills/` manually, you are on an
> unmaintained install path and will not receive updates. Migrate via:
>
>     /plugin marketplace add aldefy/compose-skill
>     /plugin install compose-expert
>
> See [MIGRATION.md](../docs/MIGRATION.md) for Codex and Copilot CLI instructions.
> This banner will remain through v2.x and escalate in v3.0.

## When this skill applies

The frontmatter `description:` is intentionally short to satisfy Codex / Copilot
CLI's 1024-character cap on that field (see issue #12). The full trigger surface
lives here so it stays available to Claude after the skill loads.

### Compose API mentions
`@Composable`, `remember`, `mutableStateOf`, `derivedStateOf`, `rememberSaveable`,
`LaunchedEffect`, `DisposableEffect`, `SideEffect`, `rememberCoroutineScope`,
`Scaffold`, `NavHost`, `NavController`, `MaterialTheme`, `ColorScheme`,
`Typography`, `LazyColumn`, `LazyRow`, `LazyVerticalGrid`, `HorizontalPager`,
`Modifier`, `Modifier.Node`, `recomposition`, `CompositionLocal`, `Style`,
`styleable`, `MutableStyleState`.

### Compose Multiplatform / KMP
`Compose Multiplatform`, `CMP`, `KMP`, `commonMain`, `expect`, `actual`,
`ComposeUIViewController`, `Window` composable, `UIKitView`, `ComposeViewport`,
`Res.drawable`, `Res.string`, `SkikoMain`.

### Android TV
`tv-material`, `tv-foundation`, `Carousel`, `NavigationDrawer` (TV),
`D-pad`, `focus indication`, `FocusRequester` on TV, `10-foot UI`,
`living room`, `tv compose`, `Android TV`, `Google TV`, `leanback migration`.

### Paging 3
`PagingSource`, `Pager`, `PagingConfig`, `PagingData`, `LazyPagingItems`,
`collectAsLazyPagingItems`, `RemoteMediator`, `LoadState`,
`asSnapshot`, `TestPager`, `cachedIn`.

### Design system / design-to-code
`atomic design`, `atoms`, `molecules`, `organisms`, `templates`,
`design tokens`, `design system`, `component library`, `reusable component`,
`Figma to Compose`, `design to compose`, `build this UI`, `implement this design`,
`spec to code`, `redline`.

### Casual phrasing
"my compose screen is slow", "my recomposition is broken",
"how do I pass data between screens", "how do I build a TV app",
"Android UI", "Kotlin UI", "compose layout", "compose navigation",
"compose animation", "compose styles", "desktop compose", "iOS compose",
"compose web".

### Review Mode triggers
Any GitHub PR URL matching `github.com/.*/pull/\d+`, or phrases:
"review this PR", "review this diff", "review this code",
"check this code", "check this diff", "what's wrong with this".
On match, follow `references/pr-review.md` exclusively.

### Session start
Auto-detect Compose projects on `session_start` — see `references/auto-init.md`.

## Quick Routing

Use this table first. Match the user's signal to one reference file and read it before
answering. `source-code/` files are supporting evidence — load a `references/*.md` file
first, then cite `source-code/` for implementation proof when receipts matter.

### State, recomposition, side effects

- **`remember`, `rememberSaveable`, `mutableStateOf` vs `mutableIntStateOf`, state hoisting** → `references/state-management.md`
- **`derivedStateOf`, `snapshotFlow`, StateFlow in UI, recomposition scope boundaries** → `references/state-management.md` (secondary: `references/performance.md`)
- **`LaunchedEffect`, `SideEffect`, `DisposableEffect`, `rememberUpdatedState`, `rememberCoroutineScope`** → `references/side-effects.md`
- **Recomposition frequency, "my screen recomposes too often", stability, `@Stable`/`@Immutable`, Compose compiler metrics, baseline profiles, strong skipping** → `references/performance.md`
- **`CompositionLocal`, ambient values, theming propagation, `LocalContext` misuse, custom locals** → `references/composition-locals.md`

### Animation and motion

- **`animate*AsState`, `AnimatedVisibility`, `Crossfade`, `updateTransition`, `Animatable`, `rememberInfiniteTransition`** → `references/animation.md`
- **Shared element transitions, gesture-driven animation, `Modifier.graphicsLayer`, Canvas drawing, custom motion spec** → `references/animation.md` (secondary: `references/modifiers.md` for `graphicsLayer`)
- **M3 motion tokens, `MotionTokens`, `MotionScheme`, animation duration tokens, M3 easing curves** → `references/material3-motion.md`

### Layout, lists, modifiers

- **`LazyColumn`, `LazyRow`, `LazyVerticalGrid`, `LazyHorizontalGrid`, `key`/`itemKey`, `contentType`, `LazyListState`, scroll state, sticky headers** → `references/lists-scrolling.md`
- **`HorizontalPager`, `VerticalPager`, `PagerState`** → `references/lists-scrolling.md`
- **Modifier chain ordering, custom layout, `Layout`, `SubcomposeLayout`, layout modifier, draw modifier, `Painter`, `Modifier.Node`** → `references/modifiers.md`

### Navigation

- **`NavHost`, `NavController`, back stack, deep links, type-safe `@Serializable` routes, navigation graph, nested graphs** → `references/navigation.md`
- **Migrating from Nav 2 to Nav 3, `NavDisplay`, `NavKey`, `rememberNavBackStack`, `NavBackStackEntry` changes** → `references/navigation-migration.md`
- **Choosing between Nav 2 and Nav 3, type-safe navigation decision, KMP navigation** → `references/navigation-migration.md` (secondary: `references/navigation.md`)

### Paging

- **`PagingSource`, `PagingData`, `Pager` setup, `PagingConfig`, `pagingDataFlow`, invalidation** → `references/paging.md`
- **`LazyPagingItems`, `collectAsLazyPagingItems`, `itemKey`, `itemContentType`, `LoadState` in UI, retry/refresh** → `references/paging.md`
- **`RemoteMediator`, offline-first paging, network + cache paging, `loadState.source.refresh`** → `references/paging-offline.md`
- **Paging with MVI, dual-flow pattern, paging tests (`asSnapshot`, `TestPager`), `CombinedLoadStates`, paging anti-patterns** → `references/paging-mvi-testing.md`

### Theming and design systems

- **`MaterialTheme`, `ColorScheme`, `Typography`, `Shapes`, dynamic color, M3 tokens, color roles** → `references/theming-material3.md`
- **Atom, molecule, organism, template, component hierarchy, design system structure, reusable components, design tokens** → `references/atomic-design.md`
- **Figma → Compose, screenshot → composable, design token translation, spec-to-code, redline interpretation** → `references/design-to-compose.md`
- **`Style {}`, `MutableStyleState`, `Modifier.styleable()` (experimental Foundation Styles API)** → `references/styles-experimental.md`

### Multiplatform and platform-specific

- **iOS/Desktop/Web CMP targets, `expect`/`actual`, `commonMain`, `Res.drawable`, `Res.string`, platform-specific composables** → `references/multiplatform.md`
- **`ComposeUIViewController` (iOS), `Window`/`Tray`/`MenuBar` (Desktop), `UIKitView`, `ComposeViewport` (Web), platform interop** → `references/platform-specifics.md`
- **TV Compose, `androidx.tv`, D-pad focus, `FocusRequester` on TV, `Carousel`, `NavigationDrawer` (TV), 10-foot UI, leanback migration** → `references/tv-compose.md`

### Interop and accessibility

- **Compose inside XML, `AndroidView`, `ComposeView`, `AbstractComposeView`, hybrid migration, View → Compose interop** → `references/view-composition.md`
- **Accessibility, `Modifier.semantics`, TalkBack, touch target size, `contentDescription`, WCAG, traversal order** → `references/accessibility.md`

### Production, review, migration

- **Production crash, ANR, Compose stack trace, `remember` leak, zero-size DrawScope, duplicate keys, stale `derivedStateOf`** → `references/production-crash-playbook.md`
- **PR review, code review, "review this diff", composable anti-patterns, smell detection, GitHub PR URL** → `references/pr-review.md`
- **Deprecated Compose API, "removed in version X", migration from old API, replaced symbols** → `references/deprecated-patterns.md`
- **Experimental opt-in, `@OptIn`, `@ExperimentalFoundationStyleApi`, unstable API usage** → `references/styles-experimental.md` (for Styles); for general guidance, the relevant topic file
- **Session start, project detection, auto-init** → `references/auto-init.md`

### Source-code receipts (cite, don't route to)

- **"Show me the actual implementation", "where in androidx is this", internal Compose mechanics** → load the topic reference first, then cite the matching `references/source-code/*.md` file:
  - Runtime/state internals (Composer, Snapshot, Effects, Remember) → `references/source-code/runtime-source.md`
  - UI/layout/measurement/draw internals → `references/source-code/ui-source.md`
  - Foundation (LazyList, Pager, Clickable, Scrollable, BasicTextField) → `references/source-code/foundation-source.md`
  - Material3 components → `references/source-code/material3-source.md`
  - Navigation Compose internals → `references/source-code/navigation-source.md`
  - CMP entry points (Window, ComposeUIViewController, UIKitView, ComposeViewport) → `references/source-code/cmp-source.md`

# Compose Expert Skill

Non-opinionated, practical guidance for writing correct, performant Compose code —
across Android, Desktop, iOS, and Web. Covers Jetpack Compose and Compose Multiplatform.
Backed by analysis of actual source code from `androidx/androidx` and
`JetBrains/compose-multiplatform-core`.

## Review Mode

**Activate when** the input contains a GitHub PR URL (`github.com/.+/pull/\d+`) or
explicit review phrases: "review this PR", "review this diff", "check this code",
"what's wrong with this".

When Review Mode activates:
1. Do **not** follow the generation workflow below
2. Read `references/pr-review.md` and follow its workflow exclusively
3. Output a structured local review report — do not post to GitHub

## Workflow

When helping with Compose code, follow this checklist:

### 1. Understand the request
- What Compose layer is involved? (Runtime, UI, Foundation, Material3, Navigation)
- Is this a state problem, layout problem, performance problem, or architecture question?
- Is this Android-only or Compose Multiplatform (CMP)?

### 2. Analyze the design (if visual reference provided)
- If the user shares a Figma frame, screenshot, or design spec, consult `references/design-to-compose.md`
- Decompose the design into a composable tree using the 5-step methodology
- Map design tokens to MaterialTheme, spacing to CompositionLocals
- Identify animation needs and consult `references/animation.md` for recipes

### 3. Consult the right reference
Read the relevant reference file(s) from `references/` before answering:

| Topic | Reference File |
|-------|---------------|
| `@State`, `remember`, `mutableStateOf`, state hoisting, `derivedStateOf`, `snapshotFlow` | `references/state-management.md` |
| Structuring composables, slots, extraction, preview | `references/view-composition.md` — for design system structure, also see `references/atomic-design.md` |
| Modifier ordering, custom modifiers, `Modifier.Node` | `references/modifiers.md` |
| `LaunchedEffect`, `DisposableEffect`, `SideEffect`, `rememberCoroutineScope` | `references/side-effects.md` |
| `CompositionLocal`, `LocalContext`, `LocalDensity`, custom locals | `references/composition-locals.md` |
| `LazyColumn`, `LazyRow`, `LazyGrid`, `Pager`, keys, content types | `references/lists-scrolling.md` |
| `NavHost`, type-safe routes, deep links, shared element transitions | `references/navigation.md` |
| `animate*AsState`, `AnimatedVisibility`, `Crossfade`, transitions | `references/animation.md` — for M3 token selection, also see `references/material3-motion.md` |
| `MaterialTheme`, `ColorScheme`, dynamic color, `Typography`, shapes | `references/theming-material3.md` — for motion, see `references/material3-motion.md`; for design tokens, see `references/atomic-design.md` |
| Recomposition skipping, stability, baseline profiles, benchmarking | `references/performance.md` |
| Semantics, content descriptions, traversal order, testing | `references/accessibility.md` |
| Removed/replaced APIs, migration paths from older Compose versions | `references/deprecated-patterns.md` |
| **Styles API** (experimental): `Style {}`, `MutableStyleState`, `Modifier.styleable()` | `references/styles-experimental.md` |
| Figma/screenshot decomposition, design tokens, spacing, modifier ordering | `references/design-to-compose.md` |
| Production crash patterns, defensive coding, state/performance rules | `references/production-crash-playbook.md` |
| Compose Multiplatform, `expect`/`actual`, resources (`Res.*`), migration | `references/multiplatform.md` |
| Desktop (Window, Tray, MenuBar), iOS (UIKitView), Web (ComposeViewport) | `references/platform-specifics.md` |
| TV Compose: Surface, Carousel, NavigationDrawer, Cards, focus, D-pad | `references/tv-compose.md` |
| M3 motion tokens, `MotionTokens`, `MotionScheme`, animation duration, easing | `references/material3-motion.md` |
| PR URL, code review, "review this PR", "what's wrong with this" | `references/pr-review.md` |
| Session start, project detection | `references/auto-init.md` |
| Atomic design, design system, reusable component, component library, design tokens | `references/atomic-design.md` |

### 4. Apply and verify
- Write code that follows the patterns in the reference
- Flag any anti-patterns you see in the user's existing code
- Suggest the minimal correct solution — don't over-engineer

### 4a. Component building mode
When the request involves building a component (composable that renders UI):
- Consult `references/atomic-design.md`
- Classify the component level (atom, molecule, organism, template)
- Apply the "Ask" prompt from Section 5 before scaffolding code
- Ensure the component satisfies the atom contract (modifier, slots, tokens, defaults)

### 5. Cite the source
When referencing Compose internals, point to the exact source file:
```
// See: compose/runtime/runtime/src/commonMain/kotlin/androidx/compose/runtime/Composer.kt
```

## Key Principles

1. **Compose thinks in three phases**: Composition → Layout → Drawing. State reads in each
   phase only trigger work for that phase and later ones.

2. **Recomposition is frequent and cheap** — but only if you help the compiler skip unchanged
   scopes. Use stable types, avoid allocations in composable bodies.

3. **Modifier order matters**. `Modifier.padding(16.dp).background(Color.Red)` is visually
   different from `Modifier.background(Color.Red).padding(16.dp)`.

4. **State should live as low as possible** and be hoisted only as high as needed. Don't put
   everything in a ViewModel just because you can.

5. **Side effects exist to bridge Compose's declarative world with imperative APIs**. Use the
   right one for the job — misusing them causes bugs that are hard to trace.

6. **Compose Multiplatform shares the runtime but not the platform**. UI code in
   `commonMain` is portable. Platform-specific APIs (`LocalContext`, `BackHandler`,
   `Window`) require `expect`/`actual` or conditional source sets.

## Source Code Receipts

Beyond the guidance docs, this skill bundles the **actual source code** from
`androidx/androidx` (branch: `androidx-main`) and `JetBrains/compose-multiplatform-core`
(branch: `jb-main`). When you need to verify how something works internally, or the
user asks "show me the actual implementation", read the raw source from
`references/source-code/`:

| Module | Source Reference | Key Files Inside |
|--------|-----------------|------------------|
| Runtime | `references/source-code/runtime-source.md` | Composer.kt, Recomposer.kt, State.kt, Effects.kt, CompositionLocal.kt, Remember.kt, SlotTable.kt, Snapshot.kt |
| UI | `references/source-code/ui-source.md` | AndroidCompositionLocals.android.kt, Modifier.kt, Layout.kt, LayoutNode.kt, ModifierNodeElement.kt, DrawModifier.kt |
| Foundation | `references/source-code/foundation-source.md` | LazyList.kt, LazyGrid.kt, BasicTextField.kt, Clickable.kt, Scrollable.kt, Pager.kt |
| Material3 | `references/source-code/material3-source.md` | MaterialTheme.kt, ColorScheme.kt, Button.kt, Scaffold.kt, TextField.kt, NavigationBar.kt |
| Navigation | `references/source-code/navigation-source.md` | NavHost.kt, ComposeNavigator.kt, NavGraphBuilder.kt, DialogNavigator.kt |
| CMP | `references/source-code/cmp-source.md` | Window.kt, ComposeUIViewController.kt, UIKitView.kt, ComposeViewport.kt, ResourceReader.kt |

### Two-layer approach
1. **Start with guidance** — read the topic-specific reference (e.g., `references/state-management.md`)
2. **Go deeper with source** — if the user wants receipts or you need to verify, read from `references/source-code/`

### Source tree map
```
androidx/androidx (branch: androidx-main)
├── compose/runtime/runtime/src/commonMain/kotlin/androidx/compose/runtime/
├── compose/ui/ui/src/androidMain/kotlin/androidx/compose/ui/platform/
├── compose/ui/ui/src/commonMain/kotlin/androidx/compose/ui/
├── compose/foundation/foundation/src/commonMain/kotlin/androidx/compose/foundation/
├── compose/material3/material3/src/commonMain/kotlin/androidx/compose/material3/
├── compose/navigation/navigation-compose/src/commonMain/kotlin/androidx/navigation/compose/
├── tv/tv-material/src/main/java/androidx/tv/material3/
└── tv/tv-foundation/src/main/java/androidx/tv/foundation/

compose-multiplatform-core (branch: jb-main)
├── compose/ui/ui/src/desktopMain/kotlin/androidx/compose/ui/window/
├── compose/ui/ui/src/iosMain/kotlin/androidx/compose/ui/window/
├── compose/ui/ui/src/webMain/kotlin/androidx/compose/ui/window/
├── compose/ui/ui/src/skikoMain/kotlin/androidx/compose/ui/
└── compose/foundation/foundation/src/skikoMain/kotlin/androidx/compose/foundation/

compose-multiplatform (resources library)
└── components/resources/library/src/commonMain/
```
