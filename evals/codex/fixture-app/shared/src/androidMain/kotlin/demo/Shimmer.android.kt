package demo

import android.graphics.RuntimeShader
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.graphics.ShaderBrush

private const val SRC = """
    uniform float2 resolution;
    half4 main(float2 p) { return half4(p / resolution, 0.5, 1.0); }
"""

fun Modifier.shimmer(): Modifier = drawBehind {
    val shader = RuntimeShader(SRC)
    shader.setFloatUniform("resolution", size.width, size.height)
    drawRect(ShaderBrush(shader))
}
