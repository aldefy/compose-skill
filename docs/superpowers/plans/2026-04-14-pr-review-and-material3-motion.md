# PR Review Mode + Material 3 Motion Reference — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a PR review workflow and Material 3 motion token reference to the compose-expert skill.

**Architecture:** Three file changes — `SKILL.md` gets a Review Mode trigger block + new routing entries; `references/pr-review.md` is a new workflow document; `references/material3-motion.md` is a new content reference sourced entirely from AOSP. All token values in `material3-motion.md` must be fetched from live AOSP source or cross-referenced against `material3-source.md` — no values from model memory.

**Tech Stack:** Markdown, GitHub CLI (`gh`), AOSP `androidx-main` branch source

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `jetpack-compose-expert-skill/SKILL.md` | Modify | Add Review Mode trigger (before Step 1), 2 new routing table rows, cross-reference notes on existing rows |
| `jetpack-compose-expert-skill/references/material3-motion.md` | Create | M3 motion token reference — duration table, easing table, Compose API mapping, decision tree, review flags |
| `jetpack-compose-expert-skill/references/pr-review.md` | Create | PR review workflow — project settings scan, 5-category Compose checklist, output report format |
| `README.md` | Modify | Bump reference count 18→19, add M3 Motion row to coverage table, update "18 guides total" to "19 guides total" |

---

## Task 1: Source M3 Motion Tokens from AOSP

**Files:**
- Read: `jetpack-compose-expert-skill/references/source-code/material3-source.md` (856 KB, already in repo)
- Fetch: Live AOSP `MotionTokens.kt` and `EasingTokens.kt` to verify current values

This task produces the authoritative token data that Task 2 writes into `material3-motion.md`. Do not skip it — values must be verified against source.

- [ ] **Step 1: Search material3-source.md for MotionTokens**

  Run:
  ```bash
  grep -n "DurationShort\|DurationMedium\|DurationLong\|DurationExtraLong" \
    jetpack-compose-expert-skill/references/source-code/material3-source.md | head -60
  ```
  Expected: Lines showing `DurationShort1 = 50.0`, `DurationMedium2 = 300.0`, etc. Note all values.

- [ ] **Step 2: Search material3-source.md for EasingTokens**

  Run:
  ```bash
  grep -n "EasingTokens\|EmphasizedDecelerate\|EmphasizedAccelerate\|StandardDecelerate\|StandardAccelerate\|CubicBezierEasing" \
    jetpack-compose-expert-skill/references/source-code/material3-source.md | head -60
  ```
  Expected: Lines showing `CubicBezierEasing(x1, y1, x2, y2)` values for each named easing curve. Note all four coordinates per curve.

- [ ] **Step 3: Fetch live MotionTokens.kt from AOSP**

  The file lives at:
  `compose/material3/material3/src/commonMain/kotlin/androidx/compose/material3/tokens/MotionTokens.kt`
  on branch `androidx-main` of `androidx/androidx`.

  Use WebFetch or `gh api` to retrieve:
  ```bash
  gh api \
    "repos/androidx/androidx/contents/compose/material3/material3/src/commonMain/kotlin/androidx/compose/material3/tokens/MotionTokens.kt?ref=androidx-main" \
    --jq '.content' | base64 -d
  ```
  If that fails (private repo), use WebFetch on:
  `https://android.googlesource.com/platform/frameworks/support/+/refs/heads/androidx-main/compose/material3/material3/src/commonMain/kotlin/androidx/compose/material3/tokens/MotionTokens.kt?format=TEXT`
  and base64-decode the response.

  Record every `Duration*` constant and its millisecond value.

- [ ] **Step 4: Fetch live EasingTokens.kt from AOSP**

  Same path pattern, file: `EasingTokens.kt` in the same `tokens/` directory.

  ```bash
  gh api \
    "repos/androidx/androidx/contents/compose/material3/material3/src/commonMain/kotlin/androidx/compose/material3/tokens/EasingTokens.kt?ref=androidx-main" \
    --jq '.content' | base64 -d
  ```

  Record every named easing constant and its `CubicBezierEasing(x1, y1, x2, y2)` definition.

- [ ] **Step 5: Cross-check and reconcile**

  Compare values from Steps 1–2 (material3-source.md) against Steps 3–4 (live AOSP). If they differ, the live AOSP value is authoritative — note the discrepancy. This reconciled list is the source of truth for Task 2.

- [ ] **Step 6: Commit sourced data notes**

  ```bash
  # No files to commit yet — data lives in your working notes.
  # Proceed to Task 2 immediately.
  ```

