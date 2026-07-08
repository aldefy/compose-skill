import org.gradle.api.DefaultTask
import org.gradle.api.file.DirectoryProperty
import org.gradle.api.provider.ListProperty
import org.gradle.api.tasks.InputFiles
import org.gradle.api.tasks.OutputDirectory
import org.gradle.api.tasks.TaskAction
import java.io.File

abstract class GenerateClaimTests : DefaultTask() {
    @get:InputFiles abstract val markdownFiles: ListProperty<File>
    @get:OutputDirectory abstract val outputDir: DirectoryProperty

    @TaskAction
    fun generate() {
        val claims = markdownFiles.get().flatMap { f -> ClaimParser.parse(f.readText(), f.name) }
        val compileBlocks = markdownFiles.get().flatMap { f -> ClaimParser.parseCompileBlocks(f.readText(), f.name) }
        requireUniqueNames(claims.map { it.name }, "verify")
        requireUniqueNames(compileBlocks.map { it.name }, "compile")

        val out = outputDir.get().asFile
        out.deleteRecursively(); out.mkdirs()

        val tests = claims.joinToString("\n\n") { c ->
            val asserts = c.asserts.joinToString("\n") { a -> emitAssertion(a) }
            """
            @Test fun `${c.name}`() {
                rule.setContent { ClaimSubjects.`${c.name}`() }
            $asserts
            }
            """.trimIndent()
        }

        val subjects = claims.joinToString("\n\n") { c ->
            // rename Subject() -> the claim name so many blocks coexist
            renameSubject(c.subjectSource, c.name).prependIndent("    ")
        }

        val compileSubjects = compileBlocks.joinToString("\n\n") { c ->
            // No @Test is emitted. If this file compiles, the doc block compiles.
            renameSubject(c.subjectSource, c.name).prependIndent("    ")
        }

        File(out, "GeneratedClaimTests.kt").writeText(
            """
            ${generatedImports()}

            @RunWith(RobolectricTestRunner::class)
            @GraphicsMode(GraphicsMode.Mode.NATIVE)
            @Config(sdk = [34])
            class GeneratedClaimTests {
                @get:Rule val rule = createComposeRule()

            $tests
            }

            object ClaimSubjects {
            $subjects
            }
            """.trimIndent(),
        )

        File(out, "GeneratedCompileOnlySubjects.kt").writeText(
            """
            ${generatedImports()}

            object CompileOnlySubjects {
            $compileSubjects
            }
            """.trimIndent(),
        )
        logger.lifecycle(
            "generateClaimTests: emitted ${claims.size} claim test(s), ${compileBlocks.size} compile-only subject(s)",
        )
    }

    private fun renameSubject(source: String, name: String): String =
        source.replace(
            Regex("""@Composable\s+fun\s+Subject\s*\("""),
            "@Composable fun `$name`(",
        )

    private fun requireUniqueNames(names: List<String>, marker: String) {
        val duplicate = names.groupingBy { it }.eachCount().filterValues { it > 1 }.keys.firstOrNull()
        require(duplicate == null) { "duplicate kotlin $marker block name '$duplicate'" }
    }

    private fun emitAssertion(assertion: Assertion): String =
        when (assertion.prop) {
            "width" -> "        rule.onRoot().assertWidthIsEqualTo(${assertion.value}.dp)"
            "height" -> "        rule.onRoot().assertHeightIsEqualTo(${assertion.value}.dp)"
            "text" -> "        rule.onNodeWithText(\"${assertion.value.escapeKotlinString()}\").assertExists()"
            "has-click-action" ->
                "        rule.onNodeWithText(\"${assertion.value.escapeKotlinString()}\").assertHasClickAction()"
            else -> error("unsupported assertion prop '${assertion.prop}'")
        }

    private fun String.escapeKotlinString(): String =
        replace("\\", "\\\\").replace("\"", "\\\"")

    private fun generatedImports(): String =
        """
            import androidx.compose.foundation.background
            import androidx.compose.foundation.clickable
            import androidx.compose.foundation.lazy.LazyColumn
            import androidx.compose.foundation.lazy.items
            import androidx.compose.foundation.layout.*
            import androidx.compose.animation.AnimatedVisibility
            import androidx.compose.material3.*
            import androidx.compose.runtime.*
            import androidx.compose.ui.Modifier
            import androidx.compose.ui.graphics.Color
            import androidx.compose.ui.unit.dp
            import androidx.compose.ui.test.junit4.createComposeRule
            import androidx.compose.ui.test.onRoot
            import androidx.compose.ui.test.onNodeWithText
            import androidx.compose.ui.test.assertHasClickAction
            import androidx.compose.ui.test.assertWidthIsEqualTo
            import androidx.compose.ui.test.assertHeightIsEqualTo
            import org.junit.Rule
            import org.junit.Test
            import org.junit.runner.RunWith
            import org.robolectric.RobolectricTestRunner
            import org.robolectric.annotation.Config
            import org.robolectric.annotation.GraphicsMode
        """.trimIndent()
}
