# Performance Optimization Reference

## Three Phases: Composition, Layout, Drawing

Every frame consists of three phases. Understanding state reads in each phase prevents unnecessary recompositions.

### Composition Phase
- Executes composable functions, evaluates state reads
- Generates lambda and instance allocations
- **State reads here trigger recomposition** of the entire scope

### Layout Phase
- Calculates size and position, runs `measure` and `layout` blocks
- Can read state without triggering composition recomposition
- Mutable state reads OK; prefer `Modifier.offset { }` over `Modifier.offset()`

### Drawing Phase
- Emits draw operations, runs `Canvas` and custom `DrawScope`
- A state read here invalidates only the draw phase (no recomposition or relayout), so read frequently changing state inside draw lambdas

**Source**: `androidx/compose/runtime/Composer.kt`

---

## Recomposition Skipping with Compiler Reports

The Compose compiler generates `$changed` bitmasks to detect state changes. Enable compiler reports to inspect stability and skippability:

```kotlin
// build.gradle.kts
composeCompiler {
    reportsDestination = layout.buildDirectory.dir("compose_reports")
    metricsDestination = layout.buildDirectory.dir("compose_metrics")
}
```

After building (`./gradlew assembleRelease`), check the generated files in `build/compose_reports/`:

- **`*_composables.txt`** — shows each composable's restartability and skippability:
  ```
  restartable skippable fun MyComponent(name: String, onClick: Function0<Unit>)
  restartable fun UnstableComponent(items: List<Item>)  // NOT skippable — unstable param
  ```

- **`*_classes.txt`** — shows stability inference for each class:
  ```
  stable class User { stable val name: String }
  unstable class ScreenState { unstable val items: List<Item> }
  ```

A composable missing `skippable` means the compiler cannot skip it during recomposition, even when inputs haven't changed. Fix by stabilizing its parameters (see Stability section below).

### Stability — @Stable and @Immutable

A type is **stable** if:
- Its public properties are stable
- Overrides to `equals()` and `hashCode()` are based on stable properties
- Recomposition is skipped when the same instance is passed

Executable check for a stable model rendered through a composable:

```kotlin verify
// name: stable-model-renders-text
// repeat: 3
// assert: text = "Ada"
// assert-not: text = "Bob"
@Immutable
data class Person(val name: String, val age: Int)

@Composable
fun Subject() {
    val person = Person("Ada", 42)
    Text(person.name)
}
```

Mark stable types explicitly:

```kotlin
@Immutable
data class Person(val name: String, val age: Int)

@Stable
class Counter {
    var count by mutableIntStateOf(0)
        private set
    fun increment() { count++ }
}

// Composable receiving stable types can skip recomposition
@Composable
fun PersonCard(person: Person) {
    Text(person.name)  // Skips if person unchanged
}
```

**Avoid**: `@Stable` on data classes with mutable fields or non-final properties.

---

## Strong Skipping Mode (Default)

Strong skipping is enabled by default with Kotlin 2.0.20 and newer. Restartable
composables with unstable parameters can be skipped using instance equality,
and lambdas inside composition are remembered automatically.

```kotlin
// The lambda is remembered automatically under strong skipping.
@Composable
fun Counter(count: Int) {
    Button(onClick = { println(count) }) {
        Text("Count: $count")
    }
}
```

Do not add obsolete `kotlinCompilerExtensionVersion` configuration to modern
Kotlin projects. Use the Kotlin Compose compiler Gradle plugin matching the
Kotlin version. Skipping still has parameter-comparison and bookkeeping cost;
avoiding unnecessary invalidations is often better than forcing stability.

---

## Defer State Reads to Layout/Draw Phase

Reading state in composition triggers recomposition. Push reads to later phases:

### Bad: Recomposition on Every Offset Change
```kotlin
@Composable
fun Box(offsetX: State<Float>) {
    val x = offsetX.value  // Reads in composition, triggers recomposition
    Box(modifier = Modifier.offset(x.dp, 0.dp))
}
```

### Good: Deferred Read in Layout Phase
```kotlin
@Composable
fun Box(offsetX: State<Float>) {
    Box(
        modifier = Modifier.offset {
            IntOffset(offsetX.value.toInt(), 0)  // Read in layout phase
        }
    )
}
```

Use `Modifier.offset { }` (lambda) instead of `Modifier.offset()` (parameter) for state-dependent positioning.

---

## derivedStateOf — Reducing Recomposition Frequency

Cache expensive calculations with `remember(keys)`; use `derivedStateOf` only to derive a value from fast-changing State:

```kotlin
// Bad: re-filters on every recomposition
@Composable
fun SearchResults(items: List<Item>, query: String) {
    val filtered = items.filter { query in it.title }  // Composition phase
    LazyColumn {
        items(filtered) { /* ... */ }
    }
}

// Good: recompute only when inputs change (plain remember; no State inputs to derive from)
@Composable
fun SearchResults(items: List<Item>, query: String) {
    val filtered = remember(items, query) { items.filter { query in it.title } }
    LazyColumn {
        items(filtered) { /* ... */ }
    }
}
```

`remember(keys)` caches a calculation. `derivedStateOf` is for a value computed from
**State objects that change more often than the result**: readers recompose only when
the derived value changes.

```kotlin
val showScrollToTop by remember { derivedStateOf { listState.firstVisibleItemIndex > 0 } }
```

### computedStateOf (Compose Runtime 1.13+)

`computedStateOf` also invalidates observers only when its result changes, but it
recalculates on every read instead of maintaining a cached derived value. It can
be cheaper for small predicates that are read once after frequent writes.

```kotlin
val showScrollToTop by remember {
    computedStateOf { scrollState.value > 0 }
}
```

Use `derivedStateOf` when repeated reads benefit from caching or the calculation
allocates/is expensive. Use `computedStateOf` for cheap calculations dominated
by read-after-write invalidation cost. Runtime 1.13 is prerelease as of this
reference update, so gate the API on the project's dependency channel.

---

## remember with Keys

Avoid unnecessary recalculation:

```kotlin
// Recalculates on every recomposition
@Composable
fun ExpensiveItem(id: Int) {
    val metadata = computeMetadata(id)  // Called every time
    Text(metadata)
}

// Recalculates only when id changes
@Composable
fun ExpensiveItem(id: Int) {
    val metadata = remember(id) { computeMetadata(id) }
    Text(metadata)
}

// Multiple keys
@Composable
fun Item(id: Int, userId: Int) {
    val data = remember(id, userId) { fetchData(id, userId) }
    Text(data.toString())
}
```

Omit `remember` if computation is cheap (string formatting, simple objects). Over-wrapping causes memory leaks.

---

## LazyList Performance — Keys and ContentType

### Always Provide Keys

Keys enable item reuse and animations:

```kotlin
// Bad: no keys, items recreated on every list change
LazyColumn {
    items(users) { user ->
        UserRow(user)
    }
}

// Good: keys enable reuse
LazyColumn {
    items(users, key = { it.id }) { user ->
        UserRow(user)
    }
}
```

### ContentType for Efficient Reuse

```kotlin
sealed class ListItem {
    data class Header(val title: String) : ListItem()
    data class User(val user: User) : ListItem()
}

LazyColumn {
    items(
        items = items,
        key = { it.hashCode() },
        contentType = { item ->
            when (item) {
                is ListItem.Header -> "header"
                is ListItem.User -> "user"
            }
        }
    ) { item ->
        when (item) {
            is ListItem.Header -> HeaderRow(item.title)
            is ListItem.User -> UserRow(item.user)
        }
    }
}
```

Without `contentType`, all items compete for one ViewHolder pool. With it, items reuse efficiently.

### Avoid Allocations in Item Scope

```kotlin
// Bad: allocates on every recomposition
LazyColumn {
    items(users) { user ->
        val userState = remember { mutableStateOf(user) }
        UserRow(userState.value)
    }
}

// Good: allocates once
LazyColumn {
    items(
        items = users,
        key = { it.id }
    ) { user ->
        UserRow(user)
    }
}
```

---

## Baseline Profiles

Baseline profiles instruct R8 to pre-compile hot code paths, reducing startup time and jank.

### Generating Profiles

Use Jetpack Macrobenchmark to record profiles:

```kotlin
@RunWith(AndroidBenchmarkRunner::class)
class StartupBenchmark {
    @get:Rule
    val benchmarkRule = MacrobenchmarkRule()

    @Test
    fun startupCompilation() = benchmarkRule.measureRepeated(
        packageName = "com.example.app",
        metrics = listOf(StartupTimings.FIRST_FRAME),
        iterations = 10,
        setupBlock = {
            pressHome()
            startActivityAndWait()
        }
    ) {
        // Interact with app
    }
}
```

Profiles are generated in `baseline-prof.txt`:
```
androidx/compose/runtime/Recomposer;startRecomposition()V
com/example/MyScreen;ComposableFunctionName(ILandroidx/compose/runtime/Composer;I)V
```

---

## R8/ProGuard Compose Rules

Compose includes default ProGuard rules. Ensure `shrinkResources true` and `minifyEnabled true`:

```gradle
android {
    buildTypes {
        release {
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}
```

Do not add keep rules for `@Stable`/`@Immutable`: stability is resolved by the Compose compiler at
build time, not at runtime, so R8 rules do not affect it. For multi-module stability, use a
`stability_config.txt`.

---

## Measuring Performance

### Layout Inspector — Recomposition Counts

In Android Studio:
1. Run app on device
2. Open **Layout Inspector** (Tools > Layout Inspector)
3. Select target process
4. Check **Show Composition Counts** (toggle in inspector)

Recomposition counts display how many times each composable was recomposed since inspection started.

### Macrobenchmark — Frame Timing

```kotlin
benchmarkRule.measureRepeated(
    packageName = "com.example.app",
    metrics = listOf(FrameTimingMetric()),
    iterations = 10
) {
    // Interact: scroll, click, etc.
}
```

Reports frame times (ms), jank, jitter. Target <16.67ms for 60 fps.

---

## Common Hot Paths

### String Formatting in Composition
String templates (`"Count: $count"`) compile to `StringBuilder` calls; the allocation is small and
`buildString` is no faster. The real cost is recomposing the scope that builds the string every
frame: defer the read (lambda/`graphicsLayer`/draw phase) or hoist the changing value, and use
`stringResource(R.string.count, count)` for localized text.

### List Filtering Without derivedStateOf
```kotlin
// Bad: filters every recomposition
@Composable
fun FilteredList(items: List<Item>, predicate: (Item) -> Boolean) {
    LazyColumn {
        items(items.filter(predicate)) { /* ... */ }
    }
}

// Good
@Composable
fun FilteredList(items: List<Item>, predicate: (Item) -> Boolean) {
    val filtered = remember(items, predicate) { items.filter(predicate) }
    LazyColumn {
        items(filtered) { /* ... */ }
    }
}
```

### Creating Objects in Lambdas
```kotlin
// Bad
Button(
    colors = ButtonDefaults.buttonColors(
        containerColor = if (isPressed) Color.Red else Color.Blue
    )
) { }

// Good: compute once
val buttonColors = remember(isPressed) {
    ButtonDefaults.buttonColors(
        containerColor = if (isPressed) Color.Red else Color.Blue
    )
}
Button(colors = buttonColors) { }
```

---

## Anti-Patterns

### Wrapping Everything in remember
```kotlin
// Unnecessary
val text = remember { "Hello" }
val size = remember { 12.sp }
val color = remember { Color.Black }
```

`remember` only for mutable state or expensive calculations.

### Premature Optimization
Profile first. Don't add `derivedStateOf` or `remember` without Layout Inspector data.

### @Stable on Mutable Data Classes
```kotlin
// DON'T
@Stable
data class MutableUser(val name: String, val age: MutableState<Int>)

// DO
@Immutable
data class User(val name: String, val age: Int)
```

---

## Resources

- **Compose Compiler Reports**: https://developer.android.com/develop/ui/compose/performance/stability-report
- **Macrobenchmark**: https://developer.android.com/develop/ui/compose/performance/measurement
- **Baseline Profiles**: https://developer.android.com/develop/ui/compose/performance/baseline-profiles
- **In-process tracing (`androidx.tracing` 2.0)**: https://developer.android.com/topic/performance/tracing/in-process-tracing
- **Tracing release notes**: https://developer.android.com/jetpack/androidx/releases/tracing
- **Jetpack Keep**: https://developer.android.com/topic/performance/app-optimization/jetpack-keep-annotations

---

## Zero-Size DrawScope Guard

During initial composition, a composable's size can be zero. This causes crashes in calculations like `size.minDimension / 2`.

```kotlin
// BAD: crashes when size is zero
Canvas(modifier = Modifier.fillMaxSize()) {
    val radius = size.minDimension / 2  // NaN or divide-by-zero
    drawCircle(color = Color.Blue, radius = radius)
}

// GOOD: always guard
Canvas(modifier = Modifier.fillMaxSize()) {
    if (size.minDimension <= 0f) return@Canvas
    val radius = size.minDimension / 2
    drawCircle(color = Color.Blue, radius = radius)
}
```

Rule: always guard DrawScope math against zero size. `fillMaxSize()` on a Canvas is fine when the parent bounds the height; in unbounded-height parents (`verticalScroll`, lazy items) give it an explicit height.

---

## Composition Tracing

Use `trace()` for Perfetto/systrace integration:

```kotlin
@Composable
fun ExpensiveScreen() {
    trace("ExpensiveScreen") {
        // composable body — visible in system traces
    }
}
```

