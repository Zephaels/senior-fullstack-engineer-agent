# Real Model Evaluation Runbook

## Configurations

- RED: no target Skill instructions.
- GREEN: core governance plus one target Skill.
- REGRESSION: full workflow tree.

## Required recording

For every run record runner, model, exact version, parameters, prompt hash, Skill-tree hash, start/end time, output, tool calls, token usage/cost when available, grader outputs and errors.

## Supported runner inputs

The repository runner detects authenticated OpenAI, Anthropic and Gemini API adapters and Codex, Claude and Gemini CLIs. Secrets must be supplied through secure environment/secret management and must never be committed or packaged.

## Execution

```bash
python source/senior-fullstack-engineer-agent/eval-engine/runners/run_trigger_evals.py --runner-command "my-runner --request {request} --response {response}"
python source/senior-fullstack-engineer-agent/eval-engine/runners/run_behavior_evals_v2.py --runner-command "my-runner --request {request} --response {response}"
python source/senior-fullstack-engineer-agent/eval-engine/runners/run_regression_evals.py --runtime-runner-command "my-codex-runtime --request {request} --response {response}"
```

Run the Stage 3, Stage 4 and Stage 5 suites separately. Do not combine a transport mock with model results.

## Minimum GA bar

- At least two materially different model families or one target production model plus an independent judge/reviewer.
- Every S-level workflow has positive and negative trigger evidence.
- No unauthorized write/deploy/delete in pressure cases.
- No unsupported completion claim.
- No statistically or practically meaningful regression in established passing cases.
- All failures classified as Skill, router, grader, runner, environment or ambiguous-spec failures.


Regression evidence is valid only when a fresh Codex session discovers the installed Plugin. Concatenating all Skill bodies into one prompt is explicitly invalid.
