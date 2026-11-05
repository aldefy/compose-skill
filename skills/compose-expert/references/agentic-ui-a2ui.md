# Agentic UI with A2UI

> Status reviewed 2026-11-05. The AndroidX A2UI artifacts are alpha APIs. Pin an
> exact version, read its release notes, and expect source changes during upgrades.

## When to use A2UI

A2UI is an open, declarative JSON protocol for an agent to describe UI. The
AndroidX renderer maps that description to trusted native Compose components.
It does **not** download or execute generated Kotlin code.

Use it when an agent must return an interactive surface whose structure is not
known at build time. Do not use it for ordinary server-driven flags, fixed
forms, or screens that are simpler and safer to model as normal app state.

```kotlin
dependencies {
    implementation("androidx.compose.material3:material3-a2ui:1.0.0-alpha02")
}
```

Always confirm the latest alpha and migration notes before copying this version.

## Architecture

An integration has three main pieces:

1. **Catalog** — the only components and client functions the agent may use.
2. **Message processor** — parses streaming protocol messages, validates them
   against the catalog, and exposes active surface models.
3. **Surface** — a model rendered by `A2uiSurface` inside the app's Compose tree.

The provided Material 3 Basic Catalog covers common text, input, layout, card,
and list components. The app supplies its own image, video, and audio renderers
so the library does not impose Coil, Glide, or Media3.

```kotlin
@Composable
fun AgentSurface(surface: A2uiSurfaceModel) {
    A2uiSurface(surfaceModel = surface)
}
```

Treat this as an architectural sketch. Alpha releases may rename factories and
interfaces; use the current API reference for exact construction code.

## Catalog design

Prefer a narrow catalog of domain-level components over giving the agent a bag
of low-level primitives.

```text
Safer:  ProductCard, ShippingChoice, ConfirmOrder
Broader: Text, Row, Column, Button, arbitrary URL opener
```

- Keep privileged actions out of the catalog.
- Validate identifiers and URLs again in application code.
- Separate read-only functions from actions that mutate data.
- Require user confirmation for purchases, deletion, sharing, authentication,
  and other consequential operations.
- Use the app's own design tokens and accessibility defaults in custom catalog
  components.

The catalog is a capability boundary, not merely a component registry.

## State and events

A2UI supports streamed structural updates, fine-grained data binding, and
outbound user events. Local bound-data changes should update the surface without
an agent round trip. Actions that need agent reasoning flow outward as events.

Keep transport and rendering separate:

```text
agent stream -> JSON extraction -> parser/processor -> surface StateFlow
user action  <- outbound event collection          <- rendered surface
```

Run message collection in a lifecycle-owned coroutine. Clear surface state when
the containing conversation/session is cleared.

## Failure handling

- Reject messages that do not validate against the negotiated catalog.
- Render explicit loading and error states; streamed trees are temporarily
  incomplete by design.
- Bound surface size, nesting depth, list lengths, media size, and update rate.
- Log schema failures without recording prompts, personal data, or model output
  containing secrets.
- Never assume that protocol validation makes a destructive client function safe.

## Testing

Test at three levels:

1. Parser/processor tests for valid, partial, malformed, and out-of-order messages.
2. Catalog component tests using A2UI testing stubs and Compose semantics.
3. End-to-end tests that assert confirmation and authorization boundaries.

Include accessibility assertions for generated forms and test progressive
updates with repeated runs. Do not rely only on screenshot tests: event routing,
focus, labels, and error recovery are behavioral contracts.

## A2UI versus Remote Compose

| Concern | A2UI | Remote Compose |
|---|---|---|
| Producer | Agent/backend using an open JSON protocol | Trusted app/tooling producing a binary document |
| Primary use | Generative, agent-controlled surfaces | Cross-process/device remote surfaces and widgets |
| Components | Catalog constrained by the app | Remote Compose capability/profile constrained |
| Trust model | Treat input as untrusted | Treat producer as trusted, still validate document limits |

Do not describe the two systems as interchangeable.

## Sources

- Android A2UI overview: https://developer.android.com/develop/ui/compose/agentic
- Catalogs: https://developer.android.com/develop/ui/compose/agentic/manage-catalogs
- Rendering surfaces: https://developer.android.com/develop/ui/compose/agentic/render-surfaces
- A2UI specification: https://a2ui.org
