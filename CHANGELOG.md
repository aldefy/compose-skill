# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-03-01

### Added
- Styles API (experimental) reference guide — covers `Style {}`, `MutableStyleState`, `Modifier.styleable()`, composition, theme integration, and alpha06 gotchas

### Fixed
- Claude Code setup: replaced non-existent `claude skill add` CLI command with correct file-based `~/.claude/skills/` and `.claude/skills/` approach
- Codex CLI setup: removed non-existent `--instructions` flag, now uses `AGENTS.md` only
- Windsurf setup: updated from legacy `.windsurfrules` to current `.windsurf/rules/*.md` approach
- Swapped logo to MIT-licensed devicon SVG

## [1.0.0] - 2026-02-28

### Added
- 13 reference guides covering state management, view composition, modifiers, side effects, composition locals, lists/scrolling, navigation, animation, theming (Material3), performance, accessibility, deprecated patterns
- 5 source code files from `androidx/androidx` (runtime, UI, foundation, material3, navigation)
- SKILL.md with workflow, checklists, and two-layer approach (guidance + source receipts)
- Setup instructions for Claude Code, Codex CLI, Gemini CLI, Cursor, GitHub Copilot, Windsurf, and Amazon Q Developer
