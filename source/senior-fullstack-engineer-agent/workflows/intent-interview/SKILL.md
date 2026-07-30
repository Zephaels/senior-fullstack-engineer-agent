---
name: intent-interview
description: Clarifies material product, requirement, business-rule, platform, data, permission, and success decisions before planning or coding. Use when a software request is underspecified, conflicting, convention-driven, or would otherwise force the agent to invent consequential requirements. Ask one high-value question at a time, resolve repository facts by reading the project, and produce a confirmed intent brief. Do not use for mechanical edits or questions already answered by available context.
---

# Intent Interview

## Purpose

Turn an ambiguous software request into a shared, actionable understanding without forcing the user through a generic questionnaire.

This workflow determines what the product or change must achieve. It does not design the detailed implementation, choose every technology, or write code.

## Governing Rules

Read and follow:

- [Engineering Constitution](../../core/constitution.md)
- [Task Classifier](../../core/task-classifier.md)
- [Decision Policy](../../core/decision-policy.md)

The interview is subordinate to the constitution and may not be used to obtain permission for unsafe behavior.

## When to Use

Use this workflow when at least one material item remains unclear:

- Relevant user or stakeholder
- Problem being solved
- Core workflow or expected outcome
- Success criteria
- Must-have scope or explicit non-goals
- Business rule or entitlement
- Platform scope or platform-specific behavior
- Persistent data, retention, ownership, or migration expectation
- Authentication, authorization, privacy, or security expectation
- Cost, operational, deployment, compliance, or reliability constraint
- Trade-off between two different product outcomes
- Hard-to-reverse or externally visible decision

Also use it when:

- The request is convention-driven, such as “build a dashboard,” “make it scalable,” or “add AI,” but the actual job is unknown.
- Different interpretations would produce materially different architectures or acceptance criteria.
- The agent notices it is silently filling in requirements before planning or coding.

## Do Not Use

Do not use this workflow when:

- The task is a mechanical, unambiguous Quick Patch.
- The user asks for an explanation rather than a project action.
- The answer is already present in the current conversation, repository, supplied files, existing requirements, ADRs, or authoritative documentation.
- The missing information is a low-risk, reversible technical detail the agent should decide under the Decision Policy.
- The task is running in a non-interactive environment and no authorized default exists. Report a blocker instead of guessing.

## Read Scope

Before asking the first question, inspect the available context that can answer questions without the user:

1. Current conversation and user-provided materials
2. Project Ledger, product brief, requirements, ADRs, and open questions
3. Repository instructions and documentation
4. Relevant code, configuration, data models, tests, and deployment files
5. Current official documentation for version-sensitive external systems

For Brownfield work, repository discovery should precede product or technical questions whose answers may already exist in code.

## Write Scope

The interview may update or produce:

- Interview Ledger
- Intent Brief
- Glossary or canonical domain terms
- Decision candidates
- Assumptions
- Open questions
- ADR proposals for genuinely hard-to-reverse choices

Do not edit application code, dependencies, infrastructure, production data, or deployment configuration during the interview.

Do not create an ADR for an ordinary reversible implementation choice.

## Interview Principles

### One high-value question at a time

Ask one question, wait for the answer, update the model, then select the next question.

A small batch is allowed only when:

- Questions are independent
- The user explicitly requests a faster batch
- The answers can be supplied compactly without causing confusion

Never dump a broad questionnaire at the user.

### Facts are investigated; decisions are asked

Use tools and repository reading to resolve facts. Ask the user for product intent, policy, preference, accepted risk, or an irreversible decision.

Examples:

- Read the code to determine the current authentication library.
- Ask the user whether invited editors may invite additional editors.
- Read deployment files to determine current environments.
- Ask the user whether the feature must support offline work.

### Include a recommendation

When a question involves a trade-off, include a recommended default and explain why. Do not make the user choose among unexplained technologies.

### Preserve the user's language

Use the user's domain terms. When a term is ambiguous, propose a canonical definition and record it after confirmation.

### Do not repeat answered questions

Before every question, check conversation history and the Interview Ledger. If the user has already answered, use the answer or ask only about a genuine contradiction.

### Surface contradictions

If a new answer conflicts with an earlier requirement, decision, or repository fact:

1. Show the conflict precisely.
2. Explain the impact.
3. Ask which statement should govern.
4. Mark the superseded item after confirmation.

Do not silently choose the most recent answer.

## Information Model

Track interview items with stable identifiers.

| Prefix | Type | Example |
|---|---|---|
| `OBJ-` | Outcome | Reduce manual video assembly time |
| `USR-` | User or stakeholder | Internal creative operations team |
| `FLOW-` | User workflow | Script upload to reviewed export |
| `REQ-` | Confirmed requirement | A job can be cancelled |
| `NON-` | Non-goal | No public self-service signup in v1 |
| `SUCCESS-` | Success criterion | 80% of jobs complete without manual repair |
| `DEC-` | Confirmed decision | Use third-party generation providers |
| `ASM-` | Assumption | Single organization in initial release |
| `OQ-` | Open question | Required retention period |
| `RSK-` | Risk | Provider cost spikes |
| `TERM-` | Canonical term | “Project” means one creative production workspace |

Each item should include status, source, affected artifacts, and last verification date when persisted.

## Workflow

### Step 0: Establish the current task state

Record:

- User's original request
- Current best interpretation
- Task class and mode, if known
- Facts already established
- Material unknowns
- Whether the request is blocked without user input

Do not present a fake precision percentage. Explain what is known and what remains consequentially unknown.

### Step 1: Build an information-gap map

Evaluate these categories:

1. Outcome — what must become better or possible?
2. User — who performs or benefits from the workflow?
3. Trigger — when and why is the workflow used?
4. Core flow — what is the shortest successful path?
5. Success — how will completion or quality be judged?
6. Scope — what is mandatory now?
7. Non-goals — what must not be built or changed?
8. Business rules — what policies govern behavior?
9. Data — what is created, stored, owned, retained, or deleted?
10. Access — who can see or change what?
11. Platform — which platforms and platform-specific capabilities matter?
12. Operations — scale, reliability, support, observability, rollout, and rollback
13. Constraints — budget, schedule, compliance, providers, legacy systems
14. Risk — security, privacy, money, irreversible actions, or vendor dependence

Do not ask about every category. Ask only the next question that most changes the solution or removes the largest risk.

### Step 2: Select the next question

Prioritize questions using this order:

1. Safety, authorization, privacy, money, and irreversible consequences
2. Product outcome and target user
3. Business rules and permissions
4. Scope and non-goals
5. Success criteria
6. Data ownership and lifecycle
7. Platform behavior and operational constraints
8. Reversible implementation preference

If a lower-priority answer depends on a higher-priority decision, ask the higher-priority question first.

### Step 3: Ask using the standard question contract

Use this structure:

```text
Question <ID>: <one concise question>

Current understanding:
<what is already known>

Why it matters:
<what product, architecture, data, security, UX, or release decision changes>

Recommendation:
<safe and opinionated default, when appropriate>

Answer with:
<the smallest useful format: one sentence, choice, number, or bullets>
```

Keep the visible question concise. The supporting explanation should be specific, not generic.

### Step 4: Update the Interview Ledger

After each answer:

- Add or update confirmed requirements
- Record canonical terms
- Record assumptions and validation conditions
- Record decisions and their owner
- Mark contradictions and superseded items
- Update remaining material unknowns
- Reclassify the task if risk changed

Do not wait until the end to remember decisions only in chat history.

### Step 5: Test shared understanding

Before stopping, verify that the agent can accurately state:

- What outcome is being pursued
- Who the relevant user is
- The core successful workflow
- What is in and out of scope
- How success is judged
- The material business, data, access, platform, and operational constraints
- Which assumptions remain
- Which questions are deferred and where they will be resolved

For a Complex or Critical task, also verify that a future engineer could write a testable specification without re-interviewing the user about the same product decisions.

### Step 6: Request confirmation of the intent brief

Present a compact intent brief and ask the user to confirm or correct it.

Do not treat “whatever you think,” silence, or an unrelated reply as confirmation for a Critical Change. Use the Decision Policy to determine whether a safe default is allowed.

## Stop Conditions

Stop the interview when all conditions required by task class are met.

### Q — Quick Patch

