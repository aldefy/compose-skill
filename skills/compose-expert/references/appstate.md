# Jetpack AppState

> AppState is alpha. Its APIs may change. Use it deliberately and pin exact
> versions rather than treating it as the default replacement for Flow.

Jetpack AppState extends Compose snapshot state beyond rendered UI. It contains:

- **Transform** — runs a headless `@Composable` block and exposes its result as
  `State<T>`.
- **StateStore** — a type-safe, application-scoped container for shared Compose
  state, with optional DataStore persistence.

## Transform

Use `transform` when state derivation needs Compose runtime features such as
dynamic state-read tracking, `collectAsState`, `remember`, `produceState`, or
`LaunchedEffect`.

```kotlin
val uiState: State<HomeUiState> = transform(
    initialValue = HomeUiState.Loading,
    scope = viewModelScope,
) {
    val isOnline by networkMonitor.isOnline
    val items = if (isOnline) {
        repository.remoteItems.collectAsState(initial = null).value
    } else {
        repository.cachedItems.collectAsState(initial = null).value
    }
    items?.let(HomeUiState::Content) ?: HomeUiState.Loading
}
```

Modules using `transform` or `listener` contain composable code even if they
have no UI. Enable the Compose compiler plugin for those modules.

### Transform lifecycle

A transform tied to `viewModelScope` continues while that ViewModel is alive,
including when no UI is visible. A transform created inside a composable follows
that composition. Choose the scope based on required work, not convenience.

Use `transformTest` and controlled test dispatchers for deterministic tests.

## listener

Use `listener` when a non-UI component must react to state changes without
exposing a derived state value. Side effects launched inside its composition are
cancelled when their branch leaves composition or the listener coroutine stops.

This is useful for timers and notifications, but it is not an event queue.

## StateStore

Create a `StateStore` at application or feature scope and inject narrow manager
interfaces into consumers. Do not pass the store itself throughout the UI.

Use typed `StateStoreKey` definitions, centralize mutations, and persist only
keys that must survive process death. The DataStore integration is for durable
state, not high-frequency transient UI values.

## Decision table

| Need | Prefer |
|---|---|
| Local UI editing/interaction state | `remember` / `rememberSaveable` |
| Synchronous derivation from existing `State` | `computedStateOf` or `derivedStateOf`, version/use-case dependent |
| Async stream where every value matters | `Flow` |
| Dynamic combination requiring composable APIs | AppState `transform` |
| Shared current state across app components | AppState `StateStore` |
| One-shot events or ordered transactions | `Flow`/channel-based event pipeline, not snapshot state |

`transform` represents the latest state. Rapid intermediate values may be
coalesced and equal values do not trigger recomposition. Do not use it for audit
logs, queues, running totals, payment events, or anything that must process every
value exactly once.

## ViewModels and Compose state

The old blanket rule “`mutableStateOf` must never appear in a ViewModel” is no
longer accurate. Compose runtime state is a general state engine and AppState
officially supports it outside UI.

The practical rule is:

- expose state with clear ownership;
- avoid leaking mutable state to callers;
- use `Flow` where stream semantics or non-Compose consumers require it;
- use snapshot state when atomic snapshot behavior and dynamic read tracking
  provide a concrete advantage;
- test without relying on a rendered UI.

## Sources

- Overview: https://developer.android.com/topic/libraries/architecture/appstate
- Transform: https://developer.android.com/topic/libraries/architecture/appstate/transform
- StateStore: https://developer.android.com/topic/libraries/architecture/appstate/statestore
- State outside UI: https://developer.android.com/topic/libraries/architecture/appstate/state-beyond-ui
