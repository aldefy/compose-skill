# Migrating from Navigation 2 to Navigation 3

Navigation 3 reframes navigation as state you own. The library no longer holds
the back stack — your composable does, as a `SnapshotStateList`. This file
covers the conceptual shifts, the mechanical migration steps, and a decision
guide for whether to migrate at all.

> Navigation 2 is **not deprecated**. Migration is optional. See
> "Choosing Nav 2 vs Nav 3" below before committing to a port.

For Nav 2 reference, see `navigation.md`.

## Conceptual shifts

| Nav 2 | Nav 3 |
|---|---|
| `NavController` owns the back stack | You own the back stack — a `SnapshotStateList<NavKey>` |
| `NavHost` renders composable destinations | `NavDisplay` observes the back stack and renders the top entry |
| Routes are strings or `@Serializable` types | Keys are `@Serializable` types implementing `NavKey` |
| Imperative: `navController.navigate(Detail(id))` | List ops: `backStack.add(Detail(id))`, `backStack.removeLastOrNull()` |
| `NavGraph` groups destinations | No graph object — entries are resolved by an `entryProvider` lambda |
| Library parses deep links | Your code parses URIs and constructs the back stack |
| Graph-scoped ViewModels via `getBackStackEntry()` | Entry-scoped ViewModels via `rememberViewModelStoreNavEntryDecorator()` |
| `currentBackStackEntryAsState()` for tab selection | Inspect the list directly: `backStack.last()` |
| `saveState` / `restoreState` for tab persistence | Per-tab back stacks held in your state, or a root-swap pattern |

<!-- source: references/source-code/navigation-source.md — search "NavController" and "NavBackStackEntry" for the Nav 2 ownership model this migration moves away from -->

## Migration steps

### 1. Mark route types as `NavKey`

```kotlin
// Nav 2
@Serializable data object Home
@Serializable data class Detail(val id: String)

// Nav 3
@Serializable data object Home : NavKey
@Serializable data class Detail(val id: String) : NavKey
```

### 2. Replace `NavController` with a back-stack list

```kotlin
// Nav 2
val navController = rememberNavController()
navController.navigate(Detail(id))

// Nav 3
val backStack = rememberNavBackStack(Home)
backStack.add(Detail(id))
```

`rememberNavBackStack` returns a `SnapshotStateList<NavKey>` that integrates
with Compose snapshots — mutating it inside an event handler triggers the right
recompositions in `NavDisplay`.

### 3. Replace `NavHost` with `NavDisplay`

`NavHost { composable<T> { ... } }` becomes `NavDisplay { entryProvider { entry<T> { ... } } }`.
Each `composable<T>` block becomes an `entry<T>` block. Calls to
`navController.navigate(...)` become `backStack.add(...)`. Calls to `popBackStack()`
become `backStack.removeLastOrNull()`.

### 4. Replace graph-scoped ViewModels with entry decorators

Nav 3 scopes a `ViewModelStore` to each back-stack entry automatically through
`rememberViewModelStoreNavEntryDecorator()`. There is no graph scope — for state
that needs to outlive a single entry, lift it to a parent composable or scope a
ViewModel at the Activity / App level.

```kotlin
// Nav 2 — graph-scoped via getBackStackEntry
val parentEntry = remember(entry) { navController.getBackStackEntry("checkout") }
val sharedViewModel: CheckoutViewModel = hiltViewModel(parentEntry)

// Nav 3 — share at a higher scope, or hoist state to a parent composable
val sharedViewModel: CheckoutViewModel = viewModel() // Activity-scoped
```

### 5. Parse deep links yourself

Nav 3 does not parse deep links. Parse the URI in your platform entry point
(Activity, scene delegate, etc.) and construct the back stack manually:

```kotlin
// Nav 2
composable<Detail>(
    deepLinks = listOf(navDeepLink<Detail>(basePath = "https://example.com/detail"))
) { /* ... */ }

// Nav 3
LaunchedEffect(deepLinkId) {
    if (deepLinkId != null) {
        backStack.clear()
        backStack.addAll(listOf(Home, Detail(deepLinkId)))
    }
}
```

### 6. Replace tab navigation

Nav 2's `popUpTo(saveState=true) + restoreState=true` pattern becomes direct
back-stack manipulation in Nav 3. The exact shape depends on whether you want
per-tab back stacks (hold one `SnapshotStateList` per tab) or a root-swap
(replace `backStack[0]`).

