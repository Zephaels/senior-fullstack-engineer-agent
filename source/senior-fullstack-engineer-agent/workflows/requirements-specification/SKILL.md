---
name: requirements-specification
description: Converts confirmed product intent or a proposed change into precise, testable behavior specifications before architecture or coding. Use for new products, meaningful features, behavior changes, APIs, permissions, data lifecycles, multi-platform workflows, or repair of incomplete and contradictory requirements. Supports Greenfield specifications and Brownfield specification deltas. Do not use to choose implementation technologies or to invent unresolved business policy.
---

# Requirements Specification

## Purpose

Define what the system must make true, for whom, under which conditions, including success, failure, permissions, data, compatibility, platform, operational, and quality expectations. Create a contract that architecture, implementation, testing, review, and release can trace without re-interpreting product intent.

Requirements describe behavior and constraints. They do not contain implementation code or silently choose architecture.

## When to Use

Use this workflow when:

- Product intent is sufficiently understood and a testable specification is needed.
- A new feature, user workflow, API, permission, data model behavior, integration, or platform capability is proposed.
- An existing system requires a behavior change and a Brownfield delta must be made explicit.
- Requirements are vague, contradictory, incomplete, untestable, or scattered across chat, issues, code, and documentation.
- A defect reveals that expected behavior, failure semantics, or edge cases were never specified.
- Complex or Critical work needs a readiness gate before architecture or parallel implementation.

## Do Not Use

Do not use this workflow when:

- Product outcome, user, scope, or business policy remains materially unclear; route to `intent-interview`.
- Current behavior is unknown in an existing repository; run `repository-discovery` first.
- The task is only technology selection or architectural option analysis; use `architecture-design` after requirements are ready.
- A Quick Patch is fully unambiguous and affects no public behavior, data, permission, or compatibility contract.

Do not use a specification to hide unresolved decisions behind vague language such as “appropriate,” “secure,” “fast,” “user-friendly,” or “handle errors.”

## Preconditions

Read and apply:

- [`../../core/constitution.md`](./references/core/constitution.md)
- [`../../core/task-classifier.md`](./references/core/task-classifier.md)
- [`../../core/decision-policy.md`](./references/core/decision-policy.md)
- `intent-interview` when an Intent Brief exists
- `repository-discovery` for Brownfield work

Required inputs, as applicable:

- Confirmed Intent Brief or an already unambiguous task.
- Repository Discovery Report for existing systems.
- Current specifications, ADRs, API contracts, schemas, policies, and Project Ledger.
- Task class and operating mode.

## Specification Modes

Select exactly one mode:

- `Create` — define a Greenfield capability or a previously unspecified area.
- `Delta` — define added, modified, or removed behavior in an existing system.
- `Repair` — resolve gaps, contradictions, ambiguity, or missing failure semantics.
- `Review` — assess readiness without modifying the specification unless authorized.

For Brownfield changes, preserve current truth separately from proposed truth. Do not rewrite unrelated specifications.

## Normative Language

Use normative terms consistently:

- `MUST` / `SHALL` — required for acceptance.
- `MUST NOT` / `SHALL NOT` — prohibited behavior.
- `SHOULD` — recommended but an approved exception may exist.
- `MAY` — permitted optional behavior.

Every normative requirement needs at least one observable scenario, acceptance method, or explicit verification route.

## Requirement Identifiers

Use stable identifiers:

- `REQ-` — functional behavior
- `NFR-` — non-functional requirement
- `SEC-` — security or privacy requirement
- `DATA-` — data ownership, lifecycle, integrity, migration, or retention
- `ACC-` — accessibility
- `COMPAT-` — compatibility, versioning, or migration
- `OPS-` — operations, rollout, support, observability, recovery
- `NON-` — explicit non-goal
- `DEF-` — deferred behavior with owner and resolution stage

Do not renumber existing identifiers casually. Mark superseded items explicitly.

## Required Coverage by Task Class

### Q — Quick Patch

A full specification is usually unnecessary. Record:

- Exact expected behavior.
- Exact non-behavior.
- Verification criterion.

### S — Standard Change

Define:

- User or actor.
- Trigger and core behavior.
- Acceptance criteria.
- Major error and permission behavior.
- Scope and non-goals.

### C — Complex Feature

Add:

- End-to-end workflows and state transitions.
- All material unhappy paths.
- Data, access, platform, external provider, reliability, observability, rollout, and compatibility requirements.
- Requirement-to-scenario traceability.

### X — Critical Change

Add explicit semantics for:

- Authentication, authorization, tenant isolation, privacy, payment, compliance, or irreversible actions.
- Type, nullability, protocol, idempotency, concurrency, retry, timeout, cancellation, recovery, and rollback.
- Data integrity, audit, retention, deletion, migration, backup, and incident behavior.
- Performance and resilience budgets.
- Required approvals and independent verification.

An X-level specification is not ready if an implementer would need to invent public behavior, security policy, data policy, failure semantics, or irreversible decisions.

## Workflow

### Step 1: Confirm the specification boundary

Record:

- Capability or change name.
- User outcome and relevant actors.
- Greenfield or Brownfield mode.
- In-scope and out-of-scope behavior.
- Current truth and proposed delta for Brownfield work.
- Dependencies on other specifications or contracts.

If the boundary contains multiple independently acceptable capabilities, split them.

### Step 2: Consolidate source material

Collect and reconcile:

- Intent Brief and Interview Ledger.
- Repository facts and current behavior.
- Existing specifications, contracts, schemas, tickets, ADRs, policies, and tests.
- Authoritative external constraints.

Record contradictions. Do not silently prefer chat, code, test, or documentation when they disagree.

### Step 3: Define actors and permissions

For every actor or system identity, define:

- What it can initiate, read, modify, approve, cancel, export, or delete.
- What it must not access or infer.
- Ownership and tenant boundaries.
- Authentication or trust assumptions.
- Behavior when authorization changes during a workflow.

Permission checks must be observable from the trusted boundary, not only implied by UI state.

### Step 4: Define the successful workflow

Describe the shortest successful path:

1. Initial state and prerequisites.
2. Trigger or input.
3. Validation.
4. State transitions or business rules.
5. Observable result.
6. Persisted or emitted side effects.
7. Confirmation, feedback, or audit evidence.

Separate user-visible behavior from internal implementation.

### Step 5: Define alternate and failure workflows

Cover relevant cases:

- Missing, empty, invalid, duplicate, stale, conflicting, or oversized input.
- Permission denied, expired identity, revoked access, or tenant mismatch.
- Offline, timeout, partial failure, rate limit, provider failure, and retry exhaustion.
- Concurrent updates, duplicate submission, cancellation, rollback, or recovery.
- Insufficient storage, quota, funds, capacity, or dependency availability.
- Unsupported platform, browser, device, locale, or accessibility mode.
- Cleanup after interruption or abandoned workflows.

Define whether the outcome is retryable, recoverable, compensatable, or final.

### Step 6: Define state and lifecycle semantics

For meaningful entities or workflows, specify:

- States and allowed transitions.
- Who or what can cause each transition.
- Preconditions and postconditions.
- Terminal, retryable, cancelled, expired, archived, deleted, and restored states.
- Visibility and editability in each state.
- Invariants that must always hold.

Do not allow UI labels to become the only definition of business state.

### Step 7: Define data behavior

Specify:

- Data created, read, updated, deleted, exported, or shared.
- Ownership, source of truth, classification, and sensitivity.
- Required fields, optionality, validation, and uniqueness.
- Retention, deletion, archive, restore, backup, and legal hold when relevant.
- Consistency, ordering, duplicate handling, and conflict policy.
- Migration and compatibility requirements for existing data.
- What may appear in logs, metrics, traces, analytics, or model inputs.

### Step 8: Define external and public contracts

For APIs, events, SDKs, integrations, plugins, files, and public UI behavior, specify:

- Version and compatibility expectations.
- Inputs, outputs, errors, status, ordering, and pagination.
- Idempotency, retry, timeout, cancellation, and webhook behavior.
- Authentication and authorization semantics.
- Deprecation, migration, rollback, and consumer impact.

Implementation-specific encoding belongs in architecture only when it is part of the public contract.

### Step 9: Define platform and experience requirements

