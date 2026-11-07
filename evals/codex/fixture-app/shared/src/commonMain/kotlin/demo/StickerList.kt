package demo

import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable

data class Sticker(val id: Long, val name: String)

@Composable
fun StickerList(stickers: List<Sticker>) {
    LazyColumn {
        items(stickers) { sticker ->
            Text(sticker.name)
        }
    }
}