No interview is normally needed. Stop when objective, exact edit, and verification are unambiguous.

### S — Standard Change

Stop when:

- User outcome and relevant user are clear
- Core behavior and acceptance are clear
- Scope and major non-goals are clear
- No unresolved material business, permission, data, or compatibility decision remains

### C — Complex Feature

Stop when:

- All Standard conditions are met
- Core workflow and failure outcomes are clear
- Data, access, platforms, external providers, reliability, and rollout constraints are sufficiently defined
- Remaining assumptions are reversible and recorded
- Open technical questions can be resolved during architecture without changing product meaning

### X — Critical Change

Stop only when:

- All Complex conditions are met
- Decision owners are identified
- Security, privacy, payment, data, compliance, or irreversible semantics are explicitly confirmed
- No critical public behavior or failure rule must be invented by implementation
- Required approval and side-effect confirmation points are known

The interview may stop with deferred items only when each item has an owner, resolution stage, and safe boundary preventing premature implementation.

## Output Contract

Produce an Intent Brief using this structure:

```markdown
# Intent Brief

## Outcome

## Relevant Users and Stakeholders

## Problem and Why Now

## Core Successful Workflow

## Must-Have Scope

## Explicit Non-Goals

## Success Criteria

## Business Rules

## Data and Ownership

## Access and Security Expectations

## Platforms and Experience Constraints

## Operational Constraints

## Confirmed Decisions

## Assumptions

## Deferred Questions

## Risks

## Classification Update

## Confirmation
```

Also produce or update an Interview Ledger:

```yaml
interview:
  status: confirmed
  task_class: C-G
  outcome: OBJ-001
  confirmed_items:
    - REQ-001
    - REQ-002
    - NON-001
  decisions:
    - DEC-001
  assumptions:
    - ASM-001
  open_questions:
    - OQ-003
  next_workflow: requirements-specification
```

## Handoff Rules

After confirmation:

- Route product alternatives to product discovery only when direction remains open.
- Route confirmed behavior to requirement specification.
- Route Brownfield technical facts to repository discovery and change-delta analysis.
- Route hard-to-reverse technical trade-offs to architecture and ADR work.
- Route implementation only after required specification and design gates pass.

The downstream workflow must use the confirmed intent, not the user's original ambiguous wording.

## User Declines Further Questions

If the user asks to continue without more questions:

1. Respect the request for low-risk, reversible details.
2. Record assumptions explicitly.
3. Choose safe defaults consistent with the repository.
4. Reduce scope rather than inventing consequential behavior.
5. Block only the decisions that the Decision Policy does not permit the agent to make.
6. State the effect of unresolved items on confidence, testing, or release.

Do not use refusal to answer as permission to make a Critical Change decision.

## Examples

### Greenfield example

User: “Build an automated AI video platform.”

First useful question:

```text
Question USR-001: Who completes the primary workflow in v1?

Current understanding:
The system should automate video production, but the operating user is not yet clear.

Why it matters:
An internal operations tool, a creator SaaS, and an enterprise approval platform require different permissions, workflows, UX, billing, and deployment.

Recommendation:
Start with one primary user group for v1 and treat other groups as explicit non-goals.

Answer with:
One user group and the job they need to complete.
```

Do not begin by asking which frontend framework the user prefers.

### Brownfield example

User: “Add an editor role.”

Before asking product questions, read the existing role model, authorization checks, tenant boundaries, tests, and API contracts.

Then ask the unresolved policy question:

```text
Question SEC-001: May an editor invite or promote other members?

Why it matters:
This changes the authorization model and tenant security boundary, not only the UI.

Recommendation:
Editors should not manage membership unless that is an explicit product requirement.
```

## Anti-Patterns

Do not:

- Ask every possible discovery question regardless of relevance.
- Ask the user for package names, file paths, or current behavior that the repository can reveal.
- Ask multiple dependent questions in one message.
- Hide the recommendation to appear neutral.
- Lead the user toward a technically convenient answer.
- Convert an assumption into a confirmed requirement.
- Continue interviewing after the required decisions are complete.
- Stop while a Critical Change still requires invented security, data, or financial behavior.
- Write application code during the interview.
- Repeat questions already answered in conversation or project artifacts.
