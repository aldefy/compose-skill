# Paging 3 — Offline-First with RemoteMediator

Local DB as the single source of truth, network as a refresh trigger. Builds on
the core setup in `paging.md`. Room itself sits outside this skill's scope —
this file documents only the parts where `RemoteMediator` shapes Compose UI
behaviour (LoadState semantics, refresh policies, what the UI sees).

## Compose Multiplatform note

Room is Android-only. In CMP `commonMain`, the equivalent stack is **SQLDelight**
(`app.cash.sqldelight`), which provides a `PagingSource` factory via
`app.cash.sqldelight:androidx-paging3-extensions`. The mental model below is
identical — local DB as source of truth, `RemoteMediator` writes to it, the UI
observes via the DB-backed `PagingSource`. Only the DAO/insert/transaction calls
change shape. The `LoadState` rules (use `loadState.source.refresh` over
`loadState.refresh`) apply identically because they're a property of the
Paging 3 contract, not of Room.

Where the snippets below say `db.itemDao()` / `db.withTransaction { ... }`, the
SQLDelight equivalent is `database.itemQueries.insertAll(...)` /
`database.transaction { ... }`.

## When RemoteMediator runs

`RemoteMediator.initialize()` controls whether a network refresh fires on first
load. This decides whether the user sees stale-but-instant data or a loading
state.

```kotlin
@OptIn(ExperimentalPagingApi::class)
override suspend fun initialize(): InitializeAction {
    val cacheTimeout = TimeUnit.HOURS.toMillis(1)
    val lastUpdated = db.remoteKeyDao().getLastUpdated("items") ?: 0L

    return if (System.currentTimeMillis() - lastUpdated < cacheTimeout) {
        InitializeAction.SKIP_INITIAL_REFRESH
    } else {
        InitializeAction.LAUNCH_INITIAL_REFRESH
    }
}
```

| Return value | UI effect |
|---|---|
| `LAUNCH_INITIAL_REFRESH` (default) | Triggers a `REFRESH` load before showing data — user sees a loading indicator first |
| `SKIP_INITIAL_REFRESH` | Shows cached rows immediately; network only fires on user-triggered refresh or `append` |

Pick `SKIP_INITIAL_REFRESH` when the cache is fresh enough that flashing a
spinner over existing data degrades perceived performance.

## RemoteMediator implementation

```kotlin
@OptIn(ExperimentalPagingApi::class)
class ItemRemoteMediator(
    private val api: ItemApi,
    private val db: AppDatabase,
) : RemoteMediator<Int, ItemEntity>() {

    override suspend fun initialize(): InitializeAction {
        val lastUpdated = db.remoteKeyDao().getLastUpdated("items") ?: 0L
        val cacheTimeout = TimeUnit.HOURS.toMillis(1)
        return if (System.currentTimeMillis() - lastUpdated < cacheTimeout) {
            InitializeAction.SKIP_INITIAL_REFRESH
        } else {
            InitializeAction.LAUNCH_INITIAL_REFRESH
        }
    }

    override suspend fun load(
        loadType: LoadType,
        state: PagingState<Int, ItemEntity>,
    ): MediatorResult {
        val page = when (loadType) {
            LoadType.REFRESH -> 1
            LoadType.PREPEND -> return MediatorResult.Success(endOfPaginationReached = true)
            LoadType.APPEND -> {
                val remoteKey = db.remoteKeyDao().getRemoteKey("items")
                remoteKey?.nextPage ?: return MediatorResult.Success(endOfPaginationReached = true)
            }
        }

        return try {
            val response = api.getItems(page = page, limit = state.config.pageSize)

            db.withTransaction {
                if (loadType == LoadType.REFRESH) {
                    db.itemDao().clearAll()
                    db.remoteKeyDao().delete("items")
                }
                db.itemDao().insertAll(response.items.map { it.toEntity() })
                db.remoteKeyDao().insert(
                    RemoteKey(
                        id = "items",
                        nextPage = if (response.items.isEmpty()) null else page + 1,
                        lastUpdated = System.currentTimeMillis(),
                    )
                )
            }

            MediatorResult.Success(endOfPaginationReached = response.items.isEmpty())
        } catch (e: IOException) {
            MediatorResult.Error(e)
        } catch (e: HttpException) {
            MediatorResult.Error(e)
        }
    }
}
```

<!-- source: not bundled — RemoteMediator lives in androidx.paging:paging-common -->

## Pager wiring

```kotlin
@OptIn(ExperimentalPagingApi::class)
val items: Flow<PagingData<ItemEntity>> = Pager(
    config = PagingConfig(pageSize = 20),
    remoteMediator = ItemRemoteMediator(api, db),
    pagingSourceFactory = { db.itemDao().pagingSource() },
).flow.cachedIn(viewModelScope)
```

The local `PagingSource` reads from the database. `RemoteMediator` writes to the
database. The UI observes the database-backed `PagingSource` — meaning UI updates
are driven by Room invalidation, not by the network response directly.

## LoadState with RemoteMediator (Compose-side gotcha)

Use `loadState.source.refresh` rather than the convenience `loadState.refresh`
in your Compose code:

```kotlin
val sourceRefresh = pagingItems.loadState.source.refresh
val mediatorRefresh = pagingItems.loadState.mediator?.refresh

when {
    sourceRefresh is LoadState.Loading -> FullScreenSpinner()
    mediatorRefresh is LoadState.Error -> InlineErrorBar(mediatorRefresh.error)
    pagingItems.itemCount == 0 -> EmptyState()
    else -> ItemList(pagingItems)
}
```

`loadState.refresh` collapses source + mediator into one signal. With Room as
source of truth that signal can flip to `NotLoading` while Room is still mid-
write, briefly hiding the spinner before the rows appear. Reading `source.refresh`
and `mediator.refresh` separately keeps the indicator honest.

<!-- source: references/source-code/foundation-source.md — search "LazyList" for how the rendered LazyColumn consumes the source-backed PagingData -->

## Remote keys (UI-relevant shape)

The remote-keys table is what makes pagination resumable across launches. The
table shape itself is a Room concern, but the UI behaviour depends on it being
present:

```kotlin
@Entity(tableName = "remote_keys")
data class RemoteKey(
    @PrimaryKey val id: String,
    val nextPage: Int?,
    val lastUpdated: Long = System.currentTimeMillis(),
)
```

Without a populated `nextPage`, `LoadType.APPEND` short-circuits to
`endOfPaginationReached = true` and the user sees no further pages even though
more exist on the server.

## Related

- Core Paging setup → `paging.md`
- MVI integration and tests → `paging-mvi-testing.md`
