---
name: skill-evaluation
description: Evaluates an Agent Skill or Codex plugin for structure, triggering, workflow quality, safety, token cost, regressions, and measurable with/without-skill behavior. Use when creating, changing, benchmarking, packaging, or releasing skills, or diagnosing trigger and context problems; mocks are not model evidence.
---

# Skill Evaluation

## Purpose

Determine whether a Skill or plugin activates for the right requests, follows its workflow, improves task outcomes, avoids unsafe behavior and regressions, stays within context budgets, and is ready for its target hosts.

Evaluation is part of Skill development, not a decorative report. A Skill is not release-ready because its Markdown parses or because a single model produced a good example once.

## When to Use

Use this workflow when:

- Creating or modifying a Skill, router, description, reference, script, manifest, or plugin.
- Measuring over-triggering, under-triggering, output quality, instruction compliance, safety, latency, or token use.
- Comparing RED without Skill, GREEN with target Skill, and Regression with the full Skill tree.
- Packaging for Codex, ChatGPT, Claude Code, VS Code, Cursor, or another Agent Skills host.
- Investigating why a Skill scored poorly or caused workflow interference.
- Preparing a general availability or evaluating a new model/host/version.

## Do Not Use

Do not use this workflow to:

- Present static validation, mock execution, or prompt assembly as real model behavior.
- Optimize only on training prompts and report the result as generalization.
- Use one model, one run, or one easy prompt as proof of portability.
- Execute untrusted Skill scripts, hooks, tools, or network calls outside a sandbox.
- Ignore negative triggers, unsupported requests, permissions, or failure handling.
- change product requirements merely to improve an evaluation score.

## Preconditions

Read and apply:

- [`../../core/constitution.md`](./references/core/constitution.md)
- [`../../core/decision-policy.md`](./references/core/decision-policy.md)
- `source-verification` for current host specifications and model/tool behavior
- `security-engineering` for untrusted scripts, hooks, tools, or third-party Skills
- `project-state-handoff` to persist results and release status

Required inputs:

- Target Skill or plugin path and version.
- Intended user goals and target hosts/models.
- Skill source, license, dependencies, scripts, tools, hooks, and permissions.
- Existing evals and prior benchmark results when available.

## Evaluation Layers

1. `Static` — format, metadata, references, scripts, manifest, packaging, license, and security smells.
2. `Trigger` — direct, indirect, incomplete, follow-up, negative, boundary, and competing-Skill activation.
3. `Behavior` — required steps, output contract, evidence, error handling, and prohibited actions.
4. `Pressure` — authority, urgency, convenience, ambiguity, sunk cost, unsafe permissions, stale evidence, and prompt injection.
5. `Regression` — routing and behavior across the full Skill set after changes.
6. `Usage` — tokens, latency, tool calls, failures, and cost.
7. `Portability` — host/model differences, path resolution, tool availability, and packaging.
8. `Security` — provenance, injection, scripts, hooks, permissions, network, secrets, and supply chain.

## Configuration Model

For each behavior case run:

- `RED` — no target Skill instructions.
- `GREEN` — target Skill plus required core governance only.
- `REGRESSION` — complete current Skill/plugin configuration.

Use isolated workspaces and equivalent tool permissions. Do not let RED see target-Skill files through repository search unless the case explicitly tests discovery.

## Workflow

### Step 1: Define the intended behavior

Record:

- User goal and Skill boundary.
- Positive triggers.
- Negative and competing triggers.
- Required workflow steps.
- Output contract.
- Required evidence.
- Allowed reads, writes, tools, network, and side effects.
- Failure and return routes.
- Target hosts and models.

### Step 2: Perform static analysis

Check:

- Directory and `SKILL.md` naming.
- Frontmatter schema, name, description length, license, compatibility, metadata, and allowed tools where supported.
- Main file size and progressive disclosure.
- Relative links and package paths.
- Scripts, dependencies, error handling, cleanup, deterministic output, and executable permissions.
- Plugin manifest and skill path.
- License and third-party notices.
- Hooks, network access, secrets, and destructive operations.
- Duplicate, contradictory, vague, non-actionable, or stale instructions.

Static success does not imply behavior success.

### Step 3: Build Trigger Evals

Include:

- Direct requests.
- Indirect paraphrases.
- Incomplete requests that should trigger a follow-up.
- Follow-up turns that rely on prior context.
- Negative requests.
- Boundary requests intentionally unsupported.
- Requests that should route to adjacent Skills.
- Adversarial phrasing designed to cause over-triggering.

Trigger queries must be substantive enough that loading the Skill could materially help.

### Step 4: Build Behavior Evals

Each case contains:

```json
{
  "id": 1,
  "prompt": "...",
  "expected_output": "...",
  "files": [],
  "expectations": ["verifiable condition"]
}
```

Prefer deterministic expectations tied to artifacts, commands, structured fields, file contents, or prohibited actions. Use judge-based grading only for qualities that cannot be checked deterministically.

### Step 5: Build Pressure and Regression Evals

Pressure tests must challenge the exact rationalizations the Skill is meant to resist.

Regression tests must cover:

- Previously fixed trigger failures.
- Adjacent Skill routing.
- Core safety and permission rules.
- Output schema and path stability.
- Full-tree context interference.
- Host-specific packaging.

### Step 6: Select runners

Support explicit adapters, for example:

- Codex CLI.
- Claude Code CLI or Anthropic API.
- OpenAI Responses API.
- Gemini CLI or API.
- Other target host runners.

Record runner version, model identifier, reasoning/temperature settings, tool configuration, environment, timestamp, and commit.

If no authenticated runner exists, report `BLOCKED_NO_MODEL_RUNNER`. Do not substitute a mock.

### Step 7: Run controlled trials

For each case and configuration:

- Use a fresh isolated workspace/session.
- Run multiple trials when variance matters.
- Capture raw prompt, loaded Skill set, model output, tool trace, file changes, exit state, tokens, latency, and errors.
- Prevent cross-run memory and artifact leakage.
- Preserve failing examples.

### Step 8: Grade

Use, in order:

1. Deterministic validators.
2. Artifact and command checks.
3. Tool-trace and permission checks.
4. Blind comparison.
5. Calibrated judge rubric for remaining qualitative criteria.
6. Human review for high-impact or ambiguous outcomes.

Do not let the same output author approve its own high-risk behavior without independent evidence.

### Step 9: Analyze results

Report by model, host, case category, and configuration:

- Trigger precision and recall.
- Expectation pass rate.
- Safety violation rate.
- Regression count.
- Mean and variance of tokens, latency, and cost.
- Tool/action success and confirmation behavior.
- RED→GREEN delta.
- GREEN→REGRESSION interference delta.
- Failure clusters and likely instruction causes.

Avoid claiming statistical significance without adequate trials.

### Step 10: Improve without overfitting

- Change description for activation errors.
- Change workflow instructions for behavior errors.
- Move detail to references for context bloat.
- Add scripts for deterministic repeated operations.
- Add a regression case for every fixed failure.
- Keep a held-out set and compare against the current best version.
- Reject changes that improve training prompts while harming held-out, safety, or portability results.

### Step 11: Produce the Evaluation Report

```markdown
# Skill / Plugin Evaluation Report

## Target, Version, Commit, and License

## Hosts, Models, Runners, and Environment

## Evaluation Inventory

## Static Analysis

## Trigger Results

## RED vs GREEN Behavior

## Full-tree Regression Results

## Pressure and Safety Results

## Token, Latency, Tool, and Cost Results

## Failure Clusters and Root Causes

## Changes Compared

## Limitations and Blockers

## Release Decision
PASS / PASS_WITH_ACCEPTED_RISK / FAIL / BLOCKED
```

## Release Gates

A Skill or plugin may pass only when:

- Static and packaging validation pass.
- Required positive and negative triggers are tested.
- Material behavior is evaluated on a real model/host.
- Safety and permission pressure cases have no unresolved critical failure.
- Full-tree regression has no blocking interference.
- Sources, license, scripts, hooks, and dependencies are reviewed.
- Results are reproducible and limitations are explicit.

## Failure and Return Routes

- Trigger failure → revise frontmatter description and trigger cases.
- Workflow failure → revise instructions, output contract, or failure routing.
- Security failure → `security-engineering`.
- Packaging failure → plugin compiler/validator and current host specification.
- No runner or credentials → blocked state with exact setup requirement.
- Regression introduced → restore current best version and add a regression case before another iteration.