---

## Task 2: Write `material3-motion.md`

**Files:**
- Create: `jetpack-compose-expert-skill/references/material3-motion.md`

Use only the values sourced in Task 1. The structure must match the spec exactly.

- [ ] **Step 1: Verify animation.md for any existing M3 token mentions**

  ```bash
  grep -n "MotionTokens\|DurationMedium\|EmphasizedDecelerate" \
    jetpack-compose-expert-skill/references/animation.md
  ```
  Note what's already there to avoid duplication. `material3-motion.md` should complement, not repeat, `animation.md` API explanations.

- [ ] **Step 2: Write the file**

  Create `jetpack-compose-expert-skill/references/material3-motion.md` with these exact sections in order:

  ```markdown
  # Material 3 Motion Tokens

  Source: `compose/material3/material3/src/commonMain/kotlin/androidx/compose/material3/tokens/`
  in `androidx/androidx` (branch: `androidx-main`)

  CMP compatibility: `MotionTokens` and `EasingTokens` are in `androidx.compose.material3` —
  available on all CMP targets (Android, Desktop, iOS, Web) since M3 1.2.0. No platform guards needed.

  ---

  ## 1. Why Use Motion Tokens

  M3 motion tokens encode the Material Design motion spec. Using them instead of hardcoded
  values ensures animations stay in sync with the design system and are easy to update globally.

  **Never hardcode durations or easing curves.** Use tokens:
  - Consistency: all M3 components use these same tokens
  - Theming: tokens can be overridden at the theme level
  - Reviewability: `tween(MotionTokens.DurationMedium2.toInt())` is self-documenting

  ---

  ## 2. Duration Tokens

  All durations are in milliseconds. Source: `MotionTokens.kt`.

  | Token | Value (ms) | Use Case |
  |-------|-----------|---------|
  | `MotionTokens.DurationShort1` | [sourced value] | Micro interactions — ripple, checkbox tick |
  | `MotionTokens.DurationShort2` | [sourced value] | Small element appear/disappear |
  | `MotionTokens.DurationShort3` | [sourced value] | Icon transitions, selection indicators |
  | `MotionTokens.DurationShort4` | [sourced value] | Tooltip, chip appear |
  | `MotionTokens.DurationMedium1` | [sourced value] | FAB expand, card state change |
  | `MotionTokens.DurationMedium2` | [sourced value] | **Most common** — dialog, bottom sheet, nav transitions |
  | `MotionTokens.DurationMedium3` | [sourced value] | Expanded component transitions |
  | `MotionTokens.DurationMedium4` | [sourced value] | Page-level transitions |
  | `MotionTokens.DurationLong1` | [sourced value] | Complex layout changes |
  | `MotionTokens.DurationLong2` | [sourced value] | Shared element enter |
  | `MotionTokens.DurationLong3` | [sourced value] | Shared element — large content |
  | `MotionTokens.DurationLong4` | [sourced value] | Full container morphs |
  | `MotionTokens.DurationExtraLong1` | [sourced value] | Full-screen transitions only |
  | `MotionTokens.DurationExtraLong2` | [sourced value] | Full-screen transitions only |
  | `MotionTokens.DurationExtraLong3` | [sourced value] | Full-screen transitions only |
  | `MotionTokens.DurationExtraLong4` | [sourced value] | Full-screen transitions only |

  Replace all `[sourced value]` placeholders with actual ms values from Task 1.

  ---

  ## 3. Easing Tokens

  Source: `EasingTokens.kt`. All values are `CubicBezierEasing(x1, y1, x2, y2)`.

  | Token | Cubic Bezier | Direction | Use Case |
  |-------|-------------|-----------|---------|
  | `EmphasizedDecelerateEasing` | [sourced x1, y1, x2, y2] | Entering | Element arriving on screen |
  | `EmphasizedAccelerateEasing` | [sourced x1, y1, x2, y2] | Exiting | Element leaving screen |
  | `EmphasizedEasing` | [sourced x1, y1, x2, y2] | Both | Default for most transitions |
  | `StandardDecelerateEasing` | [sourced x1, y1, x2, y2] | Entering | Simple element enter |
  | `StandardAccelerateEasing` | [sourced x1, y1, x2, y2] | Exiting | Simple element exit |
  | `StandardEasing` | [sourced x1, y1, x2, y2] | Both | Simple state change |
  | `LinearEasing` | 0f, 0f, 1f, 1f | — | Only for repeating/looping animations |

  Replace all `[sourced ...]` placeholders with actual CubicBezierEasing values from Task 1.

  > **Rule:** Enter animations use Decelerate easing (fast start, slow finish — element settles in).
  > Exit animations use Accelerate easing (slow start, fast finish — element leaves quickly).
  > Never use the same easing for both enter and exit.

  ---

  ## 4. Using Tokens in Compose Animation APIs

  ### animate*AsState

  \`\`\`kotlin
  // Color state change — component-level interaction
  val color by animateColorAsState(
      targetValue = if (selected) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.surface,
      animationSpec = tween(
          durationMillis = MotionTokens.DurationShort4.toInt(),
          easing = StandardEasing
      ),
      label = "selection-color"
  )
  \`\`\`

  ### AnimatedVisibility (asymmetric enter/exit)

  \`\`\`kotlin
  // Enter uses DurationMedium2 + Decelerate; exit uses DurationShort4 + Accelerate (faster exit)
  AnimatedVisibility(
      visible = visible,
      enter = fadeIn(
          animationSpec = tween(
              durationMillis = MotionTokens.DurationMedium2.toInt(),
              easing = EmphasizedDecelerateEasing
          )
      ) + slideInVertically(
          animationSpec = tween(
              durationMillis = MotionTokens.DurationMedium2.toInt(),
              easing = EmphasizedDecelerateEasing
          ),
          initialOffsetY = { it / 4 }
      ),
      exit = fadeOut(
          animationSpec = tween(
              durationMillis = MotionTokens.DurationShort4.toInt(),
              easing = EmphasizedAccelerateEasing
          )
      ) + slideOutVertically(
          animationSpec = tween(
              durationMillis = MotionTokens.DurationShort4.toInt(),
              easing = EmphasizedAccelerateEasing
          ),
          targetOffsetY = { it / 4 }
      )
  ) {
      content()
  }
  \`\`\`

  ### updateTransition (multi-property, shared spec)

  \`\`\`kotlin
  val transition = updateTransition(targetState = uiState, label = "card-state")

  val elevation by transition.animateDp(
      transitionSpec = {
          tween(MotionTokens.DurationMedium1.toInt(), easing = EmphasizedEasing)
      },
      label = "elevation"
  ) { state -> if (state.isExpanded) 8.dp else 0.dp }

  val scale by transition.animateFloat(
      transitionSpec = {
          tween(MotionTokens.DurationMedium1.toInt(), easing = EmphasizedEasing)
      },
      label = "scale"
  ) { state -> if (state.isExpanded) 1.05f else 1f }
  \`\`\`

  ### Shared element transitions

  \`\`\`kotlin
  // Shared elements use Long range — they cross screen boundaries
  Modifier.sharedElement(
      state = rememberSharedContentState(key = "hero-${item.id}"),
      animatedVisibilityScope = animatedVisibilityScope,
      boundsTransform = { _, _ ->
          tween(
              durationMillis = MotionTokens.DurationLong2.toInt(),
              easing = EmphasizedEasing
          )
      }
  )
  \`\`\`

  ---

  ## 5. Decision Tree

  Pick the duration token by answering these questions in order:

  1. **Is this a micro interaction?** (ripple spread, checkbox check mark, toggle thumb)
     → `DurationShort1` or `DurationShort2`

  2. **Is this a component state change?** (button press feedback, chip select, icon swap)
     → `DurationShort3` or `DurationShort4`

  3. **Is this a container change?** (card expand, FAB extend, menu open, tooltip appear)
     → `DurationMedium1` or `DurationMedium2`

  4. **Is this a screen-level element transition?** (dialog enter, bottom sheet, search bar expand)
     → `DurationMedium3` or `DurationMedium4`

  5. **Is this a shared element / hero transition?** (image expands from list to detail)
     → `DurationLong1` or `DurationLong2`

  6. **Is this a full-screen complex transition?** (entire screen morphs)
     → `DurationLong3`, `DurationLong4`, or `DurationExtraLong` range

  **Easing rule (always):**
  - Element entering screen → Decelerate easing
  - Element leaving screen → Accelerate easing
  - Element changing state (not entering/leaving) → Standard or Emphasized easing
  - Looping / repeating animation → `LinearEasing`

  ---

  ## 6. Review Flags

  Patterns to catch in code review. Cross-reference with `references/pr-review.md` Category 3.

  | Pattern Found in Code | Flag | Suggested Fix |
  |-----------------------|------|--------------|
  | `tween(50)` | Hardcoded duration | `MotionTokens.DurationShort1.toInt()` |
  | `tween(100)` | Hardcoded duration | `MotionTokens.DurationShort2.toInt()` |
  | `tween(150)` | Hardcoded duration | `MotionTokens.DurationShort3.toInt()` |
  | `tween(200)` | Hardcoded duration | `MotionTokens.DurationShort4.toInt()` |
  | `tween(250)` | Hardcoded duration | `MotionTokens.DurationMedium1.toInt()` |
  | `tween(300)` | Hardcoded duration | `MotionTokens.DurationMedium2.toInt()` |
  | `tween(350)` | Hardcoded duration | `MotionTokens.DurationMedium3.toInt()` |
  | `tween(400)` | Hardcoded duration | `MotionTokens.DurationMedium4.toInt()` |
  | Any other `tween(N)` with integer literal | Hardcoded duration | Pick nearest `MotionTokens.*` duration |
  | `FastOutSlowInEasing` | Pre-M3 easing constant | `EmphasizedDecelerateEasing` (if entering) or `EmphasizedEasing` |
  | `LinearOutSlowInEasing` | Pre-M3 easing constant | `EmphasizedDecelerateEasing` |
  | `FastOutLinearInEasing` | Pre-M3 easing constant | `EmphasizedAccelerateEasing` |
  | `animateColorAsState(target)` with no `animationSpec` | Missing spec | Add `tween(MotionTokens.DurationShort4.toInt(), easing = StandardEasing)` |
  | Same easing for both `enter` and `exit` in `AnimatedVisibility` | Incorrect easing pairing | Enter → Decelerate, exit → Accelerate |
  | Duration > 600ms on non-shared-element animation | Too slow | Reduce to `DurationLong1` or below |
  ```

  Note: Replace all `[sourced value]` and `[sourced x1, y1, x2, y2]` with actual values from Task 1 before writing the file.

