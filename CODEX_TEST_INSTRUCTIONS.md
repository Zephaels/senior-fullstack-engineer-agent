# Codex Test Instructions — v1.0.0-rc.4.3

This repository is the complete pending-release source and Codex Plugin candidate.

## Give Codex this repository

1. Extract the ZIP into a clean Git repository.
2. Commit the extracted baseline before testing.
3. Open the repository in Codex.
4. Copy the exact text from `docs/CODEX_EXECUTION_PROMPT.md` into Codex.
5. Let Codex execute `docs/CODEX_RC_TEST_PLAN.md`.

## Do not do these manually

- Do not rename the version to `1.0.0`.
- Do not delete failing cases.
- Do not allow Codex to push, publish, deploy, or use production credentials.
- Do not accept screenshots or statements without exact command and output evidence.

## Expected first command sequence

```bash
python scripts/validate_rc.py
python scripts/validate_plugin.py plugins/senior-fullstack-engineer-agent
python scripts/validate_release.py
```

The final Codex output must use `docs/CODEX_RESULT_TEMPLATE.md`.
