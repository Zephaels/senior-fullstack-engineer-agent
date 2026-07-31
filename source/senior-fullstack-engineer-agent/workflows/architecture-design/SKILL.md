---
name: architecture-design
description: Produces or reviews evidence-based software architecture after requirements and repository context are ready. Use for system boundaries, module design, APIs, data, state, security, reliability, deployment, platform adaptation, migrations, major technology choices, or architecture deltas in existing systems. Do not use to compensate for unresolved product requirements, to force fashionable patterns, or to generate implementation code.
---

# Architecture Design

## Purpose

Translate approved product behavior and verified project constraints into a coherent technical design that is correct, secure, maintainable, testable, operable, evolvable, and appropriate for the actual scale and platforms.

Architecture defines boundaries, responsibilities, contracts, data and state flows, failure semantics, operational behavior, and consequential decisions. It is not a framework shopping list or speculative diagram.

## When to Use

Use this workflow when:

- A Greenfield product or meaningful capability has requirements ready for technical design.
- A Brownfield change affects module boundaries, contracts, data, security, concurrency, deployment, platform behavior, or multiple components.
- A public API, database schema, authentication model, integration, event flow, background job, AI workflow, or infrastructure change needs design.
- Competing technical options require explicit trade-off analysis.
- An architecture review, repair, or delta is needed before implementation.
- Complex or Critical work requires ADRs, migration, rollback, or independent review.

## Do Not Use

Do not use this workflow when:

- Product behavior, permissions, data ownership, or Critical failure semantics remain unresolved.
- Current Brownfield architecture or behavior has not been discovered.
- The task is a local implementation detail with no meaningful boundary or contract impact.
- The goal is to justify a preferred framework, microservices, event sourcing, AI Agent, or cloud service without evidence.

Architecture must not silently expand product scope.

## Preconditions

Read and apply:

- [`../../core/constitution.md`](./references/core/constitution.md)
- [`../../core/task-classifier.md`](./references/core/task-classifier.md)
- [`../../core/decision-policy.md`](./references/core/decision-policy.md)
- `requirements-specification`
- `repository-discovery` for Brownfield work

Required inputs:

- Requirement Specification or approved Specification Delta.
- Repository Discovery Report for existing systems.
- Governing constraints, Project Ledger, ADRs, and source-verification records.
- Task class and platform scope.

If architecture would need to invent user-visible behavior or Critical policy, return to requirements.

## Architecture Modes

Select one:

- `Create` — design a new system or bounded capability.
- `Delta` — design the smallest architecture change for an existing system.
- `Review` — evaluate an architecture without implementing fixes.
- `Options` — compare alternatives for a consequential decision.
- `Repair` — resolve a verified architecture gap or contradiction.

## Core Boundaries

Prefer these conceptual layers when they fit the project:

- `Core` — domain models, business rules, invariants, shared state, service contracts, security semantics.
- `Features` — user capabilities, use cases, orchestration, workflows.
- `DesignSystem` — semantic tokens, UI primitives, accessibility behavior, platform-neutral design language.
- `Platform` — platform-specific UI, input, operating-system integration, lifecycle, packaging.
- `Infrastructure` — database, network, storage, cache, queues, model providers, cloud and external services.

Do not force these names into a repository that uses different but coherent boundaries. Preserve project conventions unless change is justified and approved.

## Decision Principles

Prioritize:

1. Correctness
2. Security and privacy
3. Architecture quality and integrity
4. User and platform experience
5. Maintainability and testability
6. Performance and operability
7. Development speed and code volume

Prefer:

- Simple designs that satisfy known requirements.
- Modular monoliths before speculative service decomposition.
- Stable contracts and replaceable infrastructure boundaries.
- Explicit data ownership and trusted authorization boundaries.
- Incremental migration over big-bang replacement.
- Platform-native experiences over mechanical UI reuse.
- Existing mature dependencies over custom infrastructure when justified.

## Workflow

### Step 1: Confirm architecture scope and readiness

Record:

- Requirements and scenarios in scope.
- Greenfield or Brownfield mode.
- Current architecture baseline and approved delta.
- Platforms, environments, scale, compliance, cost, team, schedule, and operational constraints.
- Decisions architecture may make under the Decision Policy.
- Decisions requiring user or owner approval.