Specify shared product semantics and platform adaptations:

- Supported platforms, browsers, devices, windows, orientations, input methods, and assistive technologies.
- Navigation and state restoration.
- Loading, empty, error, disabled, read-only, permission, offline, sync, conflict, and success states.
- Keyboard, pointer, touch, screen reader, text scaling, localization, dark mode, and high contrast.
- Which behavior is shared, adapted, platform-only, or not applicable.

Do not require pixel identity across platforms.

### Step 10: Define quality and operational requirements

Use measurable criteria when material:

- Performance and latency budgets.
- Availability, durability, consistency, and capacity.
- Security, privacy, audit, compliance, and data residency.
- Observability, support, incident, health check, and diagnostics.
- Deployment, feature flag, rollout, rollback, and recovery.
- Cost or quota boundaries.

Avoid arbitrary numbers. Record source or owner for each budget.

### Step 11: Write acceptance scenarios

Use a clear observable format, such as:

```text
Scenario: Cancel a queued generation job
GIVEN an authorized user owns a queued job
WHEN the user cancels the job
THEN the job enters the cancelled state
AND no provider request is started
AND the UI reflects cancellation without requiring a page reload
AND an audit event records the action without sensitive payload data
```

Include positive, negative, boundary, permission, interruption, and recovery scenarios appropriate to task class.

### Step 12: Record non-goals and deferred items

Every non-goal should prevent plausible scope creep. Every deferred item must include:

- Reason for deferral.
- Owner.
- Resolution stage or date condition.
- Safe boundary that prevents implementation from inventing behavior.

### Step 13: Build traceability

Map:

- Outcome → requirements
- Requirement → scenarios
- Requirement → risks
- Requirement → architecture concern
- Requirement → planned verification

Traceability may be a table rather than a separate tool.

### Step 14: Self-audit and readiness decision

Check for:

- Ambiguous actors, pronouns, states, timing, quantities, or ownership.
- Contradictory requirements.
- Missing unhappy paths or recovery behavior.
- Hidden architecture decisions masquerading as requirements.
- Undefined permissions, data lifecycle, public semantics, or compatibility.
- Unmeasurable words without acceptance evidence.
- Requirements with no scenario or verification route.
- Scenarios with no governing requirement.
- Unapproved irreversible or Critical decisions.

## Output Contract

### Greenfield Specification

```markdown
# Requirement Specification

## Metadata and Status

## Outcome and Actors

## Scope

## Explicit Non-Goals

## Glossary

## Functional Requirements

## Business Rules and State Transitions

## Permissions and Security Requirements

## Data and Lifecycle Requirements

## Public and External Contracts

## Platform and Experience Requirements

## Non-Functional and Operational Requirements

## Acceptance Scenarios

## Compatibility, Migration, and Rollback

## Assumptions

## Deferred Items

## Risks

## Traceability Matrix

## Readiness Decision
```

### Brownfield Delta

```markdown
# Specification Delta

## Current Behavior Baseline

## ADDED Requirements

## MODIFIED Requirements

## REMOVED Requirements

## Compatibility and Migration

## Regression Boundaries

## Acceptance Scenarios

## Affected Existing Specifications

## Readiness Decision
```

## Readiness Status

Return one status:

- `draft` — material content is still being assembled.
- `needs_clarification` — product or policy decisions must return to `intent-interview`.
- `needs_repository_evidence` — current behavior or contract must return to `repository-discovery`.
- `needs_source_verification` — external or version-sensitive facts are unresolved.
- `ready_for_architecture` — product behavior is sufficiently defined.
- `approved_critical` — Critical semantics and owners are explicitly approved.
- `review_only` — findings produced without modifying the specification.

## Failure and Return Routes

- Product meaning unresolved → `intent-interview`
- Existing behavior unknown → `repository-discovery`
- External standard or API unclear → `source-verification`
- Technical option unresolved but product semantics stable → `architecture-design`
- Implementation requested before readiness → stop and report the blocking requirement gap

## Quality Gate

The specification is ready only when the next engineer can design and test the requested behavior without inventing product scope, user-visible semantics, business rules, permissions, data policy, public contracts, or Critical failure behavior.
