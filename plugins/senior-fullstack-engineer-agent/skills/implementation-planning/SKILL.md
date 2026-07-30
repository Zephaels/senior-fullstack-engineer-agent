---
name: implementation-planning
description: Converts approved requirements and architecture into dependency-ordered, vertically sliced, verifiable implementation work. Use when a feature, change, migration, or repair is ready to plan before coding, especially across multiple files, layers, platforms, services, or agents. Produces exact scope, files, contracts, tests, evidence, dependencies, rollout, and rollback for each slice. Do not use while material requirement or architecture decisions remain unresolved, and do not implement code during planning.
---

# Implementation Planning

## Purpose

Create an executable plan that lets an engineer or implementation Agent deliver the approved behavior in small, coherent, testable, reviewable, and recoverable slices without re-discovering the project or redesigning the solution.

Planning says how the approved behavior will be implemented and verified. It does not write production code, install dependencies, modify schemas, or deploy.

## When to Use

Use this workflow when:

- Requirements and architecture are ready for implementation.
- A Brownfield change spans multiple files, components, contracts, data, tests, platforms, or deployment steps.
- A migration, refactor, security fix, AI integration, performance change, or release requires sequencing and rollback.
- Work will be divided among multiple engineers or Agents.
- A previous plan is vague, uses placeholders, lacks verification, or no longer matches the repository.

## Do Not Use

Do not use this workflow when:

- Product or business decisions remain unresolved.
- Current repository facts are unknown.
- Architecture, data, security, public contracts, migration, or Critical failure semantics are not ready.
- The user only requests a conceptual estimate with no implementation plan.
- The task is a truly mechanical Quick Patch whose exact file, edit, and verification are already known.

Do not plan implementation and modify code in the same workflow.

## Preconditions

Read and apply:

- [`../../core/constitution.md`](../../core/constitution.md)
- [`../../core/task-classifier.md`](../../core/task-classifier.md)
- [`../../core/decision-policy.md`](../../core/decision-policy.md)
- [`../repository-discovery/SKILL.md`](../repository-discovery/SKILL.md) for Brownfield work
- [`../requirements-specification/SKILL.md`](../requirements-specification/SKILL.md)
- [`../architecture-design/SKILL.md`](../architecture-design/SKILL.md)

Required inputs:

- Approved requirements or specification delta.
- Architecture design and relevant ADRs.
- Fresh repository map, current revision, commands, and blast radius.
- Task class, permissions, platform scope, constraints, risks, and rollout expectations.

If any implementation task would need to decide product semantics, public contracts, security policy, data policy, or irreversible architecture, return upstream.

## Planning Principles

- Deliver vertically through the real user or system path, not layer by layer in isolation.
- Prefer the smallest independently verifiable slice.
- Keep scope explicit and prevent opportunistic refactoring.
- Use project-relative paths and existing extension points.
- Every task must include validation and completion evidence.
- Dependencies, migration, rollout, rollback, and cross-platform effects are part of the plan.
- Parallel work is allowed only when write scopes and contracts do not conflict.
- A roadmap is a current hypothesis, not a promise that later evidence cannot change.

## Plan Hierarchy

Use the smallest sufficient hierarchy:

```text
Goal
└── Roadmap or implementation phases
    └── Vertical slice
        └── Atomic tasks
```

- `Goal` — the approved outcome and Definition of Done.
- `Roadmap` — current sequence of likely slices.
- `Slice` — independently acceptable, testable, reviewable, and potentially shippable outcome.
- `Task` — a concrete modification or verification step within a slice.

Do not create a separate phase for every technical layer unless it is foundational and independently verifiable.

## Required Depth by Task Class

### Q — Quick Patch

Record:

- Exact file and edit.
- Expected behavior.
- Verification command or observation.
- Immediate rollback.

### S — Standard Change

Add:

- One or more vertical slices.
- Affected files or symbols.
- Tests and acceptance evidence.
- Dependencies and review points.

### C — Complex Feature

Add:

- Dependency graph and phase gates.
- Cross-layer and cross-platform paths.
- Contract, schema, migration, observability, documentation, feature-flag, and rollout tasks.
- Independent review and convergence steps.

### X — Critical Change

Add:

- Approval points.
- Security, privacy, data-integrity, payment, compliance, migration, backup, recovery, rollback, and incident tasks.
- Failure rehearsal and evidence requirements.
- Isolated workspaces or Agent scopes.
- Stop conditions and no-go criteria.

## Workflow

### Step 1: Verify planning readiness

Confirm:

- Requirements status is ready or approved.
- Architecture status is ready or approved.
- Repository map is fresh enough for target files and commands.
- Critical decisions, approvals, migrations, and permissions are known.
- The desired outcome and Definition of Done are stable.

If not, return to the owning stage instead of embedding an unresolved decision in a task.

### Step 2: Restate goal and Definition of Done

Summarize:

- User or system outcome.
- In-scope behavior.
- Explicit non-goals.
- Acceptance scenarios.
- Quality, security, data, platform, and operational requirements.
- What evidence proves completion.

### Step 3: Map the implementation surface

From repository and architecture evidence, identify:

- Files, symbols, modules, packages, services, routes, screens, jobs, schemas, migrations, configurations, and documentation likely to change.
- Existing extension points and reusable components.
- Contracts, types, generated clients, tests, fixtures, mocks, analytics, monitoring, and deployment files.
- Callers, dependents, consumers, and platform-specific implementations.

Mark uncertain targets as investigation tasks rather than pretending exact paths are known.

### Step 4: Define vertical slices