```kotlin
// Nav 2 — saveState / restoreState dance
navController.navigate(tab.route) {
    popUpTo(startDest) { saveState = true }
    launchSingleTop = true
    restoreState = true
}

// Nav 3 — root swap
while (backStack.size > 1) backStack.removeLast()
backStack[0] = targetTopLevelKey
```

## Incremental migration

You do not have to migrate everything at once.

1. **Start with leaf screens.** Few inbound dependencies, easiest to port.
2. **Migrate shared / graph-scoped ViewModels last.** They require the most
   restructuring because Nav 3 has no graph scope.
3. **Coexist during the transition.** A Nav 2 destination can launch an
   Activity that hosts Nav 3, or vice versa. Bridge at the Activity boundary.
4. **Convert navigation effects one screen at a time.** Update ViewModel effect
   handlers from `navController.navigate(...)` to `backStack.add(...)` per
   screen, not in a single sweep.
5. **Test each migrated screen in isolation** before moving on.

## Choosing Nav 2 vs Nav 3

The biggest trap in this decision is treating Nav 3 as "the new Nav 2." It is
not — it is a different ownership model. Make the call against your project
constraints, not novelty.

### Pick Nav 3 when

- **You are on Compose Multiplatform or planning to be.** Compose Multiplatform
  1.10+ supports Nav 3 across Android, iOS, desktop, and web. Nav 2 is
  Android-only. If `commonMain` is on the roadmap, Nav 3 is the only option that
  survives the move — porting twice is wasted effort. Caveat for non-JVM targets
  (iOS, web): `NavKey` types need polymorphic serialisation registered through a
  `SavedStateConfiguration`, since Nav 3's Android path uses reflection that
  isn't available there.
- **You want type-safe destinations end-to-end and full back-stack control.**
  Nav 3's back stack is plain `SnapshotStateList` state; serialising it for
  process death, mirroring it across windows, or driving it from a state
  machine is straightforward in a way it never was with Nav 2.
- **You are starting a greenfield Compose project.** No existing graph to port,
  no string routes to grandfather, no graph-scoped ViewModels to redesign.

### Stay on Nav 2 when

- **Android-only app with a complex existing graph.** Nav 2 is not deprecated.
  Migration cost is real — graph scoping, deep link declarations, and tab
  saveState/restoreState all require restructuring. If the current setup is
  working, "it's newer" is not a sufficient reason.
- **Heavy reliance on graph-scoped ViewModels.** Nav 3 scopes ViewModels per
  back-stack entry through the `Nav3 Lifecycle ViewModel` add-on; there is no
  direct equivalent of Nav 2's graph scope (`getBackStackEntry("graphRoute")`).
  Sharing ViewModels across entries means lifting state to a parent composable
  or to a higher DI scope, which often ripples into module boundaries.
- **You depend on library-managed deep links.** The Nav 3 migration guide
  lists deep links under "unsupported features" today — you parse URIs in your
  platform entry point and construct the back stack yourself. If you have a
  large surface of Nav 2 `navDeepLink<T>` declarations, porting them means
  writing your own URI parser before you ship.

### Hybrid is fine

A Nav 2 app that introduces a new Compose-Multiplatform feature module on Nav 3
is a reasonable shape. Bridge at the Activity boundary. Don't try to interleave
the two systems inside a single screen graph.

<!-- source: references/source-code/navigation-source.md — search "NavController" and "NavHost" for the Nav 2 ownership model the decision guide above contrasts with. Nav 3's NavDisplay/NavKey/backStack APIs are not bundled in this skill's source-code receipts. -->

## Advanced Nav 3 patterns

Because you own the back stack as plain `SnapshotStateList<NavKey>` state, the
hard navigation problems become ordinary state problems — but a few have a
non-obvious idiomatic shape. All of the following are verified against the Nav 3
guidance (developer.android.com/guide/navigation/navigation-3).

### Returning a result to the previous destination

There is no `SavedStateHandle`/`previousBackStackEntry.savedStateHandle` result
API in Nav 3. Because both screens' state is in your hands, pass a callback into
the destination when you push it, or write to shared state the caller observes.

