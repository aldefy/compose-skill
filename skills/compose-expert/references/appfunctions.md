# AppFunctions — exposing app capabilities to agents

> AppFunctions shipped as **beta** at Android Dev Summit (Oct 2026); the docs
> still flag it experimental and the end-to-end Gemini integration is gated
> behind an Early Access Program. Pin exact versions and expect API movement.
> Requires Android 16 (API 36)+ devices.

AppFunctions is an Android platform API plus a Jetpack library
(`androidx.appfunctions`) that lets your app behave like an on-device MCP
server: you declare functions, the OS indexes them, and authorized agents
(Gemini, system intelligence, other apps) discover and execute them as tools.

Use it for **actions and data the agent should reach without your UI** — create
task, search email, add playlist. Do not use it to render agent replies (that
is A2UI — see `agentic-ui-a2ui.md`) or for anything needing pixel-level UI
control.

## Core pieces

1. **Service** — subclass `AppFunctionService`, register with
   `@AppFunctionServiceEntryPoint(serviceName, appFunctionXmlFileName)`.
2. **Declarations** — `@AppFunctionDeclaration(isDescribedByKDoc = true)` on
   `suspend` functions. The annotation processor generates the XML schema the
   OS indexes.
3. **Serializable shapes** — `@AppFunctionSerializable` on parameter and
   return types. Primitive-rich, flat structures serialize best.

```kotlin
@RequiresApi(36)
@AppFunctionServiceEntryPoint(
    serviceName = "TaskAppFunctionService",
    appFunctionXmlFileName = "task_app_function_service",
)
class TaskAppFunctionService : AppFunctionService() {

    /**
     * Create a new task or reminder with a title, due time, and location.
     *
     * @param title The descriptive title of the task (e.g., "Pick up my package").
     * @param dueDateTime When the task should be completed.
     * @return The created Task.
     */
    @AppFunctionDeclaration(isDescribedByKDoc = true)
    suspend fun createTask(
        title: String,
        dueDateTime: LocalDateTime? = null,
    ): Task = withContext(Dispatchers.IO) {
        if (title.isBlank()) {
            throw AppFunctionInvalidArgumentException("Title must be non-blank")
        }
        repository.createTask(title, dueDateTime)
    }
}

@AppFunctionSerializable(isDescribedByKDoc = true)
data class Task(
    /** The ID of the task. */
    val id: String,
    /** The title of the task. */
    val title: String,
)
```

## KDoc is the agent contract

With `isDescribedByKDoc = true`, your KDoc becomes the schema description the
agent reads to decide *when* and *how* to call the function. Write it for the
model, not for a human skimming source:

- First sentence: the user-visible intent ("Create a new task or reminder…"),
  not the mechanism.
- Every `@param`: what it means plus an example value.
- `@return`: what the caller gets back.
- Keep privileged actions out of declarations; expose the narrowest useful set.

## Fail loudly with predefined exceptions

Agents recover from typed errors, not stack traces. Throw the library's
predefined exceptions so the agent learns *why* a call failed:

- `AppFunctionInvalidArgumentException` — bad or missing parameters.
- `AppFunctionElementNotFoundException` — referenced entity does not exist.

A generic `Exception` gives the agent nothing to correct against.

## Caller side (brief)

Callers need the `EXECUTE_APP_FUNCTIONS` permission. They obtain an
`AppFunctionManager`, verify support (absence of the manager means the device
lacks the feature), and check `isAppFunctionEnabled(packageName, functionId)`
before invoking. Your app does not need to feature-check — the Jetpack library
handles that.

## Compose integration: agent acts, UI observes

An AppFunction executes in your service, off the composition. The UI should
learn about mutations the same way it learns about any data change — through
observable state:

```text
agent ──executes──▶ AppFunction (service, Dispatchers.IO)
                         │ mutates repository / StateStore
                         ▼
              Compose UI recomposes from State/Flow
```

- Never touch `MutableState` owned by a composition directly from the service
  thread — go through the repository or a `StateStore` (see `appstate.md`).
- If a function's result should navigate or open a screen, emit state and let
  the navigation layer react; do not start activities from the service unless
  the platform contract requires it.

## AppFunctions vs A2UI vs MCP

| Concern | AppFunctions | A2UI | Remote MCP |
|---|---|---|---|
| Direction | Agent → app actions/data | Agent → UI surface | Agent → server tools |
| Execution | On-device, OS-indexed | Rendered in your Compose tree | Cloud, network round-trip |
| Declared via | Annotations + KDoc | Component catalog JSON | MCP server schema |
| Trust model | Permission-gated callers | Untrusted streamed JSON | Server auth |

They compose: an agent can call your AppFunction for data, then answer with an
A2UI surface built from your catalog.

## Testing and debugging

- `adb shell cmd app_function list-app-functions` — verify registration on-device.
- `adb shell cmd app_function ...` subcommands — inspect metadata, execute
  functions directly.
- Unit-test function bodies as plain suspend functions; the service is a thin
  shell.
- Test KDoc as a contract: if a first-read model could misroute the call,
  rewrite the doc.
- The official `device-ai/appfunctions` skill in `android/skills` scaffolds
  declarations, refines KDoc, and provides the ADB commands.

## Sources

- Overview: https://developer.android.com/ai/appfunctions
- Platform API: https://developer.android.com/reference/android/app/appfunctions/package-summary
- Jetpack releases: https://developer.android.com/jetpack/androidx/releases/appfunctions
- Sample: https://github.com/android/appfunctions
- Agent skill: https://github.com/android/skills/tree/main/device-ai/appfunctions
