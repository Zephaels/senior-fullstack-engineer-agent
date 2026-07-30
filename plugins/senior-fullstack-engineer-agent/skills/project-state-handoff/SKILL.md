---
name: project-state-handoff
description: Persists, validates, transfers, and restores project state across sessions, agents, engineers, milestones, pauses, and releases. Use when work must continue later, ownership changes, a milestone completes, an implementation is blocked, or current intent, decisions, evidence, risks, artifacts, and next actions must survive outside chat context. Do not use to claim unverified completion, store secrets, or restore stale state without checking the repository and environment.
---

# Project State and Handoff

## Purpose

Maintain a trustworthy, resumable project record that separates current intent, repository facts, confirmed decisions, assumptions, open questions, risks, artifacts, evidence, work status, and next actions from transient chat memory.

A handoff is an operational contract for continuation. It is not a narrative summary, a substitute for specifications, or a place to hide missing evidence.

## When to Use

Use this workflow when:

- A session, Agent, engineer, branch, or work period is ending.
- Work is paused, blocked, handed to another person, or resumed later.
- A lifecycle milestone is completed: discovery, specification, architecture, plan, implementation slice, review, preflight, release, migration, or incident.
- Multiple Agents or worktrees need a shared read-only fact base and explicit write ownership.
- Important decisions, evidence, unknowns, risks, and next steps must be externalized.
- Existing state may be stale and must be reconciled with the current repository.

## Do Not Use

Do not use this workflow to:

- Store passwords, tokens, private keys, session cookies, sensitive production data, or unredacted user information.
- Mark tests, builds, reviews, migrations, or deployments as passed without fresh evidence.
- Replace product requirements, architecture, tasks, code review, or release records with a vague summary.
- Restore a prior state before checking the current repository, specifications, dependencies, and environment.
- Rewrite history to make a failed or partial task appear complete.

## Preconditions

Read and apply:

- [`../../core/constitution.md`](../../core/constitution.md)
- [`../../core/task-classifier.md`](../../core/task-classifier.md)
- [`../../core/decision-policy.md`](../../core/decision-policy.md)
- Relevant workflow outputs for the current milestone

Inputs may include:

- Current conversation and task request.
- Project Ledger.
- Repository status, revision, branch, diff, worktree, and untracked files.
- Specifications, ADRs, plans, change folders, reviews, evidence, and release records.
- Current environment, dependencies, external service status, and known incidents.

## State Layers

### Persistent project state

Store durable, team-relevant information in versioned project documentation when authorized, for example:

```text
docs/engineering/
  project-ledger.yaml
  glossary.md
  decisions/
  specifications/
  architecture/
  plans/
  reviews/
  releases/
```

### Runtime or session state

Store temporary continuation information outside the product fact source, for example:

```text
.sfse/runtime/
  active-task.yaml
  handoff.md
  evidence-index.json
  last-refresh.json
```

Do not commit runtime state automatically. Follow project policy.

### External source references

For external systems, store identifiers and links or references, not secret contents. Record access requirements without embedding credentials.

## Ledger Item Types

Use stable IDs:

| Prefix | Type |
|---|---|
| `OBJ-` | Outcome |
| `FCT-` | Repository or environment fact |
| `TERM-` | Canonical term |
| `REQ-` | Requirement |
| `NON-` | Non-goal |
| `DEC-` | Confirmed decision |
| `ADR-` | Architecture decision |
| `ASM-` | Assumption |
| `OQ-` | Open question |
| `RSK-` | Risk |
| `DEF-` | Deferred item |
| `CHG-` | Change |
| `SLICE-` | Implementation slice |
| `TASK-` | Task |
| `EVD-` | Evidence |
| `INC-` | Incident |
| `REL-` | Release |

Each item includes status, statement, source, owner, affected artifacts, dates, evidence, supersession, and freshness when relevant.

## Confidence and Freshness

Use these states:

- `confirmed` — supported by current user decision, code, test, command, or authoritative source.
- `inferred` — reasoned but not directly proven.
- `assumed` — temporary reversible default.
- `unknown` — not established.
- `stale` — previously established but no longer safe to reuse.
- `superseded` — replaced by an explicit newer item.

Do not express false numerical confidence.

## Handoff Modes

Select one:

- `Save` — persist current state before pause or transfer.
- `Resume` — validate and restore prior state.
- `Milestone` — record completion of a lifecycle stage.
- `Blocker` — capture why work cannot safely continue.
- `Release` — record production delivery and post-release state.
- `Incident` — preserve timeline, current impact, mitigation, evidence, and next owner.
- `Reconcile` — resolve differences between chat, ledger, repository, specs, and environment.

## Workflow: Save

### Step 1: Establish current truth

Collect:

- Current task and desired outcome.
- Task class, mode, branch, revision, and workspace.
- Modified, staged, untracked, generated, and ignored files relevant to the task.
- Active specifications, architecture, plans, change folders, and reviews.
- Commands actually run and their results.
- External writes, deployments, migrations, or incidents that actually occurred.

Do not infer completion from code appearance or earlier statements.

### Step 2: Update ledger items

Record or update:

- Confirmed facts and decisions.
- Requirements and non-goals.
- Assumptions and validation conditions.
- Open questions, owner, resolution stage, and safe boundary.
- Risks, severity, mitigation, trigger, and owner.
- Evidence and exact source.
- Superseded items and contradictions.

### Step 3: Record work status

For each slice or task, use one:

- `not_started`
- `in_progress`
- `blocked`
- `implemented_unverified`
- `verified`
- `reviewed_needs_fixes`
- `accepted`
- `released`
- `rolled_back`
- `superseded`

