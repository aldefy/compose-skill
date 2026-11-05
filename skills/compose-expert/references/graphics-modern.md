# Modern Compose Graphics

## Version gates

The Dev Summit graphics APIs span stable Compose 1.12, Compose 1.13 prerelease,
and newer Android platform APIs. State the required Compose and Android versions
next to every example. Provide a fallback or omit an effect when unavailable.

## Mesh gradients

Compose 1.12 adds `MeshGradientPainter` for multicolor interpolation across a
two-dimensional vertex grid. Use it with `Modifier.paint` or drawing APIs for
art-directed backgrounds that cannot be expressed as a linear/radial gradient.

Keep animated mesh inputs small, remember data that does not change, and avoid
allocating vertex/color collections every frame.

On Android 14+, platform mesh drawing can render custom geometry directly.
Decode and prepare large inputs off the main thread.

## Wide color gamut

Wide-gamut `Color` values only provide a benefit when the window and display
support the color space. Enable wide color gamut for media or graphics that need
it, not as an unconditional application flag. Test on both standard-sRGB and
wide-gamut devices.

## Polygon shapes and morphing

Compose 1.13 introduces `PolygonShape` and `MorphPolygonShape`. Morph progress
is read while resolving the outline, allowing shape animation without forcing
composition for every frame.

Prefer the framework shapes over rebuilding custom `Path` objects in
composition. Ensure start/end polygons are compatible and cache immutable
geometry.

## Blur and backdrop effects

Distinguish:

- blurring content owned by the composable;
- progressive blur whose radius varies spatially;
- backdrop blur that samples content behind a render node or surface.

Backdrop APIs require new platform versions and have different behavior around
surfaces and secure content. Never make text contrast depend solely on a blur;
include a tint/scrim and verify accessibility with the fallback path.

## Performance

- Put frame-varying draw properties in `drawWithCache`, draw-phase lambdas, or
  a `graphicsLayer` as appropriate.
- Do not read rapidly changing graphics state in composition unless structure
  changes.
- Decode images to the displayed dimensions and standardize image-loader cache
  budgets.
- Benchmark actual frame timing with Macrobenchmark/Perfetto; a visually complex
  effect that looks smooth on one device is not evidence of acceptable cost.
- Test thermal and memory behavior for continuously animated or image-heavy UI.

## Sources

- Graphics in Compose: https://developer.android.com/develop/ui/compose/graphics
- Dev Summit graphics session: https://developer.android.com/events/dev-summit/talks/elevate-your-apps-with-the-latest-graphics-features-in-jetpack-compose-and-android