```kotlin
// Callback captured when pushing the picker; picker returns via it, then pops.
entry<PickColor> {
    ColorPickerScreen(
        onPicked = { color ->
            selectedColor = color        // hoisted state the caller reads
            backStack.removeLastOrNull() // pop back to the caller
        },
    )
}
```

Prefer hoisted state (a shared ViewModel or a state holder) over a callback when
the result must survive process death — a lambda captured in the back stack is
not serialisable.

### Conditional / auth-gated navigation

Don't try to "block" a destination. Derive the back stack from auth state: when
the user logs out, swap the root; when a deep link targets a gated screen while
logged out, build a stack that lands on login first.

```kotlin
// The back stack is a function of auth state — recompute the root on change.
LaunchedEffect(isLoggedIn) {
    if (!isLoggedIn) {
        backStack.clear()
        backStack.add(Login)
    }
}

// A gated deep link while logged out: land on Login, not the gated screen.
fun handleDeepLink(target: NavKey, isLoggedIn: Boolean) {
    backStack.clear()
    if (isLoggedIn) backStack.add(target) else { backStack.add(Login) /* resume target post-login */ }
}
```

### Animated transitions between destinations

`NavDisplay` animates entry changes. Set default transitions on the display, or
per-entry via `NavEntry` metadata. For shared elements across destinations, wrap
`NavDisplay` in a `SharedTransitionLayout` and pass
`LocalNavAnimatedContentScope.current` down to the shared composables.

```kotlin
SharedTransitionLayout {
    NavDisplay(
        backStack = backStack,
        // sharedTransitionScope drives cross-entry element animation
        entryProvider = entryProvider {
            entry<HomeRoute> {
                HomeScreen(
                    sharedTransitionScope = this@SharedTransitionLayout,
                    animatedVisibilityScope = LocalNavAnimatedContentScope.current,
                    onItemClick = { backStack.add(DetailsRoute(it)) },
                )
            }
            entry<DetailsRoute> { key ->
                DetailsScreen(
                    id = key.item,
                    sharedTransitionScope = this@SharedTransitionLayout,
                    animatedVisibilityScope = LocalNavAnimatedContentScope.current,
                    onBack = { backStack.removeLastOrNull() },
                )
            }
        },
    )
}
```

### Adaptive list-detail (two-pane) with Nav 3

For list-detail / supporting-pane layouts, don't hand-roll pane logic on top of
the back stack — use the adaptive scaffold. `NavigableListDetailPaneScaffold`
manages its own pane navigator; drive back with
`BackNavigationBehavior.PopUntilScaffoldValueChange` so a phone pops pane-by-pane
while a tablet keeps both panes visible.

```kotlin
NavigableListDetailPaneScaffold(
    navigator = navigator,
    listPane = { AnimatedPane { ListContent(onItemClick = { scope.launch {
        navigator.navigateTo(ListDetailPaneScaffoldRole.Detail, it)
    } }) } },
    detailPane = { AnimatedPane { DetailContent(onClose = { scope.launch {
        navigator.navigateBack(BackNavigationBehavior.PopUntilScaffoldValueChange)
    } }) } },
)
```

Keep the adaptive scaffold *inside* one Nav 3 destination — the scaffold owns
pane state; the outer `NavDisplay` owns screen-level navigation. Don't mix the
two levels.

### Multiple back stacks (per-tab) done right

Hold one `SnapshotStateList<NavKey>` per top-level tab and render the active
one. Each tab keeps its own history across tab switches — the correct
replacement for Nav 2's `saveState`/`restoreState`.

```kotlin
val tabStacks = remember {
    mutableStateMapOf(
        Tab.Home to mutableStateListOf<NavKey>(Home),
        Tab.Search to mutableStateListOf<NavKey>(Search),
    )
}
var activeTab by rememberSaveable { mutableStateOf(Tab.Home) }
val backStack = tabStacks.getValue(activeTab)  // NavDisplay renders this one

NavDisplay(backStack = backStack, entryProvider = entryProvider { /* ... */ })
```

For serialisable per-tab history across process death, back each tab's list with
`rememberNavBackStack(...)` rather than a bare `mutableStateListOf`.

## Related

- Nav 2 reference (current production patterns) → `navigation.md`
- Side-effect rules around navigation calls (`LaunchedEffect`, no-navigate-in-composition) → `side-effects.md`
