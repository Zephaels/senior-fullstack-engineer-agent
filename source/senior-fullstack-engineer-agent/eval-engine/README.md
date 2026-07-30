# Eval Engine v2

This engine mirrors progressive Skill loading instead of concatenating every Skill body.

1. `runners/build_skill_catalog.py` extracts only `name` and `description`.
2. `runners/run_trigger_evals.py` evaluates metadata-first discovery.
3. `runners/run_behavior_evals_v2.py` runs RED with no Skill, GREEN with only Core + target Skill + required assets, and requires a real Codex Plugin runtime adapter for Regression.
4. `runners/run_pressure_evals.py` runs pressure cases with only the relevant specialist contexts.
5. `runners/run_regression_evals.py` requires a real Codex Plugin runtime and fresh-session Skill discovery.
6. Graders compute deterministic routing metrics and use an independent judge only for semantic behavior or pressure expectations.
7. `graders/generate_scorecard.py` refuses GA when required evidence is missing.

External runner protocol: command template must contain `{request}` and `{response}`. Read request JSON and write response JSON. Mock transport must never be counted as model evidence.
