# Contributing

## Before changing a Skill

1. Identify the owning workflow and expected behavior.
2. Add or update positive and negative trigger cases.
3. Add behavior, pressure, or regression coverage for the change.
4. Preserve the constitution and decision policy.
5. Update `CHANGELOG.md` when behavior or distribution changes.
6. Update `NOTICE.md` when a new external source materially influences the design.

## Pull requests

- Keep changes focused.
- Do not combine unrelated refactors with behavior changes.
- Report tests and validators actually run.
- Disclose generated files and source files.
- Do not commit secrets, API keys, production data, or local caches.
- Do not weaken a quality or permission gate without an explicit architecture decision.
