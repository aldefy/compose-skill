# AGSL Shaders in Compose

> AGSL is Android-only. `RuntimeShader` needs Android 13 (API 33). Treat shader
> effects as an optional rendering layer: gate by API level, keep a readable
> fallback, and measure GPU cost on target devices. Compose Multiplatform
> targets other than Android have no `RuntimeShader`.

Android Graphics Shading Language (AGSL) is a subset of GLSL-style shading. Your
`main(float2 fragCoord)` runs per pixel and returns a **premultiplied-alpha**
color. A `RuntimeShader` is an `android.graphics.Shader`: it contributes a
function to the fragment shader Android assembles for a draw call, so it can be
used anywhere a normal shader can — in a `ShaderBrush`, a `Paint`, or a
`RenderEffect`. Use it for gradients that built-in brushes cannot express,
frosted glass, lighting, ripples, and color transforms — not for layout or
effects a normal `Brush`, `Canvas`, or shape can do.

## Choose the integration

| Goal | API | Min API |
|---|---|---|
| Paint a custom fill (background, text brush, `drawRect`) | `ShaderBrush(RuntimeShader)` in `drawWithCache` / `onDrawBehind` | 33 |
| Transform already-rendered content of a composable | `RenderEffect.createRuntimeShaderEffect(shader, "content")` via `graphicsLayer { renderEffect = ... }` | 33 |

## Fill with `ShaderBrush` (official pattern)

Create the shader and brush once, set size uniforms where the size is known
(`drawWithCache`), and set per-frame uniforms in `onDrawBehind`. This is the
pattern in the Compose Brush guide and the official performance skill.

```kotlin
@Language("AGSL")
private val CUSTOM_SHADER = """
    uniform float2 resolution;
    layout(color) uniform half4 color;
    layout(color) uniform half4 color2;

    half4 main(in float2 fragCoord) {
        float2 uv = fragCoord / resolution.xy;
        float mixValue = distance(uv, float2(0, 1));
        return mix(color, color2, mixValue);
    }
""".trimIndent()

@RequiresApi(Build.VERSION_CODES.TIRAMISU)
@Composable
fun ShaderBrushExample(from: Color, to: Color, modifier: Modifier = Modifier) {
    Box(
        modifier
            .drawWithCache {
                val shader = RuntimeShader(CUSTOM_SHADER)   // compiles here
                val shaderBrush = ShaderBrush(shader)
                shader.setFloatUniform("resolution", size.width, size.height)
                onDrawBehind {
                    shader.setColorUniform("color", from.toArgb())
                    shader.setColorUniform("color2", to.toArgb())
                    drawRect(shaderBrush)
                }
            }
            .fillMaxWidth()
            .height(200.dp)
    )
}
```

Notes:

- `layout(color)` marks a `half4` uniform as a color so Android converts it to
  the shader's working color space; set it with `setColorUniform`. Plain
  `vec4` uniforms are not converted.
- `drawWithCache` re-runs when the size changes or a read state changes, so the
  shader is recompiled then. The official guide builds it inside the cache
  block; the performance skill alternatively `remember`s the `RuntimeShader`
  and `ShaderBrush` in composition and updates size uniforms in `drawWithCache`.
  Either way, never compile per frame.
- A `ShaderBrush` always returns the same shader instance for any size; update
  uniforms rather than creating new shaders.
- The official sample also shows a top-level `val shader = RuntimeShader(src)`
  with `setFloatUniform` in a `Canvas` draw scope. That is fine for one
  instance, but a shared shader mutated from several composables will show the
  last writer's uniforms.

### Animating uniforms

Pass time/progress as a lambda or `State` and read it only in `onDrawBehind`, so
animation invalidates draw, not composition:

```kotlin
fun Modifier.animatedShader(time: () -> Float): Modifier = drawWithCache {
    val shader = RuntimeShader(ANIMATED_SHADER)
    val brush = ShaderBrush(shader)
    shader.setFloatUniform("iResolution", size.width, size.height)
    onDrawBehind {
        shader.setFloatUniform("iTime", time())
        drawRect(brush)
    }
}
```

## Transform content with `RenderEffect`

`RenderEffect.createRuntimeShaderEffect(shader, "name")` binds the rendered
content of a node to a `uniform shader name;` in your AGSL so you can sample it
with `name.eval(fragCoord)`. In Compose, apply it through `graphicsLayer` and
convert it with `asComposeRenderEffect()`.

