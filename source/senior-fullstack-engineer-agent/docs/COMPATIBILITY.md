# Compatibility

## Intended formats

- Agent Skills directories with `SKILL.md` frontmatter.
- Codex/ChatGPT skills-only Plugin with `.codex-plugin/plugin.json` and `skills/`.
- Repository marketplace with `.agents/plugins/marketplace.json` and `plugins/<name>/`.

## Current verification level

- Source and plugin static validation: automated.
- Archive integrity and checksums: automated.
- Codex manifest contract: locally validated against the current official field guide.
- Real Codex/ChatGPT installation and skill discovery: requires host testing.
- Claude, Cursor, and VS Code adapters: not part of this Stage 5 release artifact.

## Upstream limitations

Codex plugin and local marketplace behavior is evolving. Always test the exact host version and use a new plugin version when content changes.
