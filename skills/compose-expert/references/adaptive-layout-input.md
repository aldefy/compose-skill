# Adaptive Layouts and Non-Touch Input

Build for window capabilities, not device labels. Phones can be resized;
tablets can be compact; desktop windows can be narrow; foldables can expose a
hinge or tabletop posture.

## Googlebook and desktop-class Android

Googlebook is an Android desktop-class form factor, not a separate UI codebase.
Treat its resizable window, keyboard, trackpad, mouse, and external-display
capabilities as first-class inputs. Do not branch on a model name or assume a
phone-sized window.

- Support arbitrary window sizes, split-screen, multi-window, and multi-display.
- Preserve navigation, editing, scroll, and selection state across resize and
  configuration changes with `rememberSaveable`, `rememberSerializable`, or a
  state holder; do not hide resize bugs with `android:configChanges`.
- Use `Grid`, `FlexBox`, adaptive navigation scenes, and `MediaQuery` for
  responsive layout decisions.
- Add keyboard shortcuts, predictable focus traversal, Enter/Space activation,
  hover affordances, tooltips, pointer icons, and drag-and-drop where the task
  benefits from desktop input.
- Keep touch targets usable; desktop support adds input paths, it does not
  remove accessibility or touch requirements.

Aim for at least **Tier 2 (Adaptive optimized)** quality. Tier 1 (Adaptive
differentiated) applies when the experience intentionally uses desktop
multitasking, drag-and-drop, stylus, or other large-screen capabilities.

### Googlebook test matrix

Validate critical flows on a Googlebook-sized configuration, a resizable
window, split-screen, and an external display. Also test keyboard, mouse,
trackpad, hover, shortcuts, focus order, drag-and-drop where supported, and
state restoration after resize. Android's adaptive compatibility matrix includes
Googlebook, foldable, 8-inch tablet, 10.5-inch tablet, and 13-inch Chromebook
configurations; use the Desktop (Preview) emulator or resizable emulator when
available.

## Choose the layout primitive

| Need | Primitive |
|---|---|
| Simple fixed row/column | `Row` / `Column` |
| Small set that wraps and redistributes space | `FlexBox` |
| Explicit two-dimensional tracks and item placement | `Grid` |
| Large or unbounded scrolling collection | Lazy list/grid |
| App-level list/detail or supporting pane | Material 3 Adaptive + Navigation 3 scenes |

`Grid` and `FlexBox` are stable in Compose Foundation 1.13. Projects on stable
1.12 must not copy 1.13 examples without upgrading to an appropriate prerelease.

```kotlin
FlexBox(
    modifier = Modifier.fillMaxWidth(),
    config = {
        flexDirection(FlexDirection.Row)
        flexWrap(FlexWrap.Wrap)
    },
) {
    tags.forEach { tag -> FilterChip(selected = false, onClick = {}, label = { Text(tag) }) }
}
```

Check the exact 1.13 API signature; it changed during alpha development.

## Media queries

The experimental `MediaQuery` API converts capabilities such as width,
orientation, and folding posture into Compose-observable decisions. Prefer it
over manually coordinating several platform managers when its supported query
set fits the problem.

Keep capability decisions near the layout they affect. Do not branch on model
names, `isTablet`, or a one-time startup width.

## Navigation 3 scenes

Use Navigation 3 scene strategies for app-level single-pane versus multi-pane
presentation. A scene strategy can select presentation from window capability
while the back stack remains application-owned state.

Keep an adaptive scaffold inside a destination when it represents one feature's
internal list/detail flow. Use scenes when multiple navigation entries are
presented together at the app level.

## Input is not synonymous with touch

Every interactive component should work with:

- touch and stylus;
- mouse and trackpad;
- hardware keyboard;
- D-pad/rotary where the form factor requires it;
- indirect directional input on projected or eyewear devices;
- accessibility services.

Prefer semantic component APIs (`clickable`, buttons, scrollable containers)
over raw `pointerInput` so new pointer types inherit framework behavior.

## Trackpad behavior

Compose maps modern trackpad gestures to dedicated mouse/pan/scale pointer
events instead of treating every gesture as fake fingers. Do not infer a
trackpad from touch count or platform-generated finger coordinates.

Use low-level pointer APIs only when a component genuinely needs custom gesture
arbitration. Respect event passes and consumption; nested components depend on
them.

## Testing

Test focus order, Enter/Space activation, shortcuts, hover, scroll, pan, scale,
and resize behavior. Newer Compose UI test APIs include trackpad input helpers
such as `performTrackpadInput`; version-gate them in shared test utilities.

For adaptive tests, vary constraints and posture inputs rather than asserting a
specific device name.

## Sources

- Layout containers: https://developer.android.com/develop/ui/compose/layouts/containers
- Adaptive apps: https://developer.android.com/develop/ui/compose/layouts/adaptive
- Dev Summit adaptive session: https://developer.android.com/events/dev-summit/talks/scale-your-app-for-every-screen-with-compose
- Dev Summit input session: https://developer.android.com/events/dev-summit/talks/scaling-input-interactions-beyond-the-touchscreen-with-jetpack-compose
