# Jetpack Ink in Compose

> Jetpack Ink (`androidx.ink`) is Android-first. `1.0.0` is stable (2025-12-17);
> the `1.1.0-alpha` line (alpha11 on 2026-11-04) adds experimental APIs. Pin one
> version for all `ink-*` artifacts and gate alpha-only APIs explicitly.

Ink is a modular library for creating, rendering, storing, and editing
pen/stylus strokes. Use it instead of hand-rolling a `Canvas` + `Path` drawing
surface when you need low-latency wet ink, pressure/tilt-aware brushes,
serialization, or stroke-aware erasing and selection.

## Modules

| Module | Responsibility |
|---|---|
| `ink-authoring` / `ink-authoring-compose` | Real-time stroke input, `InProgressStrokesView`, low-latency rendering while the pen is down |
| `ink-brush` / `ink-brush-compose` | `Brush`, `BrushFamily`, `StockBrushes`, custom brush behavior |
| `ink-strokes` | Finished `Stroke` data, `StrokeInputBatch` |
| `ink-rendering` | `CanvasStrokeRenderer`, `ViewStrokeRenderer` for finished strokes |
| `ink-geometry` / `ink-geometry-compose` | Intersection, coverage, `PartitionedMesh` for hit-testing, selection, erasing |
| `ink-storage` | Serialization of strokes and brushes |
| `ink-nativeloader` | Loads Ink's native (JNI) code |

Depend only on the modules you use, all at the same version:

```kotlin
dependencies {
    implementation("androidx.ink:ink-authoring-compose:<version>")
    implementation("androidx.ink:ink-brush-compose:<version>")
    implementation("androidx.ink:ink-rendering:<version>")
    implementation("androidx.ink:ink-strokes:<version>")
    implementation("androidx.ink:ink-storage:<version>")
}
```

Check the release page for the current version before pinning.

## Architecture in a Compose app

```text
pen/stylus MotionEvents
      ▼
InProgressStrokes (authoring)  ── low-latency "wet" ink
      │ stroke finished
      ▼
immutable finished Stroke  ──▶  state holder (document model)
      ▼
CanvasStrokeRenderer / ViewStrokeRenderer  ── "dry" ink drawn in your UI
```

- Keep the document (list of finished strokes, selection, undo stack) in a
  ViewModel or state holder as immutable data. Compose renders from that state;
  the in-progress stroke surface is not driven by Compose state per frame.
- Do not forward every `MotionEvent` into snapshot state. The authoring module
  exists so wet ink bypasses the composition path for latency.
- Hand off a finished stroke to the document model once, then draw it with a
  renderer. Wet ink and dry ink must use the same brush so there is no visible
  color or width change on hand-off.
- Reuse renderer objects; do not recreate them per frame or per recomposition.

## Brushes

- Start with `StockBrushes` (marker, pressure pen, highlighter, emoji
  highlighter). Pass the stock brush version explicitly so a library upgrade
  cannot silently change how saved documents look.
- Custom `BrushFamily` APIs are public from `1.1.0-alpha03`. Serialize a
  `BrushFamily` with the module's encode/decode functions; when loading
  documents from other devices, use the decode overload that specifies maximum
  version compatibility and handle documents that need a newer Ink.
- Highlighter brushes have a self-overlap setting; choose it deliberately.
- Brush color shift operates in Oklab as of `1.1.0-alpha09` (`CHROMA` and
  `LIGHTNESS` targets replaced `SATURATION` and `LUMINOSITY`).

## Erasing, selection, geometry

- Whole-stroke erase and lasso selection use `ink-geometry` queries against a
  stroke's `PartitionedMesh`.
- The partial-stroke ("mesh editing"/"pixel") eraser is experimental (`1.1.0`
  alphas). `Stroke.subtract` and `Stroke.split` are annotated `@WorkerThread`:
  run them off the main thread and post the resulting strokes back to state.
- `1.1.0-alpha11` adds `PartitionedMesh` serialization so partially erased
  strokes can be saved and documents load faster.

## Persistence

Serialize stroke inputs (`StrokeInputBatch`) and brushes rather than rasterized
bitmaps: the stored form is a small fraction of the size and re-renders at any
zoom. Store the Ink version alongside the document and test round-trips,
including a document saved by an older build.

## Platform notes

- Android is the primary target. Ink also runs on server-side JVM (Linux x86_64
  only). On JDK 24+ the JNI loader emits a native-access warning unless
  `--enable-native-access=ALL-UNNAMED` is set.
- Cross-platform rendering (for example `MetalRenderer` on iOS) is behind
  `ExperimentalInkCrossPlatformRenderingApi` in the alpha line. Do not describe
  Ink as a stable Compose Multiplatform drawing library.

## Testing

- Test with a real stylus and a finger; palm rejection and hover differ.
- Record and replay `MotionEvent` sequences, including very fast strokes,
  stylus lift/re-touch, and concurrent inputs.
- Test configuration change and detach/reattach while a stroke is in progress.
- Measure end-to-end ink latency and frame time on low-end devices.
- Provide non-pen alternatives (touch drawing, keyboard/shape insertion) and
  accessible descriptions for the canvas content.

## Sources

- Ink release notes and dependencies: https://developer.android.com/jetpack/androidx/releases/ink
- Jetpack libraries overview: https://developer.android.com/jetpack
