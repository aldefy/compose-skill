# Jetpack Compose State Management Reference

## State Fundamentals

State in Compose is observable data that triggers recomposition when changed.

### Creating State

Use type-specific state holders for efficiency:

```kotlin
// General-purpose state (Any type)
val name = mutableStateOf("Alice")

// Primitive specializations (avoid boxing)
val count = mutableIntStateOf(0)
val progress = mutableFloatStateOf(0.5f)
val enabled = mutableStateOf(true)  // Boolean has no specialization
```

**Pitfall:** Using `mutableStateOf<Int>()` instead of `mutableIntStateOf()` causes unnecessary boxing on every read/write. Primitive specializations are located in `androidx.compose.runtime` (source: `State.kt`).

## remember vs rememberSaveable

Both associate state with a composition key, but differ in persistence scope.

### remember
- Lives for the composition's lifetime
- Lost on process death, configuration changes, back navigation
- Best for UI state: selection, expanded/collapsed, scroll position

```kotlin verify
// name: remember-counter-renders-clickable-state
// repeat: 3
// assert: text = "Count: 0"
// assert: has-click-action = "Count: 0"
// assert-not: text = "Count: 1"
@Composable
fun Subject() {
    var count by remember { mutableIntStateOf(0) }
    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}
```

### rememberSaveable
- Survives process death and configuration changes
- Uses `Bundle`-compatible types by default (String, Int, Boolean, etc.)
- For custom types, provide a `Saver` or use `@Parcelize`
- Best for data that represents user input or navigation state

```kotlin
@Composable
fun SearchScreen() {
    var query by rememberSaveable { mutableStateOf("") }
    // survives configuration change
}

// Custom type requires explicit Saver
data class User(val id: Int, val name: String)
val userSaver = Saver<User, String>(
    save = { "${it.id}:${it.name}" },
    restore = { parts -> User(parts.split(":")[0].toInt(), parts.split(":")[1]) }
)
var user by rememberSaveable(stateSaver = userSaver) { mutableStateOf(User(1, "Alice")) }
```

**Pitfall:** Assuming `rememberSaveable` works with all types. Custom classes need explicit `Saver` or `@Parcelize`. See `SaveableStateRegistry` in `androidx.compose.runtime.saveable`.

## State Hoisting

Move state up to a parent composable to enable reusability and testing.

### Stateful vs Stateless Pattern

```kotlin
// ❌ Stateful version (tightly coupled)
@Composable
fun Counter() {
    var count by remember { mutableIntStateOf(0) }
    Button(onClick = { count++ }) { Text(count.toString()) }
}

// ✅ Stateless version (reusable, testable)
@Composable
fun Counter(
    count: Int,
    onCountChange: (Int) -> Unit
) {
    Button(onClick = { onCountChange(count + 1) }) { Text(count.toString()) }
}

// ✅ Wrapper composable (provides state, uses stateless child)
@Composable
fun StatefulCounter() {
    var count by remember { mutableIntStateOf(0) }
    Counter(count = count, onCountChange = { count = it })
}
```

**Rule:** Push state as high as needed, but no higher. If only one child needs state, keep it there. If multiple children or parents need it, hoist up.

## derivedStateOf

Computes a value from existing state, recomputing only when dependencies change.

```kotlin
// ❌ Reads the scroll offset (changes every frame) in a large scope
val showButton = scrollState.value > 0

// ✅ Readers recompose only when the boolean flips
val showButton by remember { derivedStateOf { scrollState.value > 0 } }
```

**When to use:**
- Expensive computations from state (e.g., filtering, sorting lists)
- Combining multiple state values
- Creating intermediate state for conditional logic

```kotlin
@Composable
fun UserList(users: List<User>, filterText: String) {
    val filteredUsers = derivedStateOf {
        users.filter { it.name.contains(filterText, ignoreCase = true) }
    }

    LazyColumn {
        items(filteredUsers.value.size) { index ->
            UserRow(filteredUsers.value[index])
        }
    }
}
```

**Pitfall:** Using `derivedStateOf` for cheap operations (String concatenation, simple conditions) adds overhead. Only use when the computation is non-trivial.

**Pitfall:** a state read inside a lambda is tracked by whichever scope *runs* the lambda. A lambda run during layout or draw (`offset { }`, `graphicsLayer { }`, `drawBehind { }`) creates a dependency in that phase only; a lambda run later from an event callback (`onClick`) creates none. Use `snapshotFlow` to observe state from a coroutine.

