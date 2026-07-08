data class Assertion(val prop: String, val value: String, val negated: Boolean = false)
data class Claim(val name: String, val subjectSource: String, val asserts: List<Assertion>, val repeatCount: Int)
data class CompileBlock(val name: String, val subjectSource: String)

object ClaimParser {
    private val verifyFenceOpen = Regex("""^```kotlin\s+verify\s*$""")
    private val compileFenceOpen = Regex("""^```kotlin\s+compile\s*$""")
    private val fenceClose = Regex("""^```\s*$""")
    private val nameLine = Regex("""^//\s*name:\s*([a-z0-9-]+)\s*$""")
    private val repeatLine = Regex("""^//\s*repeat:\s*(\d+)\s*$""")
    private val dpAssertLine = Regex("""^//\s*assert:\s*(width|height)\s*=\s*(\d+)\.dp\s*$""")
    private val stringAssertLine = Regex("""^//\s*assert:\s*(text|has-click-action|content-description)\s*=\s*"([^"]+)"\s*$""")
    private val stringNegativeAssertLine = Regex("""^//\s*assert-not:\s*(text|content-description)\s*=\s*"([^"]+)"\s*$""")
    private val allowedProps = setOf("width", "height", "text", "has-click-action", "content-description")

    fun parse(markdown: String, sourceFile: String): List<Claim> {
        val lines = markdown.lines()
        val claims = mutableListOf<Claim>()
        val seenNames = mutableSetOf<String>()
        var i = 0
        var blockIndex = 0
        while (i < lines.size) {
            if (verifyFenceOpen.matches(lines[i].trim())) {
                val body = mutableListOf<String>()
                i++
                while (i < lines.size && !fenceClose.matches(lines[i].trim())) {
                    body.add(lines[i]); i++
                }
                claims.add(toClaim(body, sourceFile, blockIndex, seenNames))
                blockIndex++
            }
            i++
        }
        return claims
    }

    fun parseCompileBlocks(markdown: String, sourceFile: String): List<CompileBlock> {
        val lines = markdown.lines()
        val blocks = mutableListOf<CompileBlock>()
        val seenNames = mutableSetOf<String>()
        var i = 0
        var blockIndex = 0
        while (i < lines.size) {
            if (compileFenceOpen.matches(lines[i].trim())) {
                val body = mutableListOf<String>()
                i++
                while (i < lines.size && !fenceClose.matches(lines[i].trim())) {
                    body.add(lines[i]); i++
                }
                blocks.add(toCompileBlock(body, sourceFile, blockIndex, seenNames))
                blockIndex++
            }
            i++
        }
        return blocks
    }

    private fun toClaim(
        body: List<String>, sourceFile: String, idx: Int, seenNames: MutableSet<String>,
    ): Claim {
        fun err(msg: String): Nothing =
            error("$sourceFile: verify block #$idx: $msg")

        val name = body.firstNotNullOfOrNull { nameLine.matchEntire(it.trim())?.groupValues?.get(1) }
            ?: err("missing '// name:' line")
        if (!seenNames.add(name)) err("duplicate name '$name'")

        val repeatCount = body.firstNotNullOfOrNull { repeatLine.matchEntire(it.trim())?.groupValues?.get(1)?.toInt() } ?: 1
        if (repeatCount < 1) err("repeat count must be >= 1")

        val asserts = body.mapNotNull { line ->
            val trimmed = line.trim()
            dpAssertLine.matchEntire(trimmed)?.let { m ->
                Assertion(m.groupValues[1], m.groupValues[2])
            } ?: stringAssertLine.matchEntire(trimmed)?.let { m ->
                Assertion(m.groupValues[1], m.groupValues[2])
            } ?: stringNegativeAssertLine.matchEntire(trimmed)?.let { m ->
                Assertion(m.groupValues[1], m.groupValues[2], true)
            }
        }
        if (asserts.isEmpty()) {
            err("no '// assert:' or '// assert-not:' lines")
        }
        asserts.forEach { if (it.prop !in allowedProps) err("unsupported assert prop '${it.prop}'") }

        val subject = body.filterNot { l ->
            val t = l.trim()
            nameLine.matches(t) || repeatLine.matches(t) || dpAssertLine.matches(t) || stringAssertLine.matches(t) || stringNegativeAssertLine.matches(t)
        }.joinToString("\n").trim()
        if (!subject.contains(Regex("""@Composable\s+fun\s+Subject\s*\("""))) {
            err("no '@Composable fun Subject()' found")
        }
        return Claim(name, subject, asserts, repeatCount)
    }

    private fun toCompileBlock(
        body: List<String>, sourceFile: String, idx: Int, seenNames: MutableSet<String>,
    ): CompileBlock {
        fun err(msg: String): Nothing =
            error("$sourceFile: compile block #$idx: $msg")

        val name = body.firstNotNullOfOrNull { nameLine.matchEntire(it.trim())?.groupValues?.get(1) }
            ?: err("missing '// name:' line")
        if (!seenNames.add(name)) err("duplicate name '$name'")

        val subject = body.filterNot { l -> nameLine.matches(l.trim()) }.joinToString("\n").trim()
        if (!subject.contains(Regex("""@Composable\s+fun\s+Subject\s*\("""))) {
            err("no '@Composable fun Subject()' found")
        }
        return CompileBlock(name, subject)
    }
}
