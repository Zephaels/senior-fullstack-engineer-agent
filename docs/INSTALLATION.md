# Installation and Verification

This is an RC qualification candidate. Follow `CODEX_TEST_INSTRUCTIONS.md` and `docs/CODEX_RC_TEST_PLAN.md`.

The repository marketplace entry points to `./plugins/senior-fullstack-engineer-agent`. For a non-default local marketplace, use the current Codex marketplace installation command for the repository root, then verify with the Plugins UI or available `codex plugin` commands.

A standalone Skill copied to `${CODEX_HOME:-$HOME/.codex}/skills/` is a diagnostic fallback only; it does not prove plugin discovery. Always start a fresh Codex session after installation or version changes.