## snapshotFlow

Converts Compose state to Kotlin Flow for side effects and external APIs.

```kotlin
@Composable
fun SearchScreen(viewModel: SearchViewModel) {
    var query by remember { mutableStateOf("") }

    LaunchedEffect(Unit) {
        snapshotFlow { query }
            .debounce(500)
            .distinctUntilChanged()
            .collect { viewModel.search(it) }
    }
}
```

**Key behaviors:**
- Emits initial value, then only on changes
- Works with derivedStateOf, collections, and nested state
- Runs in the composition's coroutine scope (launched via `LaunchedEffect`)

**Pitfall:** Accessing state directly in a `LaunchedEffect` doesn't track changes:
```kotlin
// ❌ Won't re-run when query changes
LaunchedEffect(Unit) {
    viewModel.search(query)  // Capture at launch time only
}

// ✅ Re-runs when query changes
LaunchedEffect(query) {
    viewModel.search(query)
}
```

## SnapshotStateList and SnapshotStateMap

Observable collections that trigger recomposition on structural changes.

```kotlin
val items = remember { mutableStateListOf<Item>() }
items.add(Item(1, "First"))
items[0] = Item(1, "Updated")
items.removeAt(0)

val map = remember { mutableStateMapOf<String, String>() }
map["key"] = "value"  // Triggers recomposition
```

