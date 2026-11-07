package demo

import android.os.Build
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable

@Composable
fun DeviceInfo() {
    Text("Running on ${Build.MODEL}")
}
