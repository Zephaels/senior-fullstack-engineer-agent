---
name: product-discovery
description: Determines whether a proposed product or feature solves the right user problem before requirements are fixed. Use when users, outcomes, opportunities, value, usability, feasibility, viability, metrics, non-goals, or risky assumptions are unclear; not for implementation planning.
---

# Product Discovery

## Purpose

Turn a solution-shaped request into an evidence-aware product decision. Establish the user problem, desired outcome, opportunity, alternatives, assumptions, experiments, success signals, and explicit non-goals before the workflow commits to requirements or implementation.

Product discovery decides **whether and why** a capability should exist. It does not write production code, choose detailed architecture, or treat stakeholder enthusiasm as evidence.

## When to Use

Use this workflow when:

- A user proposes an app, platform, feature, workflow, AI capability, redesign, or major change without a validated problem statement.
- The target user, use context, desired outcome, or success metric is unclear.
- Multiple opportunities or solution directions compete for scope.
- A feature request may be a symptom rather than the underlying problem.
- Value, usability, feasibility, viability, go-to-market, compliance, trust, or operational assumptions could invalidate the idea.
- The team needs a low-cost experiment before committing to full engineering.
- A roadmap or backlog is feature-led and needs to be reframed around outcomes and opportunities.

## Do Not Use

Do not use this workflow to:

- Ask questions answerable from the repository, logs, analytics already provided, or authoritative documentation.
- Convert an already approved Product Brief into formal requirements; use `requirements-specification`.
- Design system architecture, APIs, schemas, or implementation tasks.
- Generate unlimited ideas without a decision, outcome, or evidence plan.
- Invent user research, market evidence, metrics, or customer quotes.
- Override an explicit user decision merely because another solution is aesthetically preferable.

## Preconditions

Read and apply:

- [`../../core/constitution.md`](../../core/constitution.md)
- [`../../core/task-classifier.md`](../../core/task-classifier.md)
- [`../../core/decision-policy.md`](../../core/decision-policy.md)
- [`../intent-interview/SKILL.md`](../intent-interview/SKILL.md) when material product decisions require user input
- [`../repository-discovery/SKILL.md`](../repository-discovery/SKILL.md) for an existing product or codebase
- [`../source-verification/SKILL.md`](../source-verification/SKILL.md) when external market, platform, legal, pricing, or technology facts affect the decision

Inputs may include:

- Initial idea, stakeholder request, customer feedback, research, analytics, support tickets, business goals, constraints, and current product behavior.
- Existing Product Brief, roadmap, backlog, metrics, experiments, or previous decisions.
- Task class and operating mode.

## Discovery Principles

- Start from the desired user or business outcome, not the proposed feature.
- Prioritize opportunities and problems before selecting solutions.
- Separate evidence, inference, assumption, preference, and decision.
- Generate alternatives before committing to the first idea.
- Treat value, usability, feasibility, and viability as independent risks.
- Prefer the cheapest reliable evidence that can change a decision.
- Do not build an experiment whose cost approaches the full product.
- Record non-goals to prevent discovery from becoming unbounded ideation.
- Discovery may invalidate, shrink, sequence, or defer the original request.
- A decision can be “do not build yet” when evidence is insufficient or the opportunity is weak.

## Required Depth by Task Class

### Q — Quick Patch

Usually do not activate product discovery. Use only when a supposedly trivial change alters user meaning, policy, billing, permissions, or a public workflow.

### S — Standard Change

Establish:

- Target user and context.
- Problem and desired outcome.
- One measurable success signal.
- Core assumption and explicit non-goals.
- Why the proposed solution is preferable to doing nothing or using the current workflow.

### C — Complex Feature

Add:

- Opportunity map.
- At least three materially different solution directions when alternatives exist.
- Value, usability, feasibility, and viability assumptions.
- Evidence inventory and confidence labels.
- Experiment plan and decision thresholds.
- Dependency, platform, trust, adoption, support, and operational risks.

### X — Critical Change

Add:

- Stakeholder and user-segment conflicts.
- Safety, compliance, payment, privacy, abuse, fairness, and irreversible-risk analysis.
- Independent review of assumptions and experiment ethics.
- No-go conditions, escalation owners, and formal approval before requirements begin.

## Workflow

### Step 1: Establish current evidence

Collect and label:

- Direct user statements.
- Existing product behavior and repository facts.
- Customer research, support, sales, analytics, and operational evidence.
- Authoritative external sources.
- Inferences and assumptions.
- Unknowns and stale information.

Do not fabricate evidence to make the discovery appear complete.

### Step 2: Define one desired outcome

Write a concise outcome statement:

```text
For [target user] in [context], improve [observable outcome]
from [current state] toward [desired state], while preserving [critical constraint].
```

The outcome must not name the proposed feature unless the feature itself is externally mandated.