**Important:** Changes to list contents trigger recomposition, but changes to list *elements* (if they're mutable objects) do not.

```kotlin
data class Item(val id: Int, var name: String)

val items = remember { mutableStateListOf(Item(1, "First")) }

// ✅ Triggers recomposition (list structure changed)
items[0] = Item(1, "Updated")

// ❌ Does NOT trigger recomposition (object mutated in-place)
items[0].name = "Updated"  // Mutated but list reference unchanged

// ✅ Correct: use copy() or mutableStateOf for nested state
items[0] = items[0].copy(name = "Updated")
```

See source: `androidx.compose.runtime.snapshots` for collection implementation.

## @Stable and @Immutable Annotations

These annotations help the compiler optimize recomposition (strong skipping mode).

### @Immutable
- All public fields are read-only primitives or other `@Immutable` types
- Instances never change after construction
- Compiler can skip recomposition if parameter unchanged

```kotlin
@Immutable
data class User(val id: Int, val name: String)
```

### @Stable
- Implements structural equality (`equals`)
- Public properties are read-only or observable
- Changes are always notified to Compose (through state objects)
- Weaker guarantee than `@Immutable`, but suitable for types with observable state

```kotlin
@Stable
class UserViewModel {
    val userName: State<String> = mutableStateOf("")
    val isLoading: State<Boolean> = mutableStateOf(false)

    // Observable state, not direct properties
}
```

Do not add stability annotations reflexively. The compiler can infer many
immutable types, and strong skipping can skip unstable parameters by identity.
Annotate only when the type actually satisfies the documented contract.

```kotlin
// May be unstable; measure before changing it.
class Config(val title: String, val color: Color)

// ✅ Properly annotated
@Immutable
class Config(val title: String, val color: Color)
```

## Strong Skipping Mode

Strong skipping is enabled by default with Kotlin 2.0.20 and newer.

**What changed:**
- Stable parameters are compared with object equality; unstable parameters use
  instance equality.
- Lambdas created inside composition are remembered automatically.
- Skipping still has comparison/bookkeeping cost; first avoid invalidations.
- The Kotlin Compose compiler plugin version must match Kotlin. Do not configure
  the obsolete `kotlinCompilerExtensionVersion` property in modern projects.

**Practical impact:**
```kotlin
// New unstable instances cannot be skipped by identity.
@Composable
fun Parent() {
    Child(title = buildString { append("Title") })
    Child(config = Config(...))  // Unstable type
}

// ✅ Cache instances
@Composable
fun Parent() {
    val title = remember { "Title" }
    val config = remember { Config(...) }
    Child(title = title)
    Child(config = config)
}
```

## State in ViewModels: StateFlow vs Compose State

### StateFlow (strong default for ViewModels)
- Survives composition recomposition and configuration changes
- Works with lifecycle (`collectAsStateWithLifecycle`)
- Safe to read from any thread; update atomically with `_state.update { }`, not `_state.value++` (read-modify-write races)

```kotlin
class UserViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()
}

@Composable
fun UserScreen(viewModel: UserViewModel) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when (uiState) {
        is UiState.Loading -> LoadingScreen()
        is UiState.Success -> SuccessScreen((uiState as UiState.Success).data)
        is UiState.Error -> ErrorScreen((uiState as UiState.Error).message)
    }
}
```

### Compose State
- Use `remember` for temporary UI-local state; it is lost when that composition leaves.
- Snapshot state may also live in a testable state holder or ViewModel when
  atomic snapshots/dynamic read tracking are required; see `appstate.md`.
- Keep mutation private regardless of the state primitive.

```kotlin
@Composable
fun SearchScreen(viewModel: SearchViewModel) {
    var showFilters by remember { mutableStateOf(false) }  // UI-only
    val searchResults by viewModel.searchResults.collectAsStateWithLifecycle()

    SearchUI(
        results = searchResults,
        showFilters = showFilters,
        onToggleFilters = { showFilters = !showFilters }
    )
}
```

**Key difference:** `collectAsStateWithLifecycle()` (in `androidx.lifecycle:lifecycle-runtime-compose`) collects only when the composable is in a STARTED state, avoiding memory leaks.

## Common Anti-Patterns

### State in Local Variables
```kotlin
// ❌ Lost on recomposition
@Composable
fun Counter() {
    var count = 0  // Reset to 0 on every recomposition
    Button(onClick = { count++ }) { Text(count.toString()) }
}

// ✅ Correct
@Composable
fun Counter() {
    var count by remember { mutableIntStateOf(0) }
    Button(onClick = { count++ }) { Text(count.toString()) }
}
```

### Reading State Inside an Effect vs Keying the Effect
```kotlin
// Reads the CURRENT value each iteration (the delegate reads State.value);
// the effect just does not restart when count changes.
var count by remember { mutableIntStateOf(0) }
LaunchedEffect(Unit) {
    while (true) {
        delay(1000)
        println(count)
    }
}

// Key the effect only when it must RESTART on change. Keying on a value that
// changes every frame (for example an animation's .value) relaunches every frame.
LaunchedEffect(count) {
    println("Count changed: $count")
}
```

### Creating State in Lambdas
```kotlin
// ❌ Creates new state on every call
val onButtonClick = {
    val newValue = remember { mutableStateOf(0) }  // ERROR: Can't call remember in lambda
}

// ✅ Create state at composition level
var value by remember { mutableIntStateOf(0) }
val onButtonClick = { value++ }
```

---

**Source references:** `androidx.compose.runtime.State`, `androidx.compose.runtime.saveable`, `androidx.lifecycle.runtime.compose`

---

## produceState

Bridge between suspend functions and Compose state:

```kotlin
@Composable
fun UserProfile(userId: String): State<User?> = produceState<User?>(initialValue = null, userId) {
    value = repository.getUser(userId)
}
```

Use when you need to convert a suspend function result into observable State. The coroutine is scoped to the composition and cancelled when the composable leaves.

Can also observe flows:
```kotlin
@Composable
fun NetworkStatus(): State<Boolean> = produceState(initialValue = false) {
    connectivityManager.observeNetworkState().collect { value = it }
}
```

---

## rememberUpdatedState

Capture latest callback value in long-running effects:

```kotlin
@Composable
fun Timer(onTimeout: () -> Unit) {
    val currentOnTimeout by rememberUpdatedState(onTimeout)
    LaunchedEffect(true) {
        delay(5000L)
        currentOnTimeout() // Always calls the latest onTimeout, even if it changed
    }
}
```

Use when: a LaunchedEffect captures a callback that might change, but you don't want to restart the effect. Without `rememberUpdatedState`, the effect would use the stale original callback or need to restart on every callback change.

---

## Sealed UiState Pattern

```kotlin
sealed interface UiState<out T> {
    data object Loading : UiState<Nothing>
    data class Success<T>(val data: T) : UiState<T>
    data class Error(val message: String) : UiState<Nothing>
}
```

Smart-cast safety:
```kotlin
// BAD: smart cast can fail if uiState changes between check and usage
if (uiState is UiState.Success) {
    Content((uiState as UiState.Success).data) // Unsafe cast
}

// GOOD: val capture for safe smart cast
when (val state = uiState) {
    is UiState.Loading -> LoadingIndicator()
    is UiState.Success -> Content(state.data) // Safe smart cast via val
    is UiState.Error -> ErrorMessage(state.message)
}
```

---

## State Holder Class Pattern

For complex screens with multiple interrelated state values, create a state holder:

```kotlin
@Composable
fun rememberSearchState(
    listState: LazyListState = rememberLazyListState(),
    coroutineScope: CoroutineScope = rememberCoroutineScope()
): SearchState = remember(listState, coroutineScope) {
    SearchState(listState, coroutineScope)
}

@Stable
class SearchState(
    val listState: LazyListState,
    private val coroutineScope: CoroutineScope
) {
    var query by mutableStateOf("")
        private set

    val isScrolled: Boolean
        get() = listState.firstVisibleItemIndex > 0

    fun updateQuery(newQuery: String) { query = newQuery }
    fun scrollToTop() { coroutineScope.launch { listState.animateScrollToItem(0) } }
}
```

This pattern (used by `rememberScrollState`, `rememberDrawerState`, etc.) groups related state and logic into a single class, avoiding parameter bloat in composables.

---

## Production State Rules

### 1. Choose state semantics deliberately in ViewModels

```kotlin
// Flow is a strong default when non-Compose consumers or stream operators matter.
class MyViewModel : ViewModel() {
    private val _name = MutableStateFlow("")
    val name = _name.asStateFlow()

    fun updateName(new: String) { _name.value = new }
}
```

Compose runtime state is also supported outside UI. Jetpack AppState provides
`Transform` and `StateStore` for ViewModels, repositories, managers, and
services. Use snapshot state when its atomic snapshots or dynamic read tracking
provide a concrete benefit; keep mutations private and test the state holder.
See `appstate.md`. Do not enforce a blanket ban on `mutableStateOf` in ViewModels.

### 2. SharedFlow for one-shot events, NOT Channel

```kotlin
// GOOD: SharedFlow with buffer for one-shot events
private val _events = MutableSharedFlow<AppEvent>(extraBufferCapacity = 1)
val events = _events.asSharedFlow()

// Emit from ViewModel
fun onAction() { _events.tryEmit(AppEvent.ShowSnackbar("Done")) }

// Collect in composable
LaunchedEffect(Unit) {
    viewModel.events.collect { event ->
        when (event) {
            is AppEvent.ShowSnackbar -> snackbarHostState.showSnackbar(event.message)
            is AppEvent.Navigate -> onNavigate(event.route)
        }
    }
}
```

### 3. rememberSaveable only at NavGraph level

Use `rememberSaveable` for screen-level state (search query, tab selection) at the NavGraph entry point, not deep inside composable trees where it adds unnecessary persistence overhead.

### 4. snapshotFlow + distinctUntilChanged() for reactive scroll

```kotlin
LaunchedEffect(listState) {
    snapshotFlow { listState.firstVisibleItemIndex }
        .distinctUntilChanged()
        .collect { index -> viewModel.onScrollPositionChanged(index) }
}
```

### 5. .stateIn() with .map() for derived flows

```kotlin
val filteredItems = repository.items
    .map { items -> items.filter { it.isActive } }
    .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())
```

---

## Compose Multiplatform Notes

### rememberSaveable and Bundle

`rememberSaveable`, `Bundle`, and `@Parcelize` are **Android-only**. On CMP targets:

```kotlin
// Android: @Parcelize works
@Parcelize
data class SearchParams(val query: String, val filters: List<String>) : Parcelable

// CMP: use @Serializable instead
@Serializable
data class SearchParams(val query: String, val filters: List<String>)
```

For state persistence across configuration changes in CMP, use kotlinx.serialization-based custom `Saver` implementations.

### collectAsStateWithLifecycle

`collectAsStateWithLifecycle()` is in `androidx.lifecycle:lifecycle-runtime-compose` -- it's Android-specific.

```kotlin
// Android: lifecycle-aware, stops collecting when paused
val state by viewModel.uiState.collectAsStateWithLifecycle()

// CMP commonMain: basic collection, does NOT stop in background
val state by viewModel.uiState.collectAsState()

// CMP with multiplatform lifecycle (lifecycle-runtime-compose:2.10.0+):
// collectAsStateWithLifecycle() available in commonMain
```

On CMP without the multiplatform lifecycle library, flows continue collecting when the app is backgrounded -- be aware of battery and performance implications.
