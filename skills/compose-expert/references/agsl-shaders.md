# AGSL Shaders in Compose

> AGSL is Android-only. `RuntimeShader` was added in Android API 33 (Android 13).
> Treat shader effects as an optional rendering layer: gate by API level, keep a
> readable fallback, and measure GPU cost on target devices. Compose
> Multiplatform targets other than Android have no `RuntimeShader`.

Android Graphics Shading Language (AGSL) lets you write runtime shaders whose
`main(float2 coord)` returns a premultiplied-alpha color for each pixel. A
`RuntimeShader` is a `android.graphics.Shader` that contributes a function to
the GPU fragment shader Android assembles for a draw operation — it is not a
full GLSL fragment stage. Use it for frosted glass, dynamic lighting, ripples,
and custom color transforms — not for layout or effects a normal `Brush`,
`Canvas`, or Compose shape can express.

## Two integration points

| Goal | API |
|---|---|
| Paint a new fill (background/foreground) | `ShaderBrush(runtimeShader)` |
| Transform already-rendered content of a composable | `RenderEffect.createRuntimeShaderEffect(shader, "content")` in `graphicsLayer` |

In the second case the AGSL source declares `uniform shader content;` and
samples it with `content.eval(coord)`. Compose's `graphicsLayer { renderEffect }`
takes a Compose `RenderEffect`, so convert the platform effect with
`.asComposeRenderEffect()`.

## Fill with `ShaderBrush`

Keep AGSL source immutable, create the `RuntimeShader` once, and update uniforms
when inputs change.

```kotlin
private const val GradientShader = """
    uniform float2 resolution;
    uniform float time;

    half4 main(float2 coord) {
        float2 uv = coord / resolution;
        float wave = 0.5 + 0.5 * sin(uv.x * 6.2831 + time);
        return half4(uv.x, wave, uv.y, 1.0);
    }
"""

@RequiresApi(33)
@Composable
fun ShaderBackdrop(time: Float, modifier: Modifier = Modifier) {
    val shader = remember { RuntimeShader(GradientShader) }
    val brush = remember(shader) { ShaderBrush(shader) }

    Box(
        modifier.drawWithCache {
            shader.setFloatUniform("resolution", size.width, size.height)
            onDrawBehind {
                shader.setFloatUniform("time", time)
                drawRect(brush)
            }
        }
    )
}
```

`resolution` is set when the size changes (`drawWithCache` re-runs); `time` is
set in the draw block, so changing it re-draws without recomposing the tree
below `ShaderBackdrop`. Hoist `time` as a lambda or `State` read in the draw
phase if it changes every frame.

## Transform content with `RenderEffect`

```kotlin
private const val WaveShader = """
    uniform shader content;
    uniform float2 resolution;
    uniform float progress;

    half4 main(float2 coord) {
        float offset = sin(coord.y / resolution.y * 20.0 + progress) * 6.0;
        return content.eval(coord + float2(offset, 0.0));
    }
"""

@RequiresApi(33)
@Composable
fun WavyContent(progress: () -> Float, content: @Composable () -> Unit) {
    val shader = remember { RuntimeShader(WaveShader) }

    Box(
        Modifier.graphicsLayer {
            shader.setFloatUniform("resolution", size.width, size.height)
            shader.setFloatUniform("progress", progress())
            renderEffect = RenderEffect
                .createRuntimeShaderEffect(shader, "content")
                .asComposeRenderEffect()
        }
    ) { content() }
}
```

The layer block is a draw-phase scope: reading `progress()` there invalidates the
layer, not composition. It allocates a new `RenderEffect` each run, which is
acceptable for a single animated layer but measure it before applying the same
pattern to many items.

## Uniform and shader rules

- Declare every uniform you set. Setting an undeclared name or the wrong type
  throws `IllegalArgumentException` (for example `setFloatUniform(name, x, y)`
  requires a `float2`/`vec2` uniform).
- An uninitialized primitive uniform defaults to 0. An uninitialized color or
  shader uniform is undefined — always set them.
- Color uniforms need `layout(color) uniform half4 name;` and
  `setColorUniform` so the value is converted to the working color space.
- Return premultiplied alpha: `[R*A, G*A, B*A, A]`, not straight alpha.
- AGSL's origin is the upper-left of the canvas/render node, unlike GLSL's
  lower-left. `BitmapShader` samples in pixel coordinates, not normalized UV.
- `setInputShader` binds a `Shader` to a `uniform shader`; `setInputBuffer` skips
  color-space conversion for non-color data such as normal or height maps.

## `graphicsLayer` and performance

- A `RenderEffect` applies to the layer; it does not change layout measurement.
- Keep frame-varying uniforms in draw/layer scopes, not in composition.
- Limit layer bounds. Fullscreen effects cost fill rate and memory.
- Avoid stacking blur, shader, clip, and alpha layers without profiling.
- Do not construct a `RuntimeShader` inside a draw loop — compiling the program
  is the expensive part. Create it in `remember`.
- Check text and icon contrast after effects; add a scrim or drop the effect
  when the fallback is more readable.

## Fallback strategy

AGSL is an enhancement, not a content contract. Render the same content when
`Build.VERSION.SDK_INT < 33`, when construction throws, or when your frame
budget is exceeded. Interaction, semantics, accessibility labels, and essential
contrast must not depend on shader output.

```kotlin
@Composable
fun OptionalWave(enabled: Boolean, progress: () -> Float, content: @Composable () -> Unit) {
    if (enabled && Build.VERSION.SDK_INT >= 33) {
        WavyContent(progress, content)
    } else {
        content()
    }
}
```

## Testing

- Screenshot-test shader-enabled and fallback paths.
- Verify semantics and TalkBack output are identical in both paths.
- Benchmark frame time, jank, GPU memory, and thermals with
  Macrobenchmark/Perfetto on representative low-end and high-end devices.
- Exercise configuration changes and process recreation; do not assume a shader
  that compiles on one GPU behaves identically on another.

## Sources

- `RuntimeShader` (API 33): https://developer.android.com/reference/android/graphics/RuntimeShader
- Compose graphics overview: https://developer.android.com/develop/ui/compose/graphics/draw/overview
- Compose graphics modifiers: https://developer.android.com/develop/ui/compose/graphics/draw/modifiers
- Android Dev Summit graphics session: https://developer.android.com/events/dev-summit/talks/elevate-your-apps-with-the-latest-graphics-features-in-jetpack-compose-and-android
