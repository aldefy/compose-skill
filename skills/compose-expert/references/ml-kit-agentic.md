# ML Kit Agentic Workflows

> ML Kit Agentic API is alpha. It uses Gemini Nano through Android AICore;
> APIs, model availability, and device support can change. Keep network and
> consequential side effects under app control.

ML Kit's Android Agentic API orchestrates focused, multi-step, on-device
workflows. `AgentRunner` manages the loop over `GenerativeModel`: it observes
context, chooses typed tools, receives results, and continues until completion
or a turn limit. Use it for local commands, lookup, filtering, curation, and
validated data entry — not for an unconstrained general-purpose cloud agent.

## Dependency and runtime

```kotlin
dependencies {
    implementation("com.google.mlkit:genai-agent:<latest-alpha>")
}
```

The runtime uses Gemini Nano through Android's AICore service. Availability is
device- and rollout-dependent; treat model readiness as a runtime capability,
not a build-time guarantee. Keep a deterministic non-agent fallback for devices
without the required model or service.

## Choose the orchestration level

| Need | API |
|---|---|
| Automatic tool dispatch, managed history, multi-step loop | `AgentRunner` / `AgentSession` |
| Custom prompts, typed generation, app-managed history/tools | `GenerativeModel` |
| Stateless writing, vision, or rewriting | Task-specific ML Kit GenAI APIs |

`AgentSession` keeps in-memory conversation state across turns. Bound execution
with `maxTurns` (default 10) to limit runaway loops, battery use, and latency.
Release sessions with `session.close()`, `deleteSession(sessionId)`, or
`clearAllSessions()` when the owning workflow ends.

## Tools and AppFunctions

The agent can discover registered Android AppFunctions and select them as typed
tools. Keep tools narrow:

- one clear responsibility;
- explicit parameter and result types;
- short, concrete descriptions;
- validation before every mutation;
- no hidden network or payment side effects.

```text
user intent
    ▼
AgentSession / AgentRunner
    ├── Gemini Nano reasoning
    ├── typed AppFunction call
    ├── validated result
    └── next step or final response
```

See `appfunctions.md` for declarations, KDoc contracts, permission boundaries,
and typed failure exceptions. AppFunctions may still call network services, so
"on-device agent" does not mean every side effect is local or offline.

## Compose integration

The official overview does not publish imports or constructor signatures; follow
the ML Kit Get started guide for setup and treat the sketch below as structure,
not compilable code (`AssistantUiState`, `Idle`, `Running`, `Completed`, `Failed`,
and `runAgent` are app-defined).

Keep the agent session outside composition — typically in a ViewModel or a
state holder. Expose immutable progress, tool status, errors, and final data to
Compose through `StateFlow` or AppState `StateStore`; render loading, waiting for
confirmation, success, and failure explicitly.

```kotlin
class AssistantViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<AssistantUiState>(Idle)
    val uiState: StateFlow<AssistantUiState> = _uiState.asStateFlow()

    suspend fun run(request: String) {
        _uiState.value = Running
        try {
            // Create/use AgentSession outside composition; collect events here.
            _uiState.value = Completed(runAgent(request))
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (error: Exception) {
            _uiState.value = Failed(error)
        }
    }
}
```

Do not start an agent loop directly in a composable body. If composition owns
the lifetime, use `LaunchedEffect` with stable keys and close the session in the
corresponding lifecycle owner. Never let a recomposition accidentally create a
second session.

## Safety and product boundaries

- Require explicit confirmation before deletion, purchase, sharing,
authentication, messages, or other consequential actions.
- Show which tool/action is running when the workflow can surprise the user.
- Cap turns, input size, output size, tool latency, and total execution time.
- Keep prompts and local context on-device where possible; audit tools that
  access network data.
- Treat model output and tool arguments as untrusted input. Validate IDs,
  permissions, URLs, and amounts in app code.
- Cancel on screen/account scope loss and release sessions on logout.
- Design an offline/non-agent fallback for unsupported devices and model errors.

## Testing

- Unit-test tool implementations independently from model behavior.
- Test unavailable AICore/model, denied permission, malformed arguments,
  cancellation, max-turn termination, timeout, and typed tool failures.
- Run repeated workflows to detect nondeterministic state or duplicate side
  effects; make mutations idempotent where possible.
- Verify session cleanup and process-death recovery.
- Inspect AppFunction registration (see `appfunctions.md`) before testing agent
  selection; a tool that is not registered cannot be chosen.
- Test on physical devices with AICore and Gemini Nano available; emulators may
  not provide the model.

## Sources

- ML Kit Android agentic workflows: https://developers.google.com/ml-kit/genai/agent/android
- ML Kit GenAI overview: https://developers.google.com/ml-kit/genai
- AppFunctions: https://developer.android.com/ai/appfunctions
- Android AICore: https://developer.android.com/ai/aicore
- Android Dev Summit agentic announcement: https://developer.android.com/blog/posts/build-it-your-way-a-next-era-of-android-development