- [ ] **Step 3: Verify file completeness**

  ```bash
  # Check all 7 sections exist
  grep -n "^## " jetpack-compose-expert-skill/references/material3-motion.md
  ```
  Expected output: 7 section headers (Why Use, Duration Tokens, Easing Tokens, Using Tokens, Decision Tree, Review Flags, and the CMP note at top).

  ```bash
  # Confirm no placeholder text remains
  grep -n "\[sourced" jetpack-compose-expert-skill/references/material3-motion.md
  ```
  Expected: no output. If any `[sourced ...]` remain, go back and fill them from Task 1 data.

- [ ] **Step 4: Commit**

  ```bash
  git add jetpack-compose-expert-skill/references/material3-motion.md
  git commit -m "feat: add material3-motion.md reference sourced from AOSP MotionTokens + EasingTokens"
  ```

---

## Task 3: Write `pr-review.md`

**Files:**
- Create: `jetpack-compose-expert-skill/references/pr-review.md`
- Read first: `jetpack-compose-expert-skill/references/modifiers.md` (for modifier ordering rules)
- Read first: `jetpack-compose-expert-skill/references/performance.md` (for recomposition checklist items)
- Read first: `jetpack-compose-expert-skill/references/multiplatform.md` (for CMP compatibility rules)

- [ ] **Step 1: Read modifier ordering rules**

  ```bash
  grep -n "order\|paint model\|background.*padding\|padding.*background\|clickable" \
    jetpack-compose-expert-skill/references/modifiers.md | head -40
  ```
  Note the exact ordering rules — these feed Category 1 of the checklist.

