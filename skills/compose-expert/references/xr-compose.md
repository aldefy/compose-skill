# Compose for Android XR and Projected Displays

Android XR spans headsets, wired optical displays, and intelligent eyewear.
Choose APIs by device capability rather than treating XR as one UI target.

## Release maturity (AndroidX XR, checked 2026-11-06)

| Library | Channel | Version observed |
|---|---|---|
| `androidx.xr.runtime`, `androidx.xr.scenecore`, `androidx.xr.arcore` | Stable | `1.0.0` |
| `androidx.xr.compose` | Beta | `1.0.0-beta02` |
| `androidx.xr.glimmer` | Alpha | `1.0.0-alpha22` |
| `androidx.xr.projected` | Alpha | `1.0.0-alpha14` |

Core runtime, SceneCore, and ARCore are stable; the Compose spatial layer is
beta, and Glimmer and projected activities are alpha. Pin versions per library,
gate alpha/beta APIs behind a feature flag or separate module, and re-check the
release page before documenting a version — alpha APIs break between releases.

## Tooling and devices (Android Developer Summit 2026)

- **Emulators:** Android XR emulators in Android Studio are stable. Use them to
  validate layouts for XR glasses, audio glasses, and display glasses without
  hardware.
- **Engine Hub:** the Android XR Engine Hub is stable for Unity, Godot, and
  Unreal. It scaffolds projects with pre-configured OpenXR extensions and
  validated settings, and adds profiling (system traces, thermal limits, frame
  budgets across CPU/GPU) inside the engine. Setup and profiling for those engines
  belong there, not in Compose. Availability by OS was Windows-only when first
  introduced; check the current docs before promising other platforms.
- **XREAL AURA:** the first wired XR glasses on Android XR (under 95 g, portable
  compute puck). Existing Android apps run on it out of the box, so start from the
  adaptive 2D baseline and add spatial APIs where they help.
- **Geospatial:** ARCore for Jetpack XR Geospatial APIs are stable, for anchoring
  content to real-world coordinates.

## Existing 2D Compose UI

Start with an adaptive, resizable 2D activity. Existing Android UI can run in a
spatial panel with minimal changes, but it still needs keyboard, trackpad,
controller, and accessibility support.

Use normal Compose for application chrome and business UI. Introduce spatial
APIs only where depth, anchoring, or 3D content adds value.

## Compose Glimmer

Jetpack Compose Glimmer provides components for see-through projected displays.
Black may be transparent and real-world lighting is uncontrolled, so ordinary
phone colors and elevation assumptions do not transfer directly.

- Use Glimmer color helpers and verify contrast across bright/dark backgrounds.
- Use depth deliberately to separate overlapping content.
- Keep interaction targets simple and readable at a glance.
- Prefer pagers/button groups designed for the projected interaction model.

Glimmer is not Material 3 with a different theme; route Glimmer-specific work
to this reference.

## Projected activities and device context

Projected activities let a phone-hosted app provide content or audio to
intelligent eyewear. CameraX and other device-aware libraries may require a
projected device context to select peripherals on the glasses rather than the
phone.

Handle capability absence: not every display has a camera, screen, touch input,
or the same on-device model support.

## Spatial Compose and engines

Subspace composables place panels and entities in 3D space. Anchors can follow
tracked objects or geospatial positions. Keep continuously ticking 3D engines
decoupled from Compose state—forwarding every engine frame into snapshot state
causes continuous recomposition.

When embedding Unity or Godot:

- isolate engine lifecycle and failure from the host UI;
- communicate through a narrow state/event interface;
- use another process when crash isolation justifies the IPC cost;
- do not duplicate rendering loops in Compose.

SceneCore mesh APIs support custom and dynamic geometry. Update only changed
vertex ranges instead of recreating the entire mesh/entity.

## Accessibility

Design accessibility at the interaction-model stage:

- offer seated/reduced-motion and reach alternatives;
- provide snap turning or equivalent comfort controls;
- expose high-contrast outlines and scalable content;
- pair spatial audio with visual/directional captions;
- avoid interactions that require precise head or full-body movement;
- test with users with motor, visual, auditory, and cognitive disabilities.

## Sources

- Android XR: https://developer.android.com/develop/xr
- Dev Summit XR tools announcement: https://developer.android.com/blog/posts/build-android-xr-devices-tools
- AndroidX XR release notes: https://developer.android.com/jetpack/androidx/releases/xr-scenecore
- Glimmer: https://developer.android.com/develop/xr/jetpack-xr-sdk/compose-glimmer
- Dev Summit Glimmer session: https://developer.android.com/events/dev-summit/talks/build-world-anchored-experiences-for-xreal-aura-wired-xr-glasses
- Embedded engines: https://developer.android.com/events/dev-summit/talks/elevate-immersive-experiences-with-3d-engines-in-jetpack-compose-for-xr
- XR accessibility: https://developer.android.com/events/dev-summit/talks/xr-is-for-everyone-designing-accessible-spatial-experiences
