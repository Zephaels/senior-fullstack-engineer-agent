# RC.4.1 Implementation

Version: `1.0.0-rc.4.8`

Implemented in order:

1. Router v2
2. Eval Engine v2
3. Automatic Scorecard
4. Transactional Installer
5. Full static validation
6. Reproducible RC source packaging

Real Codex runtime and model evidence remain a subsequent qualification phase. Missing model or runtime evidence blocks GA rather than being replaced by mock scores.

## Eval Evidence Boundary

Trigger selection uses metadata only. GREEN behavior loads Core plus one target Skill and required assets. Regression is accepted only from a real Codex Plugin runtime with a fresh session and forced Skill reload. Missing runners or judges produce blocked reports, never synthetic pass rates.