Separate implementation from verification and acceptance.

### Step 4: Record evidence

For each evidence item, include:

- Command, test, review, screenshot, log, trace, metric, contract, or approval.
- Timestamp.
- Environment and revision.
- Result and relevant excerpt or artifact path.
- Scope and limitations.
- Whether it remains fresh.

Never store fabricated command output.

### Step 5: Define the exact next action

A usable handoff includes:

- Next workflow or task.
- Preconditions.
- Files or artifacts to read first.
- Commands to run.
- Decisions not to revisit unless evidence changes.
- Decisions still open.
- Write scope and permission boundary.
- Stop conditions and rollback point.

Avoid “continue implementation” without a concrete slice and gate.

### Step 6: Redact and review

Before saving:

- Remove secrets and sensitive payloads.
- Avoid absolute local paths unless required for the local runtime handoff.
- Avoid personal data not necessary for execution.
- Ensure claimed status matches evidence.
- Ensure the handoff does not override source specifications or ADRs.

## Workflow: Resume

### Step 1: Load prior state without trusting it yet

Read:

- Handoff.
- Project Ledger.
- Active specifications, architecture, plan, reviews, and evidence index.

Treat all operational facts as candidates for re-verification.

### Step 2: Check freshness

Compare:

- Repository root, branch, revision, diff, and worktree.
- Dependency and lockfile state.
- Relevant source, test, schema, migration, configuration, and deployment files.
- Active change/specification version.
- Environment and external provider versions or status when material.
- Previously recorded blockers, approvals, and permissions.

Mark changed facts as stale. Do not silently continue under an old plan.

### Step 3: Reconcile conflicts

If prior state conflicts with current facts:

1. Identify each conflict.
2. Determine the authoritative source or owner.
3. Mark the old item stale or superseded.
4. Update affected requirements, architecture, plans, risks, and tasks.
5. Route to the earliest stage that owns the gap.

Repository changes may require `repository-discovery`. Product changes may require `intent-interview` or `requirements-specification`.

### Step 4: Re-establish permissions

Confirm whether the resumed session may:

- Modify files.
- Install dependencies.
- Run tests or external services.
- Commit or push.
- Migrate data.
- Deploy or incur cost.

Prior authorization does not automatically transfer across environments, Agents, or users.

### Step 5: Produce a Resume Brief

State:

- Current verified objective.
- Current revision and scope.
- Accepted decisions.
- Stale or changed facts.
- Current work status.
- Next task and verification gate.
- Remaining risks and blockers.
- Required permissions.

Only then resume work.

## Workflow: Milestone or Release

For a milestone, record:

- Artifact completed.
- Readiness status.
- Evidence.
- Findings or unresolved items.
- Downstream workflow and gate.

For a release, also record:

- Release identifier and environment.
- Revision and migration version.
- Feature flags and rollout scope.
- Health checks and monitored signals.
- Rollback trigger and procedure.
- Actual post-release observation.
- Incident or follow-up items.

A release record does not imply success until post-release verification exists.

## Conflict Precedence

Use this order, while reporting contradictions:

1. Current explicit user or authorized owner decision for product policy.
2. Governing constitution and security/privacy policy.
3. Approved current specification and ADR.
4. Current verified repository and environment facts.
5. Current implementation plan and task state.
6. Prior handoff and chat summary.
7. Inference and assumption.

Do not use precedence to hide a conflict. Record and resolve it.

## Output Contract

### Project Ledger

```yaml
project:
  id: "..."
  name: "..."
  last_verified: "..."
  repository:
    root: "..."
    revision: "..."
    branch: "..."
  active_change: "CHG-..."
  task_class: "C-B"
  items:
    - id: "REQ-001"
      type: "requirement"
      status: "confirmed"
      statement: "..."
      source: "..."
      owner: "..."
      affects: []
      evidence: []
      last_verified: "..."
      supersedes: []
```

### Handoff

```markdown
# Project Handoff

## Handoff Mode and Timestamp

## Objective and Scope

## Repository and Environment State

## Governing Artifacts

## Confirmed Decisions and Invariants

## Work Completed

## Work Implemented but Not Verified

## Verification and Evidence

## Current Findings and Risks

## Open Questions and Owners

## Blockers

## Files and Artifacts Changed

## External Actions Performed

## Exact Next Action

## Required Permissions

## Stop and Rollback Conditions

## Freshness Notes
```

### Resume Brief

```markdown
# Resume Brief

## Verified Objective

## Current Revision and Scope

## Freshness Check

## Accepted Decisions

## Changed or Stale Information

## Current Work Status

## Next Task and Gate

## Risks and Blockers

## Permissions
```

## Status

Return one:

- `saved`
- `saved_with_blockers`
- `resume_ready`
- `resume_requires_discovery`
- `resume_requires_spec_update`
- `resume_requires_architecture_update`
- `resume_requires_permission`
- `conflict_requires_owner`
- `release_observation_pending`
- `incident_handoff`

## Failure and Return Routes

- Repository changed materially → `repository-discovery`
- Product intent or policy changed → `intent-interview`
- Requirement truth changed → `requirements-specification`
- Architecture or migration changed → `architecture-design`
- Plan no longer matches reality → `implementation-planning`
- Evidence missing → corresponding verification workflow before claiming completion

## Quality Gate

A handoff is complete only when another competent engineer or Agent can safely determine current truth, distinguish completed from unverified work, locate governing artifacts, understand risks and permissions, and execute the exact next action without relying on inaccessible chat memory or inventing missing decisions.
