# Paging 3 in Compose

Reference: `androidx.paging:paging-compose` (3.3.x). The Paging Compose APIs
(`LazyPagingItems`, `collectAsLazyPagingItems`, `itemKey`, `itemContentType`,
`LoadState`) live in a separate Jetpack library and are **not** bundled in this
skill's `source-code/` receipts. Where Paging touches Compose foundation primitives
(`LazyColumn`, `HorizontalPager`), citations point to bundled foundation source.

## Critical Rules

1. **`PagingData` is its own `Flow` — never wrap it inside a `UiState` `StateFlow`.**
   Any unrelated state change re-emits the wrapping `StateFlow`, which gives
   `collectAsLazyPagingItems()` a brand-new flow and resets scroll. Expose two
   properties: `state: StateFlow<UiState>` and `pagingData: Flow<PagingData<T>>`.
2. **Build the `Pager` once.** Hold it as a `val` in the ViewModel. A new `Pager`
   per recomposition means duplicate network calls and lost pagination state.
3. **Always `cachedIn(viewModelScope)`.** Without it, you lose pages on every
   configuration change and re-fetch from page 1.
4. **Stable keys.** `itemKey { it.id }` — without keys, prepend/insert shifts
   indices and the list scrolls on its own.
5. **Use `flatMapLatest` to react to filter/query changes.** Never `combine` two
   `PagingData` flows — Paging will throw `IllegalStateException: Collecting from
   multiple PagingData concurrently`.

## Dependencies

```kotlin
// Android / commonMain (KMP-safe since 3.3.0-alpha02)
implementation("androidx.paging:paging-compose:3.3.6")
implementation("androidx.paging:paging-common:3.3.6")
testImplementation("androidx.paging:paging-testing:3.3.6")
```

`paging-common` and `paging-compose` work in `commonMain` (Android, JVM, iOS).
`paging-runtime` is Android-only (RecyclerView adapters) and is not needed for
Compose. Verify Web/Wasm support against the version you pin.

### Dependency verification rule

Before suggesting a Paging API to a user, confirm the version they have actually
ships it. Paging 3.2 → 3.3 added KMP source sets and `asSnapshot`; older versions
will not have them. Check the user's `libs.versions.toml` or `build.gradle.kts`
before recommending an API surface.

## Data flow

```
PagingSource ──► Pager(config, factory) ──► Flow<PagingData<T>>
                                              │
                                              ▼  .cachedIn(viewModelScope)
                                              │
                                              ▼  collectAsLazyPagingItems()
                                              │
                                              ▼  LazyColumn / LazyVerticalGrid / Pager
```

| Component | Role |
|---|---|
| `PagingSource<Key, Value>` | Loads a single source one page at a time |
| `RemoteMediator` | Coordinates network + local DB — see `paging-offline.md` |
| `Pager` | Builds `Flow<PagingData<T>>` from a config + source factory |
| `PagingConfig` | Page size, prefetch distance, placeholder behaviour |
| `LazyPagingItems<T>` | Compose-side wrapper consumed by lazy layouts |

## PagingSource

```kotlin
class ItemPagingSource(
    private val api: ItemApi,
    private val query: String,
) : PagingSource<Int, ItemDto>() {

    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, ItemDto> {
        val page = params.key ?: 1
        return try {
            val response = api.getItems(page = page, limit = params.loadSize, query = query)
            LoadResult.Page(
                data = response.items,
                prevKey = if (page == 1) null else page - 1,
                nextKey = if (response.items.isEmpty()) null else page + 1,
            )
        } catch (e: IOException) {
            LoadResult.Error(e)
        } catch (e: HttpException) {
            LoadResult.Error(e)
        }
    }

    override fun getRefreshKey(state: PagingState<Int, ItemDto>): Int? =
        state.anchorPosition?.let { pos ->
            state.closestPageToPosition(pos)?.let { it.prevKey?.plus(1) ?: it.nextKey?.minus(1) }
        }
}
```

**Rules:**
- The factory must return a **new instance** every call. Reusing one throws
  `"PagingSource was re-used"` at runtime.
- Catch only the exceptions you expect (`IOException`, `HttpException`). Catching
  `Exception` swallows real bugs.
- Return `null` for `prevKey`/`nextKey` to signal end of pagination.
- For cursor-based APIs, use `String` as the key type and pass the next cursor.

<!-- source: not bundled — PagingSource lives in androidx.paging:paging-common -->

## Pager and ViewModel wiring

```kotlin
class ItemListViewModel(
    private val repository: ItemRepository,
) : ViewModel() {

    private val _uiState = MutableStateFlow(ItemListState())
    val uiState: StateFlow<ItemListState> = _uiState.asStateFlow()

    // PagingData is its own Flow — keep it out of UiState.
    val items: Flow<PagingData<ItemUi>> = Pager(
        config = PagingConfig(
            pageSize = 20,
            prefetchDistance = 5,
            enablePlaceholders = false,
            initialLoadSize = 40,
        ),
        pagingSourceFactory = { repository.itemPagingSource() },
    ).flow
        .map { pagingData -> pagingData.map { it.toUi() } }
        .cachedIn(viewModelScope)
}

data class ItemListState(
    val selectedFilter: FilterType = FilterType.ALL,
    val selectedIds: Set<String> = emptySet(),
)
```

| `PagingConfig` parameter | Purpose |
|---|---|
| `pageSize` | Items per page (required) |
| `prefetchDistance` | Distance from edge that triggers the next load |
| `enablePlaceholders` | Whether to expose null slots for un-loaded items |
| `initialLoadSize` | Items requested on first load (often `2 * pageSize`) |

