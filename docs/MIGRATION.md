# Migrating from the manual file-copy install

Before v2.1.0, this skill was distributed by having users copy files into
`~/.claude/skills/` (or the Codex/Copilot equivalent). That path no longer
receives updates.

## How to tell if you are on the stale path

Open `~/.claude/skills/compose-expert/SKILL.md` (or wherever you copied it).
Look at the frontmatter at the top of the file.

- **If it has `version:` (e.g. `version: 2.1.0`)** → you are up to date or
  already on the plugin path. No action needed.
- **If it has no `version:` field** → you are stale. Migrate using the steps
  below.

## How to migrate

### Claude Code

```
rm -rf ~/.claude/skills/compose-expert
/plugin marketplace add aldefy/compose-skill
/plugin install compose-expert
```

### Copilot CLI

```
rm -rf ~/.copilot/skills/compose-expert
copilot plugin install aldefy/compose-skill
```

### Codex CLI

Codex has no native plugin system. Remove the old copy and follow the
manual-install path in [INSTALL.md](INSTALL.md#codex-cli).

## Why you should migrate

- Automatic update notifications via `/plugin update` (or `git pull` for Codex).
- Migration notes for breaking changes in every release.
- Version pinning — you can roll back if a release breaks your workflow.
