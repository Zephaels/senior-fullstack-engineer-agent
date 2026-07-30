# Evaluation Suite

This directory contains the first evaluation baseline for the Stage 2 workflow skills.

## Trigger evaluation

Each workflow stores `evals/trigger_evals.json` as a mixed list of realistic prompts:

```json
[
  {"query": "...", "should_trigger": true},
  {"query": "...", "should_trigger": false}
]
```

The suite intentionally includes close negative cases so that a workflow is not triggered merely because a related noun appears.

Run trigger evaluations with a compatible Agent Skills evaluation harness. Record model, host, description version, run count, trigger rate, false positives, and false negatives.

## Pressure evaluation

`pressure/pressure_evals.json` tests whether the Agent follows lifecycle, evidence, safety, scope, freshness, and phase-boundary rules under realistic pressure such as authority, deadlines, sunk cost, production impact, missing evidence, and requests to bypass process.

Recommended process:

1. Run the scenario without the relevant skill and record baseline behavior.
2. Run the same scenario with the relevant skill loaded.
3. Score only observable actions and outputs, not rule recitation.
4. Record new rationalizations or loopholes.
5. Revise the smallest relevant rule.
6. Re-run all prior cases to prevent regression.

## Current status

The cases are authored and statically validated. They have not yet been executed against Claude Code, Codex, ChatGPT, Cursor, or another model host. No pass-rate claim is made.


## Stage 3 additions

Stage 3 adds trigger and quality evals for implementation, test engineering, debugging, QA, code review and preflight, plus cross-workflow regression cases and an external-runner RED/GREEN/Regression harness. A blocked no-runner report is an honest result, not a pass.
