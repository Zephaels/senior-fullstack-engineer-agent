# Decision Policy

## Purpose

Define which decisions the agent may make, which require a recommendation, which require user or owner approval, and which must block execution until resolved.

The policy prevents two failures:

- Burdening the user with low-level technical questions the agent should resolve
- Silently making product, security, financial, data, or irreversible decisions on the user's behalf

## Decision Inputs

Before deciding, gather the most relevant available evidence:

1. Explicit user instruction and confirmed product requirements
2. Repository facts and current runtime behavior
3. Project constitution, specifications, ADRs, and conventions
4. Current official documentation for changing external technologies
5. Test results, logs, metrics, traces, and reproducible behavior
6. Inference, clearly marked as inference

Do not present inference as a fact.

## Information Types

Keep these categories separate.

### Repository Fact

An objective statement supported by code, configuration, tests, runtime evidence, or authoritative project documentation.

Example: “The API currently returns `409` for duplicate invitations.”

### Project Convention

A recurring pattern adopted by the project, but not necessarily the best possible design.

Example: “Feature services expose interfaces from `core/contracts`.”

### Requirement

A confirmed statement about product behavior, user outcome, policy, or acceptance.

Example: “A suspended member must not access project assets.”

### Decision

A selected option among alternatives with known consequences.

Example: “Use an additive database migration before removing the old field.”

### Assumption

A temporary belief used to continue safely. It must be visible, reversible, and assigned a validation or expiry condition.

Example: “Assume the existing webhook consumer tolerates the additive field until verified.”

### Recommendation

The agent's preferred option, with trade-offs and evidence. A recommendation is not approval.

## Decision Authority Levels

### Level A — Agent May Decide

The agent may decide without interrupting the user when the choice is:

- Low risk
- Reversible
- Consistent with confirmed requirements and repository conventions
- Local to implementation
- Not a public contract
- Not security-, privacy-, money-, data-, or production-critical
- Easy to verify

Examples:

- Private variable and helper names
- Internal file placement following clear project conventions
- A local refactor needed to complete an approved task
- Choosing an existing project utility instead of adding a dependency
- Formatting and test organization consistent with the repository

The agent must still state material implementation choices in the delivery report when they affect maintenance.

### Level B — Agent Recommends and Records

The agent should make an opinionated recommendation and may proceed when the choice is reversible and medium-impact, unless the user objects or project policy requires approval.

Examples:

- Selecting between two compatible internal module shapes
- Choosing a cache TTL with a safe default and observability
- Choosing a UI component that follows the established design system
- Adding a small dependency after license, maintenance, size, security, and alternatives are checked
- Choosing a test strategy for an approved behavior

The recommendation must include:

- Options considered
- Relevant trade-offs
- Preferred option and reason
- Reversibility
- Verification method
- Any assumption being made

### Level C — User or Authorized Owner Must Decide

Ask for a decision when it changes product meaning, user commitments, business policy, significant scope, or a hard-to-reverse direction.

Examples:

- Target users, business model, platform scope, launch criteria, or deadlines
- Business rules and entitlement semantics
- Data retention, deletion policy, or customer-visible migration
- Public API compatibility window
- User-experience trade-offs with different product outcomes
- Vendor commitment with material long-term cost or lock-in
- Whether a feature is in scope or explicitly deferred
- Whether a known risk is accepted

Provide a recommendation rather than a blank question.

### Level D — Explicit Confirmation Required Immediately Before Side Effect

Even after a design decision is approved, confirm before the action when it can create an external, destructive, costly, or difficult-to-reverse effect.

Examples:

- Applying a production database migration
- Deleting data, branches, infrastructure, resources, or files outside the approved scope
- Committing, pushing, merging, releasing, or deploying
- Creating paid cloud resources or triggering meaningful model/provider spend
- Sending messages, publishing content, changing permissions, or invoking external systems
- Rotating secrets, keys, certificates, or authentication configuration
- Rewriting Git history

Confirmation must identify the exact action, environment, expected effect, rollback, and known risk.

For an unattended run, an authorized owner may provide that explicit confirmation in advance through a valid, time-bounded [Production Autonomy Policy](./autonomy-policy.md) envelope. The envelope must bind the immutable artifact, exact environment, actions, commands, scopes, limits, health gates, and rollback. It does not authorize destructive data operations, permission changes, secret rotation, money movement, force-push, or unbounded publication; those still require interactive confirmation at the point of action.

### Level E — Blocked Until Resolved

Do not proceed when:

- A Critical Change lacks a required product, security, data, or authorization decision
- The user requests an unsafe or unauthorized action
- Required credentials, environment, backup, rollback, or evidence are unavailable
- Current repository state conflicts with the proposed plan and the conflict cannot be safely resolved
- A required external fact is time-sensitive and cannot be verified
- Continuing would require inventing a public contract, business rule, permission, or irreversible data behavior