Composition tracing identifies how long composables take. Compose Runtime 1.13
adds recomposition tracing, which records state reads/writes and call stacks that
caused recomposition in Perfetto. Use it to find the invalidation source before
adding `remember`, annotations, or derived state.

### App-level tracing with `androidx.tracing` 2.0

Composition and recomposition tracing show Compose internals. For your own
code — repositories, use cases, image decoding, coroutine pipelines — add
sections with `androidx.tracing` 2.0, a Kotlin API that writes Perfetto-format
events from inside the process.

```kotlin
dependencies {
    // Libraries that only emit events: depend on the lightweight API.
    implementation("androidx.tracing:tracing:<version>")
    // App module only: Android/JVM implementation and Perfetto sink.
    implementation("androidx.tracing:tracing-wire:<version>")
}
```

Check the release page for the current version before pinning (2.0.5 was the
latest stable on 2026-10-21). On Android, `tracing-wire` initializes itself
through AndroidX Startup and writes Perfetto files to the app's no-backup files
directory; on the JVM you create a `TraceSink` and `TraceDriver` yourself.

```kotlin
suspend fun loadFeed(): Feed =
    Tracer.global.traceCoroutine(category = "feed", name = "loadFeed") {
        repository.refresh()
    }
```

Rules:

- Use `Tracer.global` at the call site; do not cache the reference — the global
  tracer can be replaced after app initialization. Never call `setGlobalTracer`
  from a library.
- Use `trace(...)` for blocking code and `traceCoroutine(...)` for suspending
  code. `traceCoroutine` propagates context across suspension points and thread
  switches, so related work appears as connected flows in Perfetto.
- Both accept a `category`, `name`, optional propagation token, `isRoot`, and a
  `metadataBlock` for annotations (arguments, source file/line, call stack
  entries). Keep metadata small; do not record user identifiers, tokens, or
  message content.
- Do not catch `CancellationException` inside a traced block to "close" the
  section — the section ends when the block exits, including by cancellation.
- Reusable libraries depend on `tracing` only; the app chooses the backend with
  `tracing-wire`.
- The library does not capture CPU scheduling or memory itself. Open the
  generated file in Perfetto and merge it with a system trace.

---

## Custom Draw Cost

When many items animate or drag at once and recomposition is already deferred, jank usually
comes from the draw phase: cost = passes per item x items x layer size.

- **Count passes.** Looping `drawContent()` N times (for example a multi-step blur-shadow loop plus an outline loop) re-executes the whole content N times per item per frame. Prefer a few passes, a
  platform shadow API, or caching the result.
- **`saveLayer`/offscreen layers allocate buffers.** Under `CompositingStrategy.Auto`, a layer
  goes offscreen when alpha < 1 or a `RenderEffect` is set; `CompositingStrategy.Offscreen`
  forces it. Use offscreen only when needed (for example `BlendMode.Clear` masking).
  Do not nest `saveLayer` inside a per-pass loop.
- **Cache static output.** If the cutout/shadow does not change per frame, record it once into
  a `GraphicsLayer` (`rememberGraphicsLayer()` + `record {}` + `drawLayer()`, Compose 1.7+) or
  render it to an `ImageBitmap`, then draw the cached layer while the item moves.
- **Allocate in `drawWithCache`, not in the draw lambda.** `Paint`, `Brush`, `Shader`, `Path`
  created per draw are garbage every frame; `drawWithCache` keeps them until the size or a read
  state changes.
- **Reads belong in the draw lambda.** Animated alpha, offset, and progress read inside
  `graphicsLayer {}`/`drawBehind {}` invalidate draw only. Passing the animated `Float` as a
  composable parameter recomposes the child every frame.
- **Measure.** Compare frame time with the effect on and off using Macrobenchmark
  `FrameTimingMetric` and a Perfetto trace; scale the item count, because cost multiplies.

---

## movableContentOf

Avoid recomposition when moving content between layout positions:

```kotlin
val movableContent = remember {
    movableContentOf {
        ExpensiveChild() // Only composed once, moved without recomposition
    }
}

if (isExpanded) {
    ExpandedLayout { movableContent() }
} else {
    CollapsedLayout { movableContent() }
}
```

Without `movableContentOf`, switching between layouts would dispose and recompose `ExpensiveChild`. With it, the content is moved, preserving state and avoiding recomposition.

---

## Compiler Reports (Expanded)

Enable compiler reports to see which composables are skippable and which types are stable:

```kotlin
// build.gradle.kts
composeCompiler {
    reportsDestination = layout.buildDirectory.dir("compose_reports")
    metricsDestination = layout.buildDirectory.dir("compose_metrics")
}
```

After building, check the output files:

- `*_composables.txt` — shows each composable's status:
  ```
  restartable skippable fun MyComponent(name: String, onClick: Function0<Unit>)
  restartable fun UnstableComponent(items: List<Item>)  // NOT skippable!
  ```

- `*_classes.txt` — shows type stability:
  ```
  stable class User { stable val name: String }
  unstable class ScreenState { unstable val items: List<Item> }
  ```

Fix unstable types by:
1. Using `@Stable` annotation on the class
2. Using `kotlinx.collections.immutable.ImmutableList` instead of `List`
3. Adding the class to `compose-stability-config.txt` for multi-module projects

---

## Jetpack Keep (alpha) — keep rules next to reflection

Compose itself needs no hand-written keep rules, but release builds that use
reflection or JNI do. Jetpack Keep (`androidx.annotation.keep`, `1.0.0-alpha01`,
requires AGP 8.7+) replaces broad `-keep` rules with annotations on the code that
performs the reflection; its Gradle plugin generates **conditional** rules, so
R8 keeps the target only if it keeps the annotated caller.

- Add both the library (`androidx.annotation.keep:keep`) and the Gradle plugin
  (`androidx.annotation.keep`) to every module that uses it; they share one
  version. The plugin reads only that module's own code.
- Annotate the reflecting function: `@UsesReflectionToConstruct`,
  `@UsesReflectionToAccessMethod`, `@UsesReflectionToAccessField`. Prefer
  `classConstant` over `className` and the most specific class; omit
  `parameterTypes` to keep every overload, pass an empty array for the
  no-argument form.
- `@UnconditionallyKeep` is for code called from outside Kotlin/Java (for example
  JNI). It limits optimization, so use it only when the `@UsesReflection*` forms
  do not apply.
- Run `./gradlew :app:lint` (`ReflectionWithoutKeepAnnotations`,
  `MissingKeepAnnotationPlugin`) then `lintFix`; inspect the output of
  `./gradlew :app:releaseExtractKeepRules` before deleting any old rule.
- It is alpha: a new version can generate rules that keep less, causing
  `ClassNotFoundException` only in release builds. Diff generated rules on every
  upgrade and test a release build. Reflection discovered by annotation is not
  covered yet; keep a manual rule for it.

---

## Production Performance Rules

1. **R8: strip previews + semantics in release** — add to `proguard-rules.pro`:
```
-assumenosideeffects class androidx.compose.ui.tooling.preview.** { *; }
```

2. **`@Suppress("ComposeUnstableCollections")`** — pragmatic skipping when stability isn't worth the complexity:
```kotlin
@Suppress("ComposeUnstableCollections")
@Composable
fun ItemList(items: List<Item>) { // List is unstable but acceptable here
    // ...
}
```

3. **ImmutableList for stability** — Guava `ImmutableList` or `kotlinx.collections.immutable`:
```kotlin
// Makes the parameter stable, enabling recomposition skipping
@Composable
fun StableList(items: ImmutableList<Item>) { ... }
```

4. **ReportDrawnWhen** for startup performance:
```kotlin
ReportDrawnWhen { items.isNotEmpty() }
```

5. **Canvas sized deliberately** — in unbounded-height parents use an explicit height instead of `fillMaxSize()`:
```kotlin
// BAD
Canvas(Modifier.fillMaxSize()) { ... }

// GOOD
Canvas(Modifier.fillMaxWidth().height(200.dp)) { ... }
```

---

## Compose Multiplatform Performance

Performance tooling differs across platforms:

| Tool | Android | Desktop | iOS | Web |
|------|---------|---------|-----|-----|
| Baseline Profiles | Yes | No | No | No |
| Macrobenchmark | Yes | No | No | No |
| Layout Inspector | Yes (AS) | No | No | No |
| Profiling | Android Studio | JMH | Instruments | Browser DevTools |
| R8/ProGuard | Yes | ProGuard separately | N/A (Kotlin/Native) | N/A |

iOS-specific:
- Kotlin/Native has different GC behavior than Android ART
- Enable ProMotion with `CADisableMinimumFrameDurationOnPhone = true` in Info.plist
- Use configurable frame rate API: increase for animations, decrease for static content

Desktop JVM:
- Different GC characteristics (G1GC vs ART)
- JIT compilation warms up differently

Web/WASM:
- Renders entire canvas per frame (unlike DOM partial repaints)
- WASM GC behavior differs from JVM
- Bundle size impacts initial load time
