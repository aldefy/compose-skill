data class Assertion(val prop: String, val dp: Int)
data class Claim(val name: String, val subjectSource: String, val asserts: List<Assertion>)

object ClaimParser {
    private val fenceOpen = Regex("""^```kotlin\s+verify\s*$""")
    private val fenceClose = Regex("""^```\s*$""")
    private val nameLine = Regex("""^//\s*name:\s*([a-z0-9-]+)\s*$""")
    private val assertLine = Regex("""^//\s*assert:\s*(width|height)\s*=\s*(\d+)\.dp\s*$""")
    private val allowedProps = setOf("width", "height")

    fun parse(markdown: String, sourceFile: String): List<Claim> {
        val lines = markdown.lines()
        val claims = mutableListOf<Claim>()
        val seenNames = mutableSetOf<String>()
        var i = 0
        var blockIndex = 0
        while (i < lines.size) {
            if (fenceOpen.matches(lines[i].trim())) {
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

    private fun toClaim(
        body: List<String>, sourceFile: String, idx: Int, seenNames: MutableSet<String>,
    ): Claim {
        fun err(msg: String): Nothing =
            error("$sourceFile: verify block #$idx: $msg")

        val name = body.firstNotNullOfOrNull { nameLine.matchEntire(it.trim())?.groupValues?.get(1) }
            ?: err("missing '// name:' line")
        if (!seenNames.add(name)) err("duplicate name '$name'")

        val asserts = body.mapNotNull { line ->
            assertLine.matchEntire(line.trim())?.let { m -> Assertion(m.groupValues[1], m.groupValues[2].toInt()) }
        }
        if (asserts.isEmpty()) err("no '// assert: <width|height> = N.dp' lines")
        asserts.forEach { if (it.prop !in allowedProps) err("unsupported assert prop '${it.prop}'") }

        val subject = body.filterNot { l ->
            val t = l.trim()
            nameLine.matches(t) || assertLine.matches(t)
        }.joinToString("\n").trim()
        if (!subject.contains(Regex("""@Composable\s+fun\s+Subject\s*\("""))) {
            err("no '@Composable fun Subject()' found")
        }
        return Claim(name, subject, asserts)
    }
}
