# Remote Compose

> Status reviewed 2026-11-05. Remote Compose is alpha and changes frequently.
> Pin one release across all `androidx.compose.remote` artifacts and consult its
> migration notes before using an example.

Remote Compose serializes a UI into a compact binary document that a separate
player renders. The player can handle layout, touch, animation, and expressions
without round trips to the producer for every frame or event.

Typical uses include launcher widgets, Wear widgets, and UI delivered across a
process or device boundary.

## Mental model

```text
trusted producer -> remote document -> transport/storage -> player
                   variables/actions                    -> host callbacks
```

The producer writes `@RemoteComposable` content or uses lower-level document
APIs. This is a constrained remote UI dialect, not normal Compose serialized.
Standard CompositionLocals and arbitrary Kotlin behavior do not automatically
exist in the player.

## Artifact families

- `remote-core` — document primitives.
- `remote-creation*` — create documents, including Compose creation APIs.
- `remote-player*` — render documents.
- `remote-tooling-preview` — preview support.
- `remote-creation-expression` — evolving platform-agnostic expression support.

As of the review date, the train is `1.0.0-alpha23`. Do not encode “latest” in
long-lived advice; link to the release page and pin the project version.

## Design rules

- Query the active creation profile before using optional operations.
- Keep documents small through templates and reusable component structures.
- Use remote state/expression types for values evaluated by the player.
- Treat host callbacks and pending intents as privileged boundaries.
- Define graceful fallback when a player lacks clipping, themed colors, touch
  modifiers, fonts, or other capabilities.
- Avoid assuming standard Compose `Dp`, `Color`, `Shape`, or state types are
  interchangeable with their Remote Compose counterparts.

## Interaction and state

Prefer player-local expressions for visual changes that must remain responsive.
Use host actions for operations that require application data or privileges.
Do not send a new document for every animation frame or pointer movement.

Validate action identifiers and dynamic parameters in the host. A compact
binary document is not an authorization mechanism.

## Glance and Wear

Jetpack Glance can emit Remote Compose documents for launcher and Wear widgets,
decoupling rendering from the application process. Wear Widgets are the
successor path for full-screen Tiles; migration may require dual services while
older Wear versions remain supported.

Keep Glance guidance separate from ordinary Compose UI: similar declarative
syntax does not mean identical components, state, lifecycle, or modifiers.

## A2UI versus Remote Compose

A2UI consumes untrusted agent-authored JSON constrained by an app catalog.
Remote Compose normally consumes a binary document produced by trusted app or
tooling code and constrained by a player profile. Use `agentic-ui-a2ui.md` for
generative agent surfaces.

## Testing

- Round-trip document creation and playback.
- Test minimum and maximum host sizes.
- Run against capability profiles with optional features disabled.
- Verify single, double, long, down/up/cancel, scroll, and resize interactions.
- Assert host action authorization separately from rendering behavior.

## Sources

- Releases and artifacts: https://developer.android.com/jetpack/androidx/releases/compose-remote
- Dev Summit overview: https://developer.android.com/events/dev-summit/talks/powering-interactive-surfaces-with-remote-compose
- Wear migration session: https://developer.android.com/events/dev-summit/talks/evolving-tiles-to-wear-widgets-using-jetpack-glance-and-remote-compose