```kotlin
private const val WAVE = """
    uniform shader content;
    uniform float2 resolution;
    uniform float progress;
    half4 main(float2 fragCoord) {
        float dx = sin(fragCoord.y / resolution.y * 20.0 + progress) * 6.0;
        return content.eval(fragCoord + float2(dx, 0.0));
    }
"""

@RequiresApi(Build.VERSION_CODES.TIRAMISU)
@Composable
fun WavyContent(progress: () -> Float, content: @Composable () -> Unit) {
    val shader = remember { RuntimeShader(WAVE) }
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

> [!NOTE]
> The official AGSL guide shows `createRuntimeShaderEffect` on a View, and the
> Compose docs show `graphicsLayer { renderEffect }` and
> `asComposeRenderEffect()` separately. The combined composable above is
> assembled from those documented pieces, not copied from one official sample.
> Run it on a device before relying on it, and apply the effect's cost warning:
> the official guide says a runtime-shader `RenderEffect` is more expensive than
> drawing in a custom view.

`graphicsLayer` facts to design around:

- `RenderEffect` on a layer is supported on Android 12+ and ignored below; a
  runtime-shader effect additionally needs API 33.
- Setting a `RenderEffect` always renders the layer into an offscreen buffer,
  regardless of `CompositingStrategy`. That costs memory and fill rate.
- The offscreen buffer defaults to the layout bounds, so effects that draw
  outside them (glows, shadows) are clipped. Compose 1.12.0-alpha01+ adds
  `graphicsLayer(outsets = LayerOutsets(24.dp), clip = false)` to enlarge the
  buffer without changing layout.
- `graphicsLayer` does not change measurement or placement.
- Prefer the lambda form of `graphicsLayer` when reading state or animating.

## AGSL rules that cause real bugs

- Origin is the **upper-left**, unlike GLSL's lower-left. Coordinates are in
  pixels of the canvas/render node, not normalized UV; `BitmapShader` also
  samples in pixels, not 0..1.
- Return premultiplied alpha: `[R*A, G*A, B*A, A]`.
- Declare every uniform you set. A missing name or wrong type throws
  `IllegalArgumentException` (for example `setFloatUniform(name, x, y)` needs a
  `float2`/`vec2`).
- Uninitialized primitive uniforms are 0; uninitialized color and shader
  uniforms are undefined.
- `setInputShader` binds a `Shader` to `uniform shader`; `setInputBuffer` skips
  color-space conversion for non-color data (normal maps, height maps).
- Constructing `RuntimeShader(src)` compiles the shader — a syntax error
  surfaces there, not at first draw.

## Fallback

Provide the same content without the shader when `SDK_INT < 33`, when
construction throws, or when your frame budget is exceeded. Interaction,
semantics, and essential contrast must not depend on shader output.

```kotlin
@Composable
fun OptionalWave(enabled: Boolean, progress: () -> Float, content: @Composable () -> Unit) {
    if (enabled && Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        WavyContent(progress, content)
    } else {
        content()
    }
}
```

## How to test and evaluate shaders

Shaders are GPU programs, so most of the risk is invisible to JVM tests. Split
the checks by what can actually run where.

| Layer | What to check | Where it runs |
|---|---|---|
| Source compiles | `RuntimeShader(src)` does not throw for every shader constant | Instrumented test, API 33+ device/emulator |
| Uniform contract | Every uniform you set is declared with that type; set each one once in a test | Same instrumented test |
| Uniform math | Mapping app state to uniforms (progress, time, colors, size) | Plain JVM unit test — keep it in ordinary Kotlin, not inline in the draw lambda |
| Visual output | Rendered pixels match a golden within tolerance | Instrumented screenshot on a real GPU or emulator with GPU enabled |
| Fallback path | `SDK_INT < 33` renders the same content and semantics | JVM test with `@Config(sdk = [32])` or an API 32 emulator |
| Performance | Frame time, jank, GPU/thermal | Macrobenchmark + Perfetto on representative devices |

Instrumented compile + uniform test:

```kotlin
@RunWith(AndroidJUnit4::class)
@SdkSuppress(minSdkVersion = Build.VERSION_CODES.TIRAMISU)
class ShaderContractTest {
    @Test
    fun customShader_compilesAndAcceptsDeclaredUniforms() {
        val shader = RuntimeShader(CUSTOM_SHADER)        // throws on bad AGSL
        shader.setFloatUniform("resolution", 100f, 100f) // throws if undeclared/wrong type
        shader.setColorUniform("color", Color.Red.toArgb())
        shader.setColorUniform("color2", Color.Blue.toArgb())
    }
}
```

Evaluation guidance:

- **Do not assume a JVM screenshot library renders AGSL.** Layoutlib-based and
  Robolectric-native renderers have documented gaps for blur and shader-style
  effects, and nothing here confirms `RuntimeShader` support. Prove it with a
  known-color shader (for example the official solid-red `half4(1,0,0,1)`
  sample) before trusting a JVM golden; otherwise capture goldens on a device.
- **Golden stability:** GPUs differ. Compare with a tolerance and per-device
  goldens, or assert on sampled pixels (a few known coordinates) instead of a
  whole-image diff. Pin the render size and pass time/progress as fixed inputs
  so frames are reproducible.
- **Test degenerate inputs:** zero size (the first `drawWithCache` pass can be
  0x0 — divide by `resolution` is NaN/Inf), huge sizes, progress outside 0..1,
  fully transparent colors, and dark/light themes.
- **Test lifecycle:** rotate and resize, recreate the activity, and scroll the
  composable in and out of a lazy list to catch shared-shader uniform leaks.
- **Semantics parity:** assert the fallback and shader paths produce the same
  semantics tree and content descriptions.
- **Cost budget:** profile before shipping. Run a Macrobenchmark with
  `FrameTimingMetric` with the effect on and off; capture a Perfetto trace for
  GPU time. Fullscreen, stacked blur + shader + alpha layers are the usual
  offenders.

> [!NOTE]
> This skill's own `verify-claims` blocks run under Robolectric, so they cannot
> execute shader code. AGSL claims in this reference are checked against the
> official docs by hand, not by the generated tests.

## Sources

- `RuntimeShader` reference (API 33): https://developer.android.com/reference/android/graphics/RuntimeShader
- Using AGSL in your app (compile at construction, Compose `ShaderBrush`, `RenderEffect`): https://developer.android.com/develop/ui/views/graphics/agsl/using-agsl
- Brush guide — AGSL `RuntimeShader` brush (official Compose sample, API 33 note): https://developer.android.com/develop/ui/compose/graphics/draw/brush
- Graphics modifiers — `graphicsLayer`, `RenderEffect` offscreen behavior, `LayerOutsets`: https://developer.android.com/develop/ui/compose/graphics/draw/modifiers
- Compose performance skill (shader uniform scoping): https://developer.android.com/agents/skills/jetpack-compose/jetpack-compose-performance/skill
- Dev Summit graphics session: https://developer.android.com/events/dev-summit/talks/elevate-your-apps-with-the-latest-graphics-features-in-jetpack-compose-and-android
