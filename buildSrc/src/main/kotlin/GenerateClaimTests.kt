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
        val out = outputDir.get().asFile
        out.deleteRecursively(); out.mkdirs()

        val tests = claims.joinToString("\n\n") { c ->
            val asserts = c.asserts.joinToString("\n") { a ->
                val fn = if (a.prop == "width") "assertWidthIsEqualTo" else "assertHeightIsEqualTo"
                "        rule.onRoot().$fn(${a.dp}.dp)"
            }
            """
            @Test fun `${c.name}`() {
                rule.setContent { ClaimSubjects.`${c.name}`() }
            $asserts
            }
            """.trimIndent()
        }

        val subjects = claims.joinToString("\n\n") { c ->
            // rename Subject() -> the claim name so many blocks coexist
            val renamed = c.subjectSource.replace(
                Regex("""@Composable\s+fun\s+Subject\s*\("""),
                "@Composable fun `${c.name}`(",
            )
            renamed.prependIndent("    ")
        }

        File(out, "GeneratedClaimTests.kt").writeText(
            """
            import androidx.compose.foundation.background
            import androidx.compose.foundation.clickable
            import androidx.compose.foundation.layout.*
            import androidx.compose.material3.*
            import androidx.compose.runtime.Composable
            import androidx.compose.ui.Modifier
            import androidx.compose.ui.graphics.Color
            import androidx.compose.ui.unit.dp
            import androidx.compose.ui.test.junit4.createComposeRule
            import androidx.compose.ui.test.onRoot
            import androidx.compose.ui.test.assertWidthIsEqualTo
            import androidx.compose.ui.test.assertHeightIsEqualTo
            import org.junit.Rule
            import org.junit.Test
            import org.junit.runner.RunWith
            import org.robolectric.RobolectricTestRunner
            import org.robolectric.annotation.Config
            import org.robolectric.annotation.GraphicsMode

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
        logger.lifecycle("generateClaimTests: emitted ${claims.size} claim test(s)")
    }
}