Each slice should traverse enough of the real path to prove a meaningful behavior, for example:

```text
UI or external trigger
→ validation and permission
→ use case or domain behavior
→ persistence/provider
→ result and feedback
→ verification evidence
```

A foundational slice is acceptable when it produces a runnable contract, schema, test harness, or migration safety mechanism required by all later slices.

Avoid plans such as “build backend, then frontend, then tests” when a thin end-to-end slice is possible.

### Step 5: Order dependencies

Create an explicit dependency graph:

- Foundation before dependent behavior.
- Contract and schema before consumers when required.
- Expand before migrate before contract for compatible migrations.
- Safety, feature flag, observability, backup, or test harness before high-risk activation.
- Verification before release.
- Cleanup only after adoption and rollback windows close.

Mark tasks that can run in parallel. Parallel tasks must have:

- Non-overlapping write scope or an agreed integration boundary.
- Frozen contracts.
- Independent validation.
- Named merge or convergence owner.

### Step 6: Write atomic tasks

Every task must specify:

- Stable task ID.
- Slice and requirement references.
- Objective.
- Exact or best-evidence file/symbol scope.
- Preconditions and dependencies.
- Concrete implementation steps.
- Interfaces, types, schemas, state, or invariants affected.
- Tests to add or update.
- Commands and expected evidence.
- Security, data, platform, performance, and observability considerations.
- Documentation or Project Ledger updates.
- Rollback or recovery point.
- Completion criteria.

Do not use placeholders such as:

- “Add appropriate error handling.”
- “Write tests.”
- “Update relevant files.”
- “Implement as discussed.”
- “Similar to the previous task.”

State the actual behavior and evidence an engineer needs.

### Step 7: Plan test and verification work

Map every material requirement to one or more of:

- Unit tests
- Integration or contract tests
- UI/E2E tests
- Permission and security tests
- Migration and rollback validation
- Failure, retry, timeout, cancellation, concurrency, and recovery tests
- Accessibility and platform tests
- Performance and capacity tests
- Observability and health checks
- Manual or human approval where automation is insufficient

Tests should be scheduled with the slice, not deferred to an undifferentiated final phase.

### Step 8: Plan migration and rollout

When relevant, include:

- Backup or snapshot.
- Expand/migrate/contract sequence.
- Data backfill and validation.
- Compatibility adapters.
- Feature flag and default state.
- Canary, staged, percentage, tenant, or platform rollout.
- Health signals and rollback trigger.
- Cleanup and deprecation.

Do not schedule an irreversible step before its recovery mechanism is verified.

### Step 9: Plan review and handoff gates

Define when to run:

- Spec or plan consistency review.
- Architecture review.
- Security review.
- Code review: specification compliance and engineering quality.
- Preflight.
- Release approval.
- Project Ledger update and handoff.

For multi-Agent execution, separate implementation and acceptance review when practical.

### Step 10: Estimate uncertainty, not false precision

Record:

- Known work.
- Investigation tasks.
- External dependencies.
- Risk drivers.
- Decisions that can change sequencing.

Use relative size or ranges when useful. Do not promise dates without capacity, dependencies, and environment information.

### Step 11: Self-review

Verify:

- Every requirement has planned implementation and verification.
- Every task traces to an approved requirement or required engineering gate.
- Tasks do not invent behavior or architecture.
- Paths and commands come from repository evidence or are marked for discovery.
- Slices are vertical and independently verifiable.
- Dependencies and parallel scopes are explicit.
- Security, data, platform, migration, observability, documentation, rollout, and rollback are not afterthoughts.
- No placeholders remain.
- The plan protects existing code and public behavior.

## Output Contract

```markdown
# Implementation Plan

## Metadata and Status

## Goal and Definition of Done

## Source Artifacts

## Scope and Non-Goals

## Repository and Revision Baseline

## Implementation Surface

## Architecture and Contract Constraints

## Roadmap

## Dependency Graph

## Vertical Slices

### Slice SLICE-001 — <Outcome>

#### Objective

#### Requirements and Scenarios

#### Preconditions and Dependencies

#### Tasks

#### Test and Evidence Plan

#### Security, Data, Platform, and Operations

#### Rollback and Recovery

#### Completion Gate

## Cross-Slice Integration

## Migration and Rollout

## Review and Approval Gates

## Documentation and Project State Updates

## Risks, Unknowns, and Investigation Tasks

## Plan Readiness Decision
```

A task uses this structure:

```yaml
task:
  id: TASK-001
  slice: SLICE-001
  requirements: [REQ-001, SEC-001]
  objective: "..."
  files:
    modify: []
    create: []
    delete: []
  dependencies: []
  steps: []
  tests: []
  commands: []
  evidence: []
  risks: []
  rollback: "..."
  done_when: []
```

## Plan Status

Return one:

- `draft`
- `blocked_requirement_gap`
- `blocked_architecture_gap`
- `blocked_repository_staleness`
- `blocked_permission`
- `ready_for_implementation`
- `approved_critical`
- `review_only`

## Failure and Return Routes

- Product or requirement gap → `requirements-specification` or `intent-interview`
- Repository path, command, or behavior uncertainty → `repository-discovery`
- Architecture, contract, data, security, or migration gap → `architecture-design`
- External version uncertainty → `source-verification`
- Implementation requested while blocked → stop and report the owning gap

## Quality Gate

The plan is ready only when an implementation engineer can execute each slice without inventing scope, architecture, contracts, failure behavior, security policy, data policy, file targets, validation, rollout, or rollback, and when every completed slice can produce fresh evidence of its acceptance.
