# Installing the Compose Expert skill

This skill ships as a plugin. Pick your host.

## Claude Code

```
/plugin marketplace add aldefy/compose-skill
/plugin install compose-expert
```

Update later with `/plugin update`.

## Copilot CLI

```
copilot plugin install aldefy/compose-skill
```

Update later with `copilot plugin update aldefy/compose-skill`.

## Codex CLI

Codex does not have a native plugin system yet. Manual install:

```
git clone https://github.com/aldefy/compose-skill ~/.codex/skills-src/compose-skill
ln -s ~/.codex/skills-src/compose-skill/skills/compose-expert ~/.codex/skills/compose-expert
```

Update later with `cd ~/.codex/skills-src/compose-skill && git pull`.

Watch [GitHub Releases](https://github.com/aldefy/compose-skill/releases) for update notifications — no automatic update channel exists for Codex users today.

## Coming from a manual file copy?

See [MIGRATION.md](MIGRATION.md).