### Step 3: Define the target user and context

Specify:

- Primary user or actor.
- Triggering situation.
- Current task or workaround.
- Frequency, urgency, and consequence.
- Access, device, environment, ability, language, and trust constraints.
- Distinction between buyer, administrator, operator, subject, and end user when relevant.

Avoid broad labels such as “everyone,” “creators,” or “businesses” without a concrete job and context.

### Step 4: Map the current journey and pain

Describe:

- Current workflow.
- Friction, failure, delay, risk, or unmet need.
- Existing alternatives and why they are insufficient.
- Evidence that the problem is material.
- What happens if nothing changes.

Do not accept “users want feature X” as a complete problem statement.

### Step 5: Build the opportunity map

For one desired outcome, identify customer or operator opportunities as needs, pains, constraints, or unresolved jobs.

Prioritize opportunities using evidence, consequence, frequency, reach, strategic fit, and uncertainty. Focus on a small number of high-value opportunities rather than covering every complaint.

### Step 6: Generate and compare solution directions

When a real choice exists, produce at least three materially different directions, including the current/default option.

For each direction, compare:

- Outcome fit.
- User effort and usability.
- Feasibility and dependency risk.
- Viability, support, cost, and operations.
- Security, privacy, trust, accessibility, and platform fit.
- Reversibility and learning value.

Do not use fake numerical precision. Explain the evidence and uncertainty behind the recommendation.

### Step 7: Identify assumptions

Create an assumption register with stable IDs:

| ID | Category | Assumption | Evidence | Risk if false | Validation method | Owner |
|---|---|---|---|---|---|---|

At minimum consider:

- Value — users care enough to change behavior.
- Usability — users can understand and complete the workflow.
- Feasibility — the system, team, providers, and platforms can support it.
- Viability — business, legal, support, cost, policy, and operations can sustain it.

For AI features also consider model quality, latency, cost, data exposure, tool permissions, fallback, human confirmation, and output validation.

### Step 8: Prioritize assumptions

Prioritize by consequence and uncertainty. Test the assumptions that could invalidate the product direction before optimizing minor details.

A high-risk assumption is not resolved by confidence, authority, popularity, or a polished prototype.

### Step 9: Design the smallest useful experiment

For each critical assumption, define:

- Hypothesis.
- Target participants or environment.
- Method.
- Required data and privacy constraints.
- Success, failure, and inconclusive thresholds.
- Duration or sample sufficiency.
- Cost and operational impact.
- Decision that follows each outcome.

Prefer prototypes, concierge tests, fake-door tests with appropriate disclosure, workflow simulation, technical spikes, or limited pilots when they are safer and cheaper than production implementation.

Do not run deceptive, destructive, discriminatory, privacy-invasive, or production-risk experiments.

### Step 10: Define success and guardrail metrics

Specify:

- Primary outcome metric.
- Leading indicators.
- Quality, safety, trust, accessibility, support, cost, and performance guardrails.
- Baseline and measurement window when evidence exists.
- What result would cause continuation, revision, rollback, or abandonment.

Metrics must connect to user or business value, not merely feature usage.

### Step 11: Define scope and non-goals

Record:

- Discovery conclusion.
- Recommended direction.
- Must-have outcome.
- Deferred opportunities.
- Explicit non-goals.
- Assumptions still unresolved.
- Decisions requiring user or stakeholder approval.

### Step 12: Produce the Product Brief

Use this output contract:

```markdown
# Product Brief

## Decision Status
Proceed / Experiment First / Revise / Defer / Do Not Build

## Desired Outcome

## Target Users and Context

## Current Journey and Problem

## Evidence Inventory

## Prioritized Opportunities

## Solution Directions and Trade-offs

## Assumption Register

## Experiment Plan

## Success and Guardrail Metrics

## Recommended Scope

## Non-goals

## Risks and Open Questions

## Downstream Requirements Inputs
```

## Quality Gates

Pass only when:

- The desired outcome is distinct from the proposed feature.
- Target users and context are concrete.
- Evidence, inference, assumptions, and decisions are separated.
- Alternatives were considered when a consequential choice exists.
- Critical assumptions and validation methods are explicit.
- Success and guardrail metrics are meaningful.
- Scope and non-goals are bounded.
- The recommendation is supported by evidence or explicitly labeled as provisional.

## Failure and Return Routes

- Missing product decision → `intent-interview`.
- Existing behavior unknown → `repository-discovery`.
- External fact or current platform behavior uncertain → `source-verification`.
- Product direction approved → `requirements-specification`.
- Technical feasibility is the only unknown → create a bounded spike through `implementation-planning`, not a production feature.

## Evidence Requirements

Do not claim validated demand, user preference, market size, experiment success, or metric improvement without a supplied or authoritative source. Record source, date, sample, limitations, and freshness.
