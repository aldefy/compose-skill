# Paging 3 — MVI Integration and Testing

The MVI dual-flow pattern, test recipes, and the anti-patterns that bite hardest
in production. Builds on `paging.md`.

## Dual-flow MVI

`PagingData` does not belong inside a `UiState` `StateFlow`. The ViewModel
exposes:

- `state: StateFlow<UiState>` — non-paging concerns (filters, selection mode,
  errors, transient flags)
- `items: Flow<PagingData<T>>` — paging stream, reacts to filter changes via
  `flatMapLatest`

```kotlin
class ItemListViewModel(
    private val repository: ItemRepository,
) : ViewModel() {

    private val _state = MutableStateFlow(ItemListState())
    val state: StateFlow<ItemListState> = _state.asStateFlow()

    private val _statusFilter = MutableStateFlow(StatusFilter.ALL)

    val items: Flow<PagingData<ItemUi>> = _statusFilter
        .distinctUntilChanged()
        .flatMapLatest { status ->
            Pager(
                config = PagingConfig(pageSize = 20),
                pagingSourceFactory = { repository.itemPagingSource(status) },
            ).flow.map { it.map { dto -> dto.toUi() } }
        }
        .cachedIn(viewModelScope)

    fun onEvent(event: ItemListEvent) {
        when (event) {
            is ItemListEvent.FilterChanged -> {
                _statusFilter.value = event.filter
                _state.update { it.copy(selectedFilter = event.filter) }
            }
            is ItemListEvent.SelectionToggled -> {
                _state.update { it.copy(selectedIds = it.selectedIds.toggle(event.id)) }
            }
            is ItemListEvent.ItemClicked -> {
                // emit navigation effect
            }
        }
    }
}
```

### Route composable collects both flows

The route composable is the only place that knows about the ViewModel. It
collects both flows and hands plain values to a stateless screen composable.

```kotlin
@Composable
fun ItemListRoute(viewModel: ItemListViewModel) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    val pagingItems = viewModel.items.collectAsLazyPagingItems()

    ItemListScreen(
        state = state,
        pagingItems = pagingItems,
        onEvent = viewModel::onEvent,
    )
}
```

The screen composable receives `LazyPagingItems` and `state` as parameters and
emits events through a callback. It has no knowledge of the ViewModel.

<!-- source: references/source-code/runtime-source.md — search "Snapshot" for why state collected via collectAsStateWithLifecycle and a separate LazyPagingItems flow do not interfere with each other's recomposition scopes -->

## Testing

### PagingSource unit test

```kotlin
@Test
fun `load returns page of items`() = runTest {
    val mockApi = MockItemApi(items = listOf(item1, item2))
    val pagingSource = ItemPagingSource(api = mockApi, query = "")

    val result = pagingSource.load(
        PagingSource.LoadParams.Refresh(key = null, loadSize = 20, placeholdersEnabled = false)
    )

    assertTrue(result is PagingSource.LoadResult.Page)
    val page = result as PagingSource.LoadResult.Page
    assertEquals(2, page.data.size)
    assertEquals(null, page.prevKey)
    assertEquals(2, page.nextKey)
}

@Test
fun `load returns error on network failure`() = runTest {
    val mockApi = MockItemApi(error = IOException("Network error"))
    val pagingSource = ItemPagingSource(api = mockApi, query = "")

    val result = pagingSource.load(
        PagingSource.LoadParams.Refresh(key = null, loadSize = 20, placeholdersEnabled = false)
    )

    assertTrue(result is PagingSource.LoadResult.Error)
}
```

### asSnapshot — flow-level integration test

`asSnapshot` (added in Paging 3.3) collects a `Flow<PagingData<T>>` into a list,
optionally driving scroll to force more loads.

```kotlin
@Test
fun `items flow loads first two pages`() = runTest {
    val viewModel = ItemListViewModel(FakeRepository())

    val snapshot = viewModel.items.asSnapshot {
        scrollTo(index = 30)
    }

    assertTrue(snapshot.size >= 30)
    assertEquals("item_1", snapshot.first().id)
}
```

### TestPager — transformation tests

```kotlin
@Test
fun `paging data maps dto to ui model`() = runTest {
    val dtos = listOf(ItemDto(id = "1", title = "Test", amount = 100.0))
    val pagingSource = dtos.asPagingSourceFactory().invoke()

    val pager = TestPager(PagingConfig(pageSize = 10), pagingSource)
    val result = pager.refresh() as PagingSource.LoadResult.Page

    assertEquals(1, result.data.size)
    assertEquals("1", result.data.first().id)
}
```

<!-- source: not bundled — TestPager and asSnapshot live in androidx.paging:paging-testing -->

## Anti-patterns

| Anti-pattern | Why it hurts | Fix |
|---|---|---|
| `PagingData` inside a `UiState` `StateFlow` | Any unrelated state change re-emits the wrapping `StateFlow`, replacing the flow that `collectAsLazyPagingItems()` is collecting and resetting scroll | Expose `PagingData` as its own top-level `Flow` |
| New `Pager` per recomposition | Duplicate network requests, lost pagination state | Hold the `Flow` as a `val` in the ViewModel |
| Reusing a `PagingSource` instance | Runtime crash: "PagingSource was re-used" | Always create a new instance inside `pagingSourceFactory` |
| Missing `cachedIn(viewModelScope)` | Pages lost on configuration change, duplicate loads | Always end the chain with `cachedIn` |
| Missing list keys | Scroll jumps, state corruption on prepend / insert | `itemKey { it.id }` with stable domain IDs |
| `combine` on `PagingData` flows | `IllegalStateException`: "Collecting from multiple PagingData concurrently" | Use `flatMapLatest` for parameter changes |
| Calling `refresh()` in a composable body | Refresh fires every recomposition — infinite loop | Call from event handler or `LaunchedEffect` |
| No `LoadState` UI handling | Broken UX: no loading indicator, no error recovery, no retry | Branch on `loadState.refresh` / `append` / `prepend` |
| Transformations after `cachedIn` | Transformations skipped on cache hit | `map` / `filter` / `insertSeparators` go **before** `cachedIn` |
| `catch (Exception)` in `PagingSource` | Hides real bugs as recoverable errors | Catch `IOException` and `HttpException` specifically |

<!-- source: references/source-code/foundation-source.md — search "LazyList" for how scroll position is tied to item identity, which is why missing keys cause the visible jump anti-pattern above -->

## Related

- Core setup → `paging.md`
- Offline-first with `RemoteMediator` → `paging-offline.md`
- Lazy layout key/contentType mechanics → `lists-scrolling.md`