- [ ] **Step 2: Read recomposition instability patterns**

  ```bash
  grep -n "unstable\|@Stable\|@Immutable\|List<\|HashMap\|remember.*lambda" \
    jetpack-compose-expert-skill/references/performance.md | head -40
  ```
  Note patterns — these feed Category 2 of the checklist.

- [ ] **Step 3: Read CMP API availability rules**

  ```bash
  grep -n "commonMain\|android\.\|LocalContext\|Activity\|Context\|R\." \
    jetpack-compose-expert-skill/references/multiplatform.md | head -40
  ```
  Note CMP-incompatible patterns — these feed Category 4 of the checklist.

- [ ] **Step 4: Write the file**

  Create `jetpack-compose-expert-skill/references/pr-review.md`:

  ```markdown
  # PR Review Mode

  Activate when: input contains a GitHub PR URL (`github.com/.+/pull/\d+`) or explicit review
  phrases ("review this PR", "review this diff", "check this code", "what's wrong with this").

  Do NOT mix with code generation. When Review Mode activates, follow only this workflow.

  ---

  ## Review Workflow

  ### Step 1 — Fetch the diff

  \`\`\`bash
  gh pr diff <PR_URL>
  \`\`\`

  Store the output. Note all changed `.kt` files.

  ### Step 2 — Fetch full file contents

  For each changed `.kt` file, fetch the complete file — not just diff lines.

  \`\`\`bash
  # Get owner/repo and branch from PR
  gh pr view <PR_URL> --json headRefName,headRepository \
    --jq '{branch: .headRefName, repo: .headRepository.nameWithOwner}'

  # Fetch full file
  gh api "repos/{owner}/{repo}/contents/{path}?ref={branch}" \
    --jq '.content' | base64 -d
  \`\`\`

  **Why full files:** The diff shows what changed. The full file shows what the composable
  actually looks like — including whether a `modifier` param exists, and how modifier chains
  are structured across multiple lines. Single-line modifier patterns (e.g.,
  `Row(modifier = Modifier.fillMaxWidth().padding(16.dp)) {`) are invisible in a diff-only view
  if the line itself was not modified.

  ### Step 3 — Scan project settings

  Run in priority order. Stop when enough signal found. Always run step 3d regardless.

  **3a. Check for .editorconfig:**
  \`\`\`bash
  cat .editorconfig 2>/dev/null || echo "not found"
  \`\`\`
  Note: indent size, max line length, trailing commas for Kotlin sections.

  **3b. Check for ktlint config:**
  \`\`\`bash
  # ktlint config lives in .editorconfig under [*.kt] or as .ktlint
  grep -A 20 "\[\*\.kt\]" .editorconfig 2>/dev/null || cat .ktlint 2>/dev/null || echo "not found"
  \`\`\`

  **3c. Check for detekt:**
  \`\`\`bash
  find . -name "detekt.yml" -o -name "detekt-config.yml" 2>/dev/null | head -3
  \`\`\`
  If found, read it. Note any complexity, naming, or style rules.

  **3d. Infer codebase conventions (always run):**
  Sample 3–5 existing composable files NOT in the diff:
  \`\`\`bash
  find . -name "*.kt" -not -path "*/build/*" | xargs grep -l "@Composable" | \
    grep -v "Test" | head -5
  \`\`\`
  For each file, note:
  - Modifier chaining style: one per line vs inline
  - Param name used: `modifier` vs `Modifier` (both are valid; note which team uses)
  - Trailing lambda style on single-slot composables
  - Named param usage on single-arg calls

  Build a **project profile** from this scan. Use it to suppress false positives. A team
  that consistently writes inline modifiers should not be flagged for it.

  ### Step 4 — Run the Compose checklist

  Evaluate every changed composable against all 5 categories below. Use the **full file**
  from Step 2, not the diff from Step 1.

  ### Step 5 — Output the report

  Use the report format at the end of this document.

  ---

  ## Compose Review Checklist

  ### Category 1: Modifier Hygiene

  Scan the full file for each changed composable function.

  - [ ] Every `@Composable` function that renders UI has a `modifier: Modifier = Modifier` parameter.
        **Flag if missing** — UI composables must expose a modifier for caller control of layout.
        Exception: private composables used only internally with no layout impact.

  - [ ] The `modifier` parameter is passed to the root layout element (the outermost composable
        in the function body). It must not be ignored, applied to an inner element, or duplicated.

  - [ ] `modifier` is not applied more than once across sibling elements. Splitting a modifier
        between two children is always wrong — only one root element receives it.

  - [ ] Modifier ordering follows the paint model. Flag these reversals:
        - `background()` before `padding()` when the intent is padding-inside-background
          (correct: `padding().background()` = background wraps padded content;
           reversed: `background().padding()` = background does NOT include padding area)
        - `clickable()` or `pointerInput()` before `padding()` — shrinks the touch target
        - `size()` or `fillMaxWidth()` after `padding()` — size no longer includes padding

  - [ ] Single-line modifier check: read the full constructor line even when unchanged in the diff.
        `Row(modifier = Modifier.fillMaxWidth().padding(16.dp).background(Color.Red))` — verify ordering.

  - [ ] Modifier chain does not use both `Modifier.padding()` and `Modifier.offset()` for
        the same visual adjustment — they are not equivalent. `offset` does not affect layout;
        `padding` does.

  ### Category 2: Recomposition

  - [ ] Composable parameters do not include unstable types without stability annotations:
        - Plain `List<T>` → use `@Immutable` data class wrapper or `ImmutableList<T>` from kotlinx-collections-immutable
        - `HashMap`, `MutableMap`, any mutable collection → not stable, must be annotated
        - Non-`data` classes without `@Stable` → compiler cannot infer stability

  - [ ] Lambdas passed as parameters are not created inline at the call site without `remember {}`.
        \`\`\`kotlin
        // BAD — new lambda instance every recomposition
        MyComposable(onClick = { doSomething() })

        // OK — stable reference
        val onClick = remember { { doSomething() } }
        MyComposable(onClick = onClick)
        // OR use a stable ViewModel function reference
        \`\`\`

  - [ ] `derivedStateOf {}` is used where a value is computed from one or more state reads.
        Flag: `val isValid = username.isNotEmpty() && password.length > 8` inside a composable body
        without `remember { derivedStateOf { ... } }`.

  - [ ] `remember {}` keys are correct:
        - `remember(Unit)` or `remember {}` with no keys but referencing an input variable = stale value bug
        - `remember(key)` where `key` never changes = effectively `remember {}` — flag if surprising

  ### Category 3: M3 Motion

  Cross-reference with `references/material3-motion.md` for token values and easing names.

  - [ ] No integer literal durations in `tween()`. Flag any `tween(N)` where N is a plain number.
        Suggest nearest `MotionTokens.*` token from the duration table in `material3-motion.md`.

  - [ ] No pre-M3 easing constants:
        - `FastOutSlowInEasing` → `EmphasizedDecelerateEasing` (entering) or `EmphasizedEasing`
        - `LinearOutSlowInEasing` → `EmphasizedDecelerateEasing`
        - `FastOutLinearInEasing` → `EmphasizedAccelerateEasing`

  - [ ] `animateColorAsState(targetValue = ...)` without `animationSpec` — flag, must specify spec.
        Suggest: `tween(durationMillis = MotionTokens.DurationShort4.toInt(), easing = StandardEasing)`

  - [ ] `AnimatedVisibility` enter and exit using the same easing curve — flag. Enter must use
        Decelerate easing; exit must use Accelerate easing. They should always be asymmetric.

  - [ ] Duration > 600ms on a non-shared-element animation — flag as too slow for the interaction type.

  ### Category 4: CMP Compatibility

  Apply only to files whose path contains `commonMain` or has no platform-specific suffix.

  - [ ] No `android.*` imports (e.g., `android.content.Context`, `android.util.Log`)
  - [ ] No `androidx.*` imports that are Android-only. Check `references/multiplatform.md`
        API availability matrix for what is and is not available in `commonMain`.
  - [ ] No `LocalContext.current` usage — not available in CMP `commonMain`
  - [ ] No `Activity`, `Context`, or `Application` references
  - [ ] Resources use `Res.drawable.*`, `Res.string.*` — not `R.drawable.*`, `R.string.*`

  ### Category 5: Lists & Keys

  - [ ] Every `items(collection)` call in `LazyColumn`, `LazyRow`, `LazyVerticalGrid`,
        or `LazyHorizontalGrid` has a `key = { item -> item.id }` parameter.
        Missing keys cause incorrect animations and item reuse bugs.

  - [ ] `contentType = { item -> item::class }` is present when a lazy list renders more than
        one type of item. Without it, Compose cannot reuse composition nodes efficiently.

  - [ ] No `LazyColumn` directly inside another `LazyColumn` without a fixed height constraint
        on the inner one. Unbounded nested lazy lists crash at runtime.

  - [ ] `TvLazyRow`, `TvLazyColumn`, `TvLazyVerticalGrid`, `TvLazyHorizontalGrid` from
        `tv-foundation` — flag as deprecated. Replace with standard Foundation equivalents
        (`LazyRow`, `LazyColumn`, etc.). See `references/tv-compose.md` migration table.

  ---

  ## Output Report Format

  \`\`\`
  ## PR Review: <PR title> (#NNN)
  Branch: <head-branch> → <base-branch>

  ### Project Profile
  - Code style: <inferred — e.g., "modifiers chained one per line", "trailing lambdas preferred">
  - Lint config: <ktlint found / detekt found / neither found>
  - Conventions inferred from: <list of files sampled>

  ---

  ### Issues

  #### Critical
  Issues that will cause bugs, crashes, or correctness problems.

  - `path/to/File.kt:42` — Missing `modifier: Modifier = Modifier` on public composable `MyCard`.
    All UI composables must expose a modifier parameter for caller control of layout.
    Fix: Add `modifier: Modifier = Modifier` to function signature; pass it to the root element.

  #### Suggestions
  Style, M3 alignment, and performance improvements.

  - `path/to/File.kt:87` — `tween(300)` → use `MotionTokens.DurationMedium2.toInt()` (300ms = Medium2 in M3 scale)
  - `path/to/File.kt:103` — `FastOutSlowInEasing` → use `EmphasizedDecelerateEasing` (M3 equivalent for entering elements)

  #### Positive Patterns
  Good Compose usage worth noting — always include at least one.

  - `path/to/File.kt:55` — Correct use of `derivedStateOf {}` to avoid redundant recompositions
  - `path/to/File.kt:71` — Shared element transition correctly uses `sharedBounds()` for container-to-page expansion

  ---

  ### Summary
  <N> critical, <M> suggestions across <K> files reviewed.
  \`\`\`

  Critical and Suggestions are always included (may be empty with "None found").
  Positive Patterns is always included — never omit it.
  ```

- [ ] **Step 5: Verify file completeness**

  ```bash
  grep -n "^## \|^### " jetpack-compose-expert-skill/references/pr-review.md
  ```
  Expected sections: Review Workflow, Step 1–5, Compose Review Checklist, all 5 Category headers, Output Report Format.

  ```bash
  # Confirm all 5 categories are present
  grep -c "### Category" jetpack-compose-expert-skill/references/pr-review.md
  ```
  Expected: `5`

- [ ] **Step 6: Commit**

  ```bash
  git add jetpack-compose-expert-skill/references/pr-review.md
  git commit -m "feat: add pr-review.md — PR review workflow and Compose checklist"
  ```

---

## Task 4: Update `SKILL.md`

**Files:**
- Modify: `jetpack-compose-expert-skill/SKILL.md`

Three additions: Review Mode trigger block, two new routing table rows, two cross-reference notes on existing rows.

- [ ] **Step 1: Add Review Mode trigger before the workflow**

  In `SKILL.md`, insert the following block **before** `## Workflow` (after the frontmatter description ends and before the first `##` heading):

  ```markdown
  ## Review Mode

  **Activate when** the input contains a GitHub PR URL (`github.com/.+/pull/\d+`) or
  explicit review phrases: "review this PR", "review this diff", "check this code",
  "what's wrong with this".

  When Review Mode activates:
  1. Do NOT follow the generation workflow below
  2. Read `references/pr-review.md` and follow its workflow exclusively
  3. Output a structured local review report (do not post to GitHub)

  ```

- [ ] **Step 2: Add two new rows to the routing table**

  In the routing table under `### 3. Consult the right reference`, add:

  ```markdown
  | M3 motion tokens, `MotionTokens`, `EasingTokens`, animation duration, easing curves | `references/material3-motion.md` |
  | PR URL, code review, "review this PR", "what's wrong with this" | `references/pr-review.md` |
  ```

  Add these two rows at the end of the existing table (before the closing blank line).

- [ ] **Step 3: Add cross-reference notes to two existing rows**

  Find the animation row:
  ```
  | `animate*AsState`, `AnimatedVisibility`, `Crossfade`, transitions | `references/animation.md` |
  ```
  Change to:
  ```
  | `animate*AsState`, `AnimatedVisibility`, `Crossfade`, transitions | `references/animation.md` — for M3 token selection, also see `references/material3-motion.md` |
  ```

  Find the theming row:
  ```
  | `MaterialTheme`, `ColorScheme`, dynamic color, `Typography`, shapes | `references/theming-material3.md` |
  ```
  Change to:
  ```
  | `MaterialTheme`, `ColorScheme`, dynamic color, `Typography`, shapes | `references/theming-material3.md` — for motion in M3 components, see `references/material3-motion.md` |
  ```

- [ ] **Step 4: Add Review Mode triggers to frontmatter description**

  In the frontmatter `description:` block, append to the list of trigger phrases:
  ```
  "review this PR", "review this code", "check this diff", or any GitHub PR URL (github.com/.*/pull/).
  ```

- [ ] **Step 5: Verify changes**

  ```bash
  grep -n "Review Mode\|pr-review\|material3-motion" jetpack-compose-expert-skill/SKILL.md
  ```
  Expected: at least 6 matches — the Review Mode block header, 2 routing rows, 2 cross-reference notes, and the frontmatter trigger addition.

- [ ] **Step 6: Commit**

  ```bash
  git add jetpack-compose-expert-skill/SKILL.md
  git commit -m "feat: add Review Mode trigger and M3 motion routing to SKILL.md"
  ```

---

## Task 5: Update `README.md`

**Files:**
- Modify: `README.md`

Three changes: reference count 18→19, new row in coverage table, update inline count string.

- [ ] **Step 1: Bump reference count in intro paragraph**

  Find:
  ```
  1. **18 reference guides** covering every major Compose topic
  ```
  Replace with:
  ```
  1. **19 reference guides** covering every major Compose topic
  ```

- [ ] **Step 2: Add M3 Motion row to coverage table**

  Find the TV Compose row (last content row before "Source code"):
  ```
  | **TV Compose** | TV Material3 (Surface, Cards, Carousel, NavigationDrawer, TabRow), focus system, D-pad navigation, theming, immersive list, TVProvider |
  ```
  Add after it:
  ```
  | **M3 Motion** | All Material 3 duration tokens (`DurationShort1–4`, `DurationMedium1–4`, `DurationLong1–4`, `DurationExtraLong1–4`), easing tokens (`EmphasizedEasing`, `StandardEasing`, etc.), mapping to Compose animation APIs, decision tree, PR review flags |
  ```

- [ ] **Step 3: Update inline count in diagram section**

  Find:
  ```
  +-- ... (18 guides total)
  ```
  Replace with:
  ```
  +-- ... (19 guides total)
  ```

- [ ] **Step 4: Verify**

  ```bash
  grep -n "19\|M3 Motion\|material3-motion" README.md
  ```
  Expected: at least 3 matches — the intro count, the coverage table row, and the diagram count.

- [ ] **Step 5: Commit**

  ```bash
  git add README.md
  git commit -m "docs: bump reference count to 19, add M3 Motion to coverage table"
  ```

---

## Task 6: Push and Open PR

- [ ] **Step 1: Push branch**

  ```bash
  git push origin fix/tv-compose-review-issues
  ```
  (This branch already exists from the TV fix work — these commits land on the same branch.)

  If you want a clean PR just for this work:
  ```bash
  git checkout -b feat/pr-review-and-m3-motion
  # cherry-pick the 4 commits from Tasks 2–5
  git push -u origin feat/pr-review-and-m3-motion
  ```

- [ ] **Step 2: Open PR**

  ```bash
  gh pr create \
    --title "feat: add PR review mode and Material 3 motion token reference" \
    --body "Adds two new capabilities to the compose-expert skill:

  **PR Review Mode** (\`references/pr-review.md\`)
  - Activates on PR URL or review intent phrases
  - Fetches full files (not just diff) to catch single-line modifier patterns and missing modifier params
  - Scans project settings (.editorconfig, ktlint, detekt + codebase conventions)
  - 5-category Compose checklist: modifier hygiene, recomposition, M3 motion, CMP compatibility, lists & keys
  - Outputs structured local report (Critical / Suggestions / Positive Patterns)

  **M3 Motion Token Reference** (\`references/material3-motion.md\`)
  - All duration and easing tokens sourced from AOSP \`MotionTokens.kt\` + \`EasingTokens.kt\`
  - Mapping to Compose animation APIs (animate*AsState, AnimatedVisibility, updateTransition, shared elements)
  - Decision tree for picking the right token
  - Review flags table for catching hardcoded durations in PRs

  **SKILL.md** updated with Review Mode trigger block, 2 new routing entries, cross-references.
  **README.md** bumped to 19 reference guides."
  ```

---

## Self-Review

### Spec Coverage Check

| Spec Requirement | Task |
|-----------------|------|
| SKILL.md Review Mode trigger (PR URL + phrases) | Task 4 Step 1 |
| SKILL.md routing entries for pr-review + material3-motion | Task 4 Step 2 |
| SKILL.md cross-references on animation + theming rows | Task 4 Step 3 |
| Project settings scan (editorconfig + ktlint + detekt + codebase inference) | Task 3 Step 4 |
| Full file fetch (not just diff) | Task 3 Step 4 (Step 2 of workflow) |
| Category 1: Modifier hygiene (5 checks) | Task 3 Step 4 |
| Category 2: Recomposition (4 checks) | Task 3 Step 4 |
| Category 3: M3 Motion (5 checks) | Task 3 Step 4 |
| Category 4: CMP compatibility (5 checks) | Task 3 Step 4 |
| Category 5: Lists & keys (4 checks) | Task 3 Step 4 |
| Report format (Critical / Suggestions / Positive Patterns) | Task 3 Step 4 |
| M3 duration tokens sourced from AOSP | Task 1 + Task 2 |
| M3 easing tokens sourced from AOSP | Task 1 + Task 2 |
| Compose API mapping (animate*AsState, AnimatedVisibility, updateTransition, shared elements) | Task 2 |
| Decision tree for token selection | Task 2 |
| Review flags table | Task 2 |
| CMP compatibility note for MotionTokens | Task 2 |
| README count 18→19 | Task 5 |
| README coverage table row | Task 5 |

All spec requirements covered. No gaps.