Return upstream if behavior, permission, data policy, or Critical semantics remain unresolved.

### Step 2: Define system context and trust boundaries

Identify:

- Users, operators, administrators, services, providers, devices, and external systems.
- System boundary and data ownership.
- Trust zones, authentication sources, authorization enforcement points, tenant isolation, secrets, and sensitive data.
- Inputs, outputs, external writes, payment, deletion, publication, or irreversible effects.

For AI systems, also define model providers, tool permissions, human confirmation boundaries, model-output validation, timeout, retry, cancellation, fallback, cost, and data exposure.

### Step 3: Derive architecture drivers

Extract from requirements:

- Functional drivers.
- Security, privacy, compliance, and audit drivers.
- Data integrity, consistency, retention, backup, and migration drivers.
- Performance, capacity, latency, availability, durability, and resilience drivers.
- Platform, accessibility, localization, offline, and synchronization drivers.
- Deployment, observability, support, incident, and rollback drivers.
- Team, delivery, dependency, license, and cost constraints.

Rank drivers by consequence. Do not optimize every dimension equally.

### Step 4: Evaluate relevant options

For consequential choices, compare at least the current/default approach and viable alternatives.

Use a decision table:

| Option | Requirement fit | Security | Complexity | Migration | Operations | Cost | Reversibility | Risks |
|---|---|---|---|---|---|---|---|---|

Avoid fake precision. Explain evidence and uncertainty.

Do not compare options when the existing project already has a suitable extension point and no material reason to replace it.

### Step 5: Define components and responsibilities

For each component or module, specify:

- Responsibility and owned invariants.
- Inputs, outputs, dependencies, and prohibited dependencies.
- Data owned or accessed.
- Trusted and untrusted boundaries.
- Lifecycle, scaling, failure, and test seams.
- Shared versus platform-specific behavior.

Prevent cyclic responsibilities and hidden global state.

### Step 6: Define end-to-end data and state flow

Trace important paths through:

1. Input or event
2. Validation
3. Authentication and authorization
4. Use case or orchestration
5. Domain state transition
6. Persistence, cache, queue, model, or provider
7. Result and side effects
8. Error, retry, timeout, cancellation, compensation, recovery, and cleanup
9. Logs, metrics, traces, and audit

Define source of truth, consistency, ordering, concurrency, idempotency, and conflict handling.

### Step 7: Define interfaces and contracts

For module, API, event, SDK, CLI, file, and external provider boundaries, define:

- Purpose and owner.
- Input/output types and nullability when contractually relevant.
- Validation and authorization.
- Errors and status semantics.
- Versioning and compatibility.
- Idempotency, retry, timeout, cancellation, ordering, and pagination.
- Observability and redaction.
- Consumer migration and deprecation.

Keep infrastructure details behind interfaces when they are expected to vary.

### Step 8: Define data architecture

Specify:

- Entities, relationships, constraints, identifiers, timestamps, and lifecycle.
- Ownership and tenant boundaries.
- Indexes and query access patterns.
- Transactions, locks, consistency, isolation, and concurrency.
- Cache strategy and invalidation.
- Queue/event delivery semantics.
- Retention, archive, deletion, export, backup, restore, and audit.
- Migration, backfill, compatibility, validation, and rollback.

Do not use a new datastore without a demonstrated requirement and operational owner.

### Step 9: Define security and privacy architecture

Specify:

- Threat actors and valuable assets.
- Authentication and session model.
- Server-side authorization and object ownership checks.
- Input, upload, path, query, deserialization, and output validation.
- Secret management and key rotation.
- Encryption and transport protection.
- Tenant isolation and least privilege.
- Audit, logging, redaction, retention, deletion, and privacy boundaries.
- Dependency and supply-chain controls.
- Abuse, rate limit, fraud, payment, and administrative controls when relevant.

Route high-risk work to `security-engineering` when available; architecture remains responsible for the baseline.

### Step 10: Define platform architecture

Classify each capability as:

- `Shared`
- `Adapted`
- `Platform Only`
- `Not Applicable`

Define platform boundaries for Web, mobile, tablet, desktop, wearable, or other targets. Preserve shared business rules and data semantics while allowing navigation, windowing, input, information density, system integrations, and lifecycle to adapt.

