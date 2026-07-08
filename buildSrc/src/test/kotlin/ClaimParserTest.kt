import org.junit.Assert.assertEquals
import org.junit.Assert.assertThrows
import org.junit.Test

class ClaimParserTest {
    private val good = """
        Intro text.

        ```kotlin verify
        // name: size-before-padding
        @Composable fun Subject() {
            Box(Modifier.size(100.dp).padding(16.dp))
        }
        // assert: width = 100.dp
        // assert: height = 100.dp
        ```

        ```kotlin
        // illustrative, not verified
        Box(Modifier.size(1.dp))
        ```
    """.trimIndent()

    @Test fun parsesOnlyVerifyBlocks() {
        val claims = ClaimParser.parse(good, "x.md")
        assertEquals(1, claims.size)
        val c = claims.single()
        assertEquals("size-before-padding", c.name)
        assertEquals(listOf("width" to 100, "height" to 100), c.asserts.map { it.prop to it.dp })
        assert(c.subjectSource.contains("fun Subject()"))
    }

    @Test fun rejectsMissingName() {
        val md = "```kotlin verify\n@Composable fun Subject() {}\n// assert: width = 1.dp\n```"
        val ex = assertThrows(IllegalStateException::class.java) { ClaimParser.parse(md, "x.md") }
        assert(ex.message!!.contains("name"))
    }

    @Test fun rejectsDuplicateName() {
        val block = "```kotlin verify\n// name: dup\n@Composable fun Subject() {}\n// assert: width = 1.dp\n```"
        val md = "$block\n\n$block"
        assertThrows(IllegalStateException::class.java) { ClaimParser.parse(md, "x.md") }
    }

    @Test fun rejectsNoSubject() {
        val md = "```kotlin verify\n// name: n\n// assert: width = 1.dp\n```"
        assertThrows(IllegalStateException::class.java) { ClaimParser.parse(md, "x.md") }
    }
}
