---
name: repository-discovery
description: Builds a verified, read-only map of an existing software repository before modification, review, debugging, migration, or planning. Use when a task targets an existing codebase, when architecture or behavior is unfamiliar, when blast radius is uncertain, or when project commands, dependencies, data flows, permissions, tests, deployment, and platform impact must be established. Do not use as a substitute for product clarification or to rewrite the repository.
---

# Repository Discovery

## Purpose

Establish a trustworthy model of an existing project before proposing architecture or changing code. Produce a compact but sufficient repository map that separates observed facts, established conventions, inferred relationships, recommendations, and unresolved unknowns.

This workflow is read-only by default. It discovers how the system actually works; it does not redesign the system while reading it.

## When to Use

Use this workflow when:

- Adding or changing a meaningful feature in an existing repository.
- Fixing a defect, regression, build failure, incident, or performance problem.
- Reviewing architecture, security, testing, accessibility, deployment, or code quality.
- Planning a migration, dependency upgrade, schema change, authentication change, or platform adaptation.
- The relevant entry point, caller, dependency, current behavior, test command, or deployment path is uncertain.
- A prior repository map may be stale because code, dependencies, configuration, or environments changed.

For a trivial Quick Patch, use the minimal discovery profile, but still identify the target file, its callers or consumers, the verification command, and any public behavior affected.

## Do Not Use

Do not use this workflow when:

- The task is genuinely Greenfield and no implementation or repository exists.
- The user asks only for a conceptual explanation unrelated to a project.
- A fresh repository map already covers the exact target and the current Git state, dependencies, and relevant files have not changed.
- The actual blocker is an unresolved product decision; route to `intent-interview` instead.

Do not use discovery as permission to browse unrelated private files, secrets, user data, build artifacts, or generated vendor directories.

## Preconditions

Read and apply:

- [`../../core/constitution.md`](../../core/constitution.md)
- [`../../core/task-classifier.md`](../../core/task-classifier.md)
- [`../../core/decision-policy.md`](../../core/decision-policy.md)

Required inputs:

- Repository root or a clearly scoped project directory.
- User request and desired outcome.
- Current task class and mode, when already known.
- Existing Project Ledger or prior handoff, when available.

If the repository cannot be accessed, report the missing access and provide the minimum information needed to proceed. Do not invent its structure.

## Read and Write Scope

### Allowed by default

- Read project instructions, source, tests, configuration, manifests, schemas, migrations, CI, deployment, and documentation.
- Run non-mutating discovery commands such as directory listings, searches, version queries, dependency inspection, static analysis, and test-listing commands.
- Run established build or test commands only when the task and environment permit it and they do not mutate external systems.

### Not allowed during discovery without separate authorization

- Editing application code or configuration.
- Installing or upgrading dependencies.
- Running migrations, seeders, destructive scripts, deploys, or external writes.
- Reading secret values, production data, unrelated user files, or credentials.
- Deleting generated files merely to make the project cleaner.

The workflow may write only its discovery artifacts when the project permits documentation updates. Otherwise return the report in the response or runtime state.

## Evidence Labels

Label every material statement as one of:

- `Fact` — directly observed in code, configuration, tests, command output, or authoritative project documentation.
- `Convention` — a repeated project pattern that appears intentional and current.
- `Inference` — a reasoned relationship not yet directly proven.
- `Recommendation` — proposed improvement, not current project truth.
- `Unknown` — consequential information not established.
- `Stale` — prior information that requires re-verification.

Never convert a convention into a recommendation without evaluation. Never present an inference as a fact.

## Discovery Profiles

### Q — Minimal

Identify:

- Exact target file or symbol.
- Relevant caller or consumer.
- Existing test or verification command.
- Public behavior or contract affected.
- Immediate risk and rollback path.

### S — Standard

Add:

- Project entry points and commands.
- Module and dependency context around the target.
- Current behavior baseline.
- Relevant tests, data, permissions, API, and platform impact.
- Local blast radius.

### C — Comprehensive

Add:

- System boundaries and major data flows.
- Authentication, authorization, trust boundaries, queues, cache, external providers, deployment, observability, migration, and rollback mechanisms.
- Cross-platform and cross-service impact.
- Repository-wide constraints relevant to the feature.

### X — Critical

Add:

- Security and privacy boundaries.
- Data classification and retention.
- Public and partner contracts.
- Failure, retry, timeout, cancellation, idempotency, recovery, and concurrency semantics.
- Production rollout, backup, incident, compliance, and independent review requirements.

## Workflow

### Step 1: Establish scope and repository identity

Record:

- Repository root and current working tree state.
- Current branch or revision when available.
- User-requested target and non-target scope.
- Task class and operating mode.
- Whether the work is read-only, planning-only, or authorized for later implementation.

If multiple projects or workspaces are present, identify which are in scope before deep inspection.

### Step 2: Load governing instructions

Search for and read applicable instructions, including when present:

- `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `README.md`
- Workspace or package-level instruction files
- Architecture, product, security, testing, deployment, and migration documentation
- Existing specifications, ADRs, Project Ledger, and active change folders

Resolve instruction precedence. Record contradictions instead of silently choosing one.

### Step 3: Identify project topology

Map only what is relevant, while capturing the project-wide basics:

- Monorepo, polyrepo, single application, library, service, plugin, mobile, desktop, or infrastructure repository.
- Applications, packages, modules, services, shared libraries, generated code, and platform layers.
- Runtime, language, framework, package manager, lockfile, toolchain, and material versions.
- Source, test, schema, migration, configuration, script, documentation, and deployment locations.
- Entrypoints for application, worker, CLI, job, API, UI, and tests.

Do not recursively enumerate vendor directories or generated artifacts unless they are directly relevant.

### Step 4: Discover runnable commands

Establish commands from project files rather than guessing:

- Install or bootstrap
- Development and run
- Format
- Lint
- Type-check or static analysis
- Unit, integration, UI, E2E, security, and performance tests
- Build and package
- Database migration and validation
- Preview, deploy, health check, and rollback

For each command, record source, working directory, prerequisites, expected side effects, and whether it was actually run.

Do not treat a command as verified merely because it exists in a manifest.

### Step 5: Map architecture and boundaries

Identify, when applicable:

- Domain or core business rules
- Feature or use-case modules
- UI, controller, view-model, or presentation layers
- API, service, repository, infrastructure, and provider boundaries
- Routing, navigation, state management, Design System, localization, and accessibility structure
- Authentication, authorization, tenant boundaries, roles, sessions, and secrets
- Database entities, schemas, migrations, indexes, caches, queues, blobs, search, vectors, and retention
- External APIs, SDKs, webhooks, background jobs, scheduled tasks, and event flows
- Environment separation, CI/CD, observability, alerting, backup, incident, and rollback paths

The output should explain relationships, not merely list directories.

### Step 6: Trace the target behavior end to end

Starting from the user-visible or external trigger, trace the relevant path through:

1. Input or event source
2. Validation and normalization
3. Authentication and authorization
4. Routing or dispatch
5. Business logic and state transitions
6. Persistence, cache, queue, or external provider
7. Error, retry, timeout, cancellation, and recovery behavior
8. Response, UI update, emitted event, or side effect
9. Logging, metrics, traces, cleanup, and rollback

For UI work, include loading, empty, error, disabled, read-only, permission, offline, responsive, and success states where applicable.

### Step 7: Establish current behavior baseline

Use the strongest available evidence:

- Existing tests
- Reproducible runtime behavior
- API contracts or schemas
- Snapshots or screenshots
- Logs, traces, metrics, or incident records
- Current specifications or documentation

Record mismatches between documentation, tests, and code. Do not choose a source of truth without explaining why.

### Step 8: Perform blast-radius analysis

Identify:

- Direct callers, imports, consumers, routes, jobs, and events.
- Shared types, schemas, contracts, generated clients, and migrations.
- Tests, fixtures, mocks, snapshots, documentation, analytics, and monitoring.
- Platform-specific implementations and cross-platform behavior.
- Deployment, feature-flag, compatibility, and data migration consequences.

Rate impact by semantics, not only by file count:

- Local implementation detail
- Shared internal contract
- Public or partner contract
- Persistent data or migration
- Security or permission boundary
- Production operations or irreversible effect

### Step 9: Separate facts from improvement ideas

Produce three explicit sections:

1. Repository Facts
2. Project Conventions
3. Recommendations

Recommendations must include rationale, impact, migration cost, and whether they are required for the current task. Avoid opportunistic refactoring.

### Step 10: Record unknowns and route them

Classify each material unknown:

- Repository fact to investigate further
- Version-sensitive fact for `source-verification`
- Product decision for `intent-interview`
- Requirement gap for `requirements-specification`
- Architecture decision for `architecture-design`
- Implementation or verification issue for a later workflow

Each unknown requires an owner, resolution stage, and safe boundary.

### Step 11: Self-audit

Before completing discovery, verify:

- The target behavior was traced end to end.
- Relevant commands came from project evidence.
- Callers, dependents, tests, data, permissions, and platforms were considered.
- Facts, conventions, inferences, recommendations, and unknowns are separated.
- No mutation occurred without authorization.
- No secret value or unrelated private data was captured.
- The report is sufficient for the next workflow without re-reading the entire repository.

## Output Contract

Produce a Repository Discovery Report:

```markdown
# Repository Discovery Report

## Scope and Revision

## Governing Instructions

## Project Topology

## Technology and Version Inventory

## Command Matrix

## Architecture and Boundaries

## Target Behavior Trace

## Current Behavior Baseline

## Data, Permissions, and External Systems

## Test and Verification Baseline

## Deployment, Observability, and Rollback

## Blast Radius

## Repository Facts

## Project Conventions

## Inferences

## Recommendations Required for This Task

## Unknowns and Resolution Routes

## Risks

## Freshness and Evidence

## Recommended Next Workflow
```

For persisted state, update the Project Ledger with stable identifiers such as `FCT-`, `RSK-`, `OQ-`, and `EVD-`.

## Completion Status

Return one status:

- `ready` — sufficient verified context exists for the next workflow.
- `ready_with_recorded_unknowns` — unknowns are bounded and assigned to later stages.
- `blocked_access` — repository or required evidence cannot be accessed.
- `blocked_contradiction` — governing instructions or sources conflict materially.
- `blocked_risk` — proceeding would cross a safety, privacy, data, or authorization boundary.
- `stale_refresh_required` — prior discovery cannot safely be reused.

## Failure and Return Routes

- Product intent unclear → `intent-interview`
- External API or framework behavior uncertain → `source-verification`
- Desired behavior undefined → `requirements-specification`
- System structure or trade-off unresolved → `architecture-design`
- Implementation requested before discovery is ready → stop and report the missing repository context

## Quality Gate

Repository discovery is complete only when a competent engineer can locate the relevant implementation, understand the current behavior and constraints, identify material dependents and risks, and choose the next workflow without inventing repository facts.