Do not enlarge a phone UI for tablet or compress a desktop workflow into a mobile layout.

### Step 11: Define reliability and operational architecture

Specify:

- Failure domains and dependencies.
- Health checks and readiness.
- Timeout, retry, backoff, circuit breaking, load shedding, and cancellation.
- Queue and job recovery.
- Feature flags and progressive rollout.
- Logging, metrics, traces, SLI/SLO, alerting, and dashboards.
- Backup, restore, disaster recovery, incident, and runbook requirements.
- Capacity and cost controls.

Alerts should describe actionable symptoms, not merely internal events.

### Step 12: Define deployment and environment model

Specify:

- Development, testing, staging, and production separation.
- Configuration and secret injection.
- Build artifacts and reproducibility.
- CI/CD gates.
- Infrastructure and permissions.
- Database or data migration order.
- Preview, canary, blue-green, phased, or flag rollout as applicable.
- Health validation and rollback.

Deployment or infrastructure execution is not part of architecture design unless separately authorized.

### Step 13: Define migration and rollback

For Brownfield changes, include:

- Compatibility window.
- Expand/migrate/contract or equivalent sequence.
- Data backfill and validation.
- Dual-read, dual-write, adapters, or version bridges when justified.
- Consumer migration.
- Rollback trigger, safe point, and irreversible boundary.
- Cleanup and deprecation date conditions.

A migration is incomplete without evidence and recovery strategy.

### Step 14: Record ADRs

Create an ADR only for consequential, cross-cutting, hard-to-reverse, public, security, data, operational, or long-lived decisions.

Each ADR includes:

- Context
- Decision
- Status
- Drivers
- Alternatives considered
- Consequences
- Risks
- Reversibility
- Migration and rollback
- Evidence and date
- Owner or approver when required

Do not create ADRs for ordinary local choices.

### Step 15: Define validation architecture

Map each architecture driver to validation:

- Contract tests
- Unit and integration tests
- End-to-end scenarios
- Security and permission tests
- Migration and rollback rehearsal
- Performance and capacity tests
- Failure injection or recovery tests
- Accessibility and platform validation
- Observability and health checks

Architecture is not ready when critical claims have no validation route.

### Step 16: Self-review

Check:

- Requirement coverage and traceability.
- No product behavior was invented.
- Existing extension points were preferred when suitable.
- Boundaries, ownership, state, data, errors, security, platforms, and operations are explicit.
- Complexity matches actual scale and risk.
- Public contracts, migrations, and rollback are covered.
- Assumptions and unknowns are visible.
- The implementation planner can create slices without redesigning the system.

## Output Contract

```markdown
# Architecture Design

## Metadata and Status

## Scope and Requirements Traceability

## Current Architecture Baseline

## Architecture Drivers and Constraints

## System Context and Trust Boundaries

## Options and Trade-offs

## Selected Architecture

## Components and Responsibilities

## End-to-End Data and State Flows

## Interfaces and Contracts

## Data Architecture

## Security and Privacy Architecture

## Platform Architecture

## Reliability, Performance, and Operations

## Deployment and Environments

## Migration, Compatibility, and Rollback

## Observability and Incident Readiness

## Test and Validation Architecture

## ADRs

## Assumptions and Unknowns

## Risks

## Readiness Decision
```

For Brownfield work, make the delta explicit:

- Unchanged architecture
- Added components or boundaries
- Modified contracts or data
- Removed or deprecated behavior
- Migration and regression impact

## Readiness Status

Return one:

- `draft`
- `needs_requirement_clarification`
- `needs_repository_evidence`
- `needs_source_verification`
- `needs_security_review`
- `needs_owner_decision`
- `ready_for_planning`
- `approved_critical`
- `review_only`

## Failure and Return Routes

- Product or behavior ambiguity → `requirements-specification` or `intent-interview`
- Current implementation uncertainty → `repository-discovery`
- External technology or API uncertainty → `source-verification`
- Plan requested before design is ready → stop and report the unresolved architecture decisions

## Quality Gate

Architecture is ready only when a competent implementation team can divide the work without inventing component ownership, public contracts, data semantics, security boundaries, platform responsibilities, failure behavior, migration, or operational strategy.