## Invalidating after writes

After mutations (create/update/delete on the underlying source), call
`PagingSource.invalidate()`. The factory produces a fresh source and Paging
restarts from `getRefreshKey`.

```kotlin
class ItemRepository(private val api: ItemApi) {
    private var current: ItemPagingSource? = null

    fun itemPagingSource(query: String = ""): PagingSource<Int, ItemDto> =
        ItemPagingSource(api, query).also { current = it }

    fun invalidate() { current?.invalidate() }
}
```

## Reacting to filter / query changes

Use `flatMapLatest` on the parameter flow so each parameter change builds a new
`Pager`. Combine multiple parameter flows first, then `flatMapLatest`:

```kotlin
class ItemListViewModel(
    private val repository: ItemRepository,
) : ViewModel() {

    private val _query = MutableStateFlow("")
    private val _statusFilter = MutableStateFlow(StatusFilter.ALL)

    fun onQueryChanged(value: String) { _query.value = value }
    fun onStatusChanged(value: StatusFilter) { _statusFilter.value = value }

    val items: Flow<PagingData<ItemUi>> = combine(
        _query.debounce(300).distinctUntilChanged(),
        _statusFilter.distinctUntilChanged(),
    ) { query, status -> query to status }
        .flatMapLatest { (query, status) ->
            Pager(
                config = PagingConfig(pageSize = 20),
                pagingSourceFactory = { repository.itemPagingSource(query, status) },
            ).flow.map { it.map { dto -> dto.toUi() } }
        }
        .cachedIn(viewModelScope)
}
```

**Rules:**
- `distinctUntilChanged()` before `flatMapLatest` avoids redundant Pager creation.
- `debounce` on text input prevents one Pager per keystroke.
- `cachedIn` goes **after** `flatMapLatest`, never inside the lambda — caching
  inside means each new query throws away the cache.

## Compose UI with LazyPagingItems

```kotlin
@Composable
fun ItemListScreen(
    uiState: ItemListState,
    pagingItems: LazyPagingItems<ItemUi>,
    onEvent: (ItemListEvent) -> Unit,
) {
    LazyColumn {
        items(
            count = pagingItems.itemCount,
            key = pagingItems.itemKey { it.id },
            contentType = pagingItems.itemContentType { "item" },
        ) { index ->
            pagingItems[index]?.let { item ->
                ItemRow(
                    item = item,
                    isSelected = uiState.selectedIds.contains(item.id),
                    onClick = { onEvent(ItemListEvent.ItemClicked(item.id)) },
                )
            }
        }
    }
}
```

| Operation | Behaviour |
|---|---|
| `pagingItems[index]` | Reads the item **and** triggers a load if needed |
| `pagingItems.peek(index)` | Reads without triggering a load |
| `pagingItems.retry()` | Retries the last failed load |
| `pagingItems.refresh()` | Reloads from the start — **never** call from a composable body |
| `pagingItems.itemKey { }` | Stable identity for diffing |
| `pagingItems.itemContentType { }` | Layout reuse hint |

`LazyPagingItems` works with every lazy layout — `LazyColumn`, `LazyRow`,
`LazyVerticalGrid`, `LazyHorizontalGrid`, `HorizontalPager`, `VerticalPager`.
Prefer the `items(count, key, contentType)` overload over `itemsIndexed` —
indices shift on prepend, keys do not.

<!-- source: references/source-code/foundation-source.md — search "LazyList" for the items(count, key, contentType) overload; search "Pager" for HorizontalPager/VerticalPager integration -->

## LoadState handling

| State | `refresh` | `append` / `prepend` |
|---|---|---|
| `Loading` | Initial load or pull-to-refresh | Loading next/previous page |
| `Error(throwable)` | Initial load failed | Page load failed |
| `NotLoading(endReached)` | Idle | No more pages / idle |

Pattern: branch on `pagingItems.loadState.refresh`. Show full-screen
loading/error/empty only when `itemCount == 0`. With items already on screen,
use a thin top-of-list `LinearProgressIndicator` for refresh, and an inline
loading/error row at the bottom for `append` with a `retry()` button.

**RemoteMediator note:** check `loadState.source.refresh` instead of
`loadState.refresh`. The convenience property may report complete before Room
finishes its write transaction. Details in `paging-offline.md`.

## PagingData transformations

Apply transformations on the outer `Flow` **before** `cachedIn`. Anything after
`cachedIn` is dropped on cache hit.

```kotlin
val items: Flow<PagingData<ListItem>> = Pager(config, pagingSourceFactory)
    .flow
    .map { pagingData ->
        pagingData
            .map { dto -> ListItem.ContentItem(dto.toUi()) }
            .filter { it.item.status != ItemStatus.DELETED }
            .insertSeparators { before, after ->
                when {
                    before == null -> ListItem.DateHeader("Today")
                    after == null -> null
                    before.dateGroup != after.dateGroup -> ListItem.DateHeader(after.dateGroup)
                    else -> null
                }
            }
    }
    .cachedIn(viewModelScope)

sealed interface ListItem {
    data class ContentItem(val item: ItemUi) : ListItem
    data class DateHeader(val label: String) : ListItem
}
```

When you use `insertSeparators`, give every variant a unique key
(`"item_${id}"`, `"header_${label}"`) and a distinct `contentType` so the lazy
layout reuses the right view holder.

## Related references

- Offline-first paging with Room and `RemoteMediator` → `paging-offline.md`
- MVI dual-flow pattern, testing, and anti-patterns → `paging-mvi-testing.md`
- Lazy layout fundamentals (keys, content types, `LazyListState`) → `lists-scrolling.md`
