# Compose for Android XR and Projected Displays

Android XR spans headsets, wired optical displays, and intelligent eyewear.
Choose APIs by device capability rather than treating XR as one UI target.

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
- Glimmer: https://developer.android.com/develop/xr/jetpack-xr-sdk/compose-glimmer
- Dev Summit Glimmer session: https://developer.android.com/events/dev-summit/talks/build-world-anchored-experiences-for-xreal-aura-wired-xr-glasses
- Embedded engines: https://developer.android.com/events/dev-summit/talks/elevate-immersive-experiences-with-3d-engines-in-jetpack-compose-for-xr
- XR accessibility: https://developer.android.com/events/dev-summit/talks/xr-is-for-everyone-designing-accessible-spatial-experiences
