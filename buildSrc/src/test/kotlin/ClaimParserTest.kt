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
        assertEquals(listOf("width" to "100", "height" to "100"), c.asserts.map { it.prop to it.value })
        assert(c.subjectSource.contains("fun Subject()"))
    }

    @Test fun parsesTextAndClickActionAssertions() {
        val md = """
            ```kotlin verify
            // name: button-semantics
            @Composable fun Subject() {
                Button(onClick = {}) { Text("Save") }
            }
            // assert: text = "Save"
            // assert: has-click-action = "Save"
            ```
        """.trimIndent()

        val claim = ClaimParser.parse(md, "x.md").single()
        assertEquals(
            listOf("text" to "Save", "has-click-action" to "Save"),
            claim.asserts.map { it.prop to it.value },
        )
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

    @Test fun parsesCompileBlocksSeparatelyFromVerifyBlocks() {
        val md = """
            ```kotlin compile
            // name: stable-material-button
            @Composable fun Subject() {
                Button(onClick = {}) { Text("Save") }
            }
            ```

            ```kotlin verify
            // name: measured-box
            @Composable fun Subject() { Box(Modifier.size(100.dp)) }
            // assert: width = 100.dp
            ```
        """.trimIndent()

        val compileBlocks = ClaimParser.parseCompileBlocks(md, "x.md")
        assertEquals(1, compileBlocks.size)
        assertEquals("stable-material-button", compileBlocks.single().name)
        assert(compileBlocks.single().subjectSource.contains("fun Subject()"))
    }

    @Test fun rejectsCompileBlockWithoutName() {
        val md = "```kotlin compile\n@Composable fun Subject() {}\n```"
        val ex = assertThrows(IllegalStateException::class.java) {
            ClaimParser.parseCompileBlocks(md, "x.md")
        }
        assert(ex.message!!.contains("name"))
    }

    @Test fun rejectsCompileBlockWithoutSubject() {
        val md = "```kotlin compile\n// name: missing-subject\nval x = 1\n```"
        assertThrows(IllegalStateException::class.java) {
            ClaimParser.parseCompileBlocks(md, "x.md")
        }
    }
}