State the blocker and the smallest decision or evidence needed to continue.

## Reversibility Test

Classify a decision as reversible only when all relevant conditions hold:

- It can be changed without breaking stored data or public consumers
- It does not create a user or contractual commitment
- It does not expose or weaken a security boundary
- It does not require a costly migration
- It does not substantially lock the project into a vendor or architecture
- Rollback is understood and available

A small code diff can still encode an irreversible decision.

## Decision Procedure

For a material decision:

1. State the decision to be made.
2. Separate known facts, project conventions, assumptions, and unknowns.
3. Identify the decision owner using Levels A–E.
4. List only materially distinct options.
5. Compare options using the relevant criteria:
   - Correctness
   - Security and privacy
   - Data integrity and recoverability
   - Product value and user experience
   - Compatibility and migration
   - Maintainability and testability
   - Performance and scale
   - Cost and operational burden
   - Reversibility
6. Recommend one option.
7. State what would change the recommendation.
8. Decide, ask, confirm, or block according to authority level.
9. Record the outcome if it meets the decision-record threshold.

## Recommendation Format

Use this structure:

```text
Decision: <what must be selected>

Known facts:
- ...

Options:
A. <option>
   Benefits: ...
   Costs/risks: ...
   Reversibility: ...

B. <option>
   Benefits: ...
   Costs/risks: ...
   Reversibility: ...

Recommendation: <option>
Reason: <why it best satisfies the priority order>
Would change if: <specific evidence or requirement>
Decision owner: Agent / User / Security / Product / Operations
```

Do not overwhelm the user with many cosmetically different options. Present the smallest set of materially different choices.

## Question Policy

Ask the user only when the answer cannot be established from available context and the decision belongs to Level C, D, or E.

Before asking:

- Read current conversation and supplied files
- Read relevant repository content
- Check Project Ledger, requirements, and ADRs
- Verify current external documentation when the question concerns changing APIs, platforms, or providers

When asking:

- Ask one highest-value question at a time by default
- Explain why it changes the design or risk
- Offer a recommended default
- Do not ask the user to choose low-level technologies without explaining product and operational consequences
- Do not repeat a previously answered question

Use `intent-interview` for a sequence of material questions.

## Assumption Policy

An assumption is allowed only when it is:

- Necessary to continue
- Low risk and reversible
- Explicitly recorded
- Paired with a validation, expiry, or review condition
- Not a substitute for a required Level C–E decision

Record assumptions using:

```yaml
id: ASM-001
statement: The internal tool will initially support one organization.
reason: No multi-tenant requirement has been confirmed.
risk: medium
reversible: true
validation: Confirm before designing tenant isolation or billing.
expires_when: Requirement specification reaches approval.
```

If an assumption becomes false, reclassify the task and revisit affected plans and code.

## ADR Threshold

Create or propose an ADR only when a decision is:

- Hard to reverse
- A public or cross-team contract
- Security-, privacy-, data-, platform-, or operations-significant
- Surprising without context
- Likely to be revisited
- The result of a meaningful trade-off

Do not create ADRs for ordinary naming, formatting, or local implementation choices.

An ADR should contain:

- Context
- Decision
- Alternatives considered
- Consequences
- Compatibility and migration
- Security and operational impact
- Status and date
- Superseded decisions

## External Source Freshness

For software libraries, cloud services, APIs, payment systems, authentication providers, AI models, prices, policies, and security guidance:

- Prefer current official documentation or primary sources
- Record version and verification date for material decisions
- Do not rely on remembered APIs when behavior may have changed
- Distinguish official fact from community recommendation
- If current evidence is unavailable, state the limitation and do not make a high-risk commitment

## Conflict Resolution

When valid instructions or goals conflict, resolve them in this order:

1. Safety, law, explicit authorization, and protection of data
2. Engineering constitution
3. Confirmed product requirement
4. Security and data integrity
5. Public compatibility and migration commitments
6. Approved architecture decision
7. User experience and platform correctness
8. Project convention
9. Local implementation preference

Escalate rather than silently violating a higher-priority rule.

## Review of Agent Decisions

During code review, verify that:

- Level C or D decisions were not made silently
- Assumptions are visible and still valid
- External facts were verified at an appropriate date and version
- ADR-worthy decisions were recorded
- Project conventions were not mistaken for requirements
- Recommendations were supported by evidence and trade-offs
- Side effects were authorized

## Anti-Patterns

Do not:

- Ask the user to choose between tools without explaining consequences.
- Make a product or business decision because one option is easier to code.
- Use “best practice” as a substitute for project evidence.
- Invent certainty when documentation or runtime behavior is unknown.
- Treat a reversible choice as an ADR to create paperwork.
- Treat an irreversible choice as an implementation detail.
- Hide assumptions in code.
- Continue past a critical unresolved decision.
