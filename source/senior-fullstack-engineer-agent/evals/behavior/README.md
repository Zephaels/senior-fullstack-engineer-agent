# RED → GREEN → Regression Behavior Evaluation

## Goal

Measure whether a model behaves better because the Skill is loaded, not merely whether the Skill file is syntactically valid.

## Configurations

1. **RED baseline** — prompt sent to a clean model session without this Skill.
2. **GREEN target skill** — same prompt with only the root governance files and target workflow available.
3. **Regression full tree** — same prompt with the full current package available.

Use identical model, version, temperature, tools, files and run count. Isolate sessions so the baseline cannot see prior Skill text.

## Runner contract

The included script accepts an external command template. The command must read a JSON request file and write a JSON response file:

```json
{
  "response": "model output text",
  "tool_calls": [],
  "metadata": {"model": "...", "tokens": 0}
}
```

The request includes the prompt, configuration, root path and skill paths.

## Scoring

Each expectation is scored against observable output or tool actions. Do not award points for repeating rules without following them. A prohibited action is a blocker even if the prose sounds correct.

Recommended manual blind review remains necessary for subtle architecture and safety judgments.

## Current environment

If no authenticated runner is available, `eval-engine/runners/run_behavior_evals_v2.py` writes a blocked attempt report. This is intentional: it is better to report no model run than fabricate RED/GREEN pass rates.
