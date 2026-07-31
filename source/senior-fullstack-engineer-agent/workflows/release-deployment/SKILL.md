---
name: release-deployment
description: Plans, authorizes, executes, verifies, records, and rolls back software releases or deployments. Use only for the exact revision after required implementation, review, security, and preflight evidence, including migrations, flags, canaries, staged rollout, stores, infrastructure, or rollback.
---

# Release and Deployment

## Purpose

Move an exact, reviewed, verified revision into the intended environment through a controlled, observable, reversible process, then confirm real system health and update project state.

Release planning may be read-only. Deployment, merge, publication, migration, feature-flag change, infrastructure modification, or external notification is an operational write and requires the permission level defined by the Decision Policy.

## When to Use

Use this workflow when:

- A general availability has passed the required implementation, testing, QA, review, security, and preflight gates.
- Preparing a production, staging, preview, app-store, package, desktop, mobile, backend, data, model, or infrastructure release.
- A database or data migration must be sequenced with application rollout.
- Feature flags, canaries, blue-green, phased rollout, maintenance windows, or rollback are required.
- A deployment failed or post-release health requires a rollback decision.
- A release record, changelog, runbook, or post-release observation window must be established.

## Do Not Use

Do not use this workflow to:

- Deploy an unreviewed or unverified revision.
- Reuse evidence from a different commit, artifact, environment, or configuration.
- Invent permission to merge, push, publish, modify production data, incur cost, or notify users.
- Hide failed, skipped, stale, or blocked checks.
- Run destructive migration without backup, compatibility, validation, and rollback or an explicitly approved irreversible boundary.
- Call a successful CI build a successful production release.

## Preconditions

Read and apply:

- [`../../core/constitution.md`](./references/core/constitution.md)
- [`../../core/task-classifier.md`](./references/core/task-classifier.md)
- [`../../core/decision-policy.md`](./references/core/decision-policy.md)
- [`../../core/autonomy-policy.md`](./references/core/autonomy-policy.md) for any unattended release
- `preflight-verification`
- `code-review`
- `security-engineering` when security boundaries changed
- `project-state-handoff`
- `source-verification` for current platform deployment guidance

Required inputs:

- Exact source revision and immutable build artifact identity.
- Target environment, platform, account, region, tenant, channel, or store.
- Preflight result for that revision.
- Approved release scope, change record, migration, feature-flag, observability, rollback, and communication plan.
- Explicit operational permission.

For an unattended run, additionally require the bundled authorization envelope and exact run plan. Validate both before execution. The supervisor defaults to validation-only; `--execute` is valid only after the owner has approved the exact envelope and plan. Use the files bundled with this Skill:

- `references/templates/autonomy-run-envelope.json`
- `references/templates/autonomy-run-plan.json`
- `references/schemas/autonomy-run-envelope.schema.json`
- `references/schemas/autonomy-run-plan.schema.json`
- `scripts/validate_autonomy_envelope.py`
- `scripts/validate_autonomy_plan.py`
- `scripts/autonomy_supervisor.py`

## Release Principles

- Deploy artifacts, not mutable workspaces.
- Evidence must match the exact revision, artifact, configuration, and target.
- Separate build, release, deployment, migration, activation, and observation.
- Prefer progressive exposure and reversible steps.
- Expand before contract for schema and contract migrations.
- Establish health signals and rollback triggers before deployment.
- A deployment is incomplete until post-release verification and state recording finish.
- Do not let urgency erase backups, permissions, or rollback.
- Stop when observed system behavior contradicts the plan.

## Required Depth by Task Class

### Q — Quick Patch

Require exact revision, focused checks, artifact identity, simple rollback, smoke test, and release record.

### S — Standard Change

Add staging/preview validation, configuration check, monitoring, communication, and post-release observation.

### C — Complex Feature

Add phased rollout, compatibility window, migration sequencing, feature flags, capacity, support/runbook, consumer coordination, and explicit rollback decision points.

### X — Critical Change

Require independent approval, maintenance or launch window, backup/restore validation, incident commander or owner, no-go conditions, rollback rehearsal, security and compliance evidence, and controlled production permissions.

## Workflow

### Step 1: Establish release identity

Record:

- Repository, branch, commit, tag, and dirty-state status.
- Artifact name, version, digest, signature, provenance, and build job.
- Configuration and feature-flag version.
- Target environment, account, region, channel, and platform.
- Dependency and migration versions.

Do not deploy from uncommitted local changes unless the target process explicitly supports and records an immutable artifact.

### Step 2: Verify gate status

Confirm for the exact revision:

- Requirements and acceptance state.
- Implementation status.
- Test and QA evidence.
- Code review outcome.
- Security outcome and accepted risk.
- Preflight result.
- Required approvals.
- Documentation, changelog, support, and operational readiness.

Any failed or stale blocking gate returns upstream.

### Step 3: Define release strategy

Select the smallest safe strategy:

- Preview or internal.
- Staging.
- Canary.
- Percentage or cohort rollout.
- Blue-green.
- Feature-flag activation.
- Region-by-region.
- App-store phased release.
- Full release only when justified.

Define exposure sequence, duration, decision owner, and stop conditions.

### Step 4: Define migration sequence

For data, schema, API, event, model, or infrastructure changes specify:

- Compatibility window.
- Backup and restore point.
- Expand, backfill, validate, switch, and contract order.
- Read/write compatibility.
- Consumer migration.
- Lock, load, downtime, and data-integrity risks.
- Roll-forward and rollback behavior.
- Irreversible boundary and approval.

Do not combine destructive contract steps with the first application deployment when a safer compatible sequence exists.

### Step 5: Define health and rollback criteria

Before execution specify:

- Health checks and smoke tests.
- SLI/SLO and critical business metrics.
- Error, latency, saturation, queue, job, data, security, support, and cost indicators.
- Comparison baseline.
- Observation window.
- Automatic and manual rollback triggers.
- Who can decide continue, pause, roll back, or escalate.

### Step 6: Confirm operational permission

Summarize the exact external writes:

- Merge or push.
- Publish package, image, app, model, or assets.
- Modify infrastructure, configuration, secrets, flags, DNS, routes, or production data.
- Run migration or backfill.
- Notify customers or operators.
- Incur cost or consume quota.

Obtain required confirmation. Prior permission does not automatically transfer to a different environment, scope, or irreversible action.

Unattended execution is allowed only when the exact artifact hash, commands, paths, environment, expiry, health gates, zero-cost limit, and rollback command pass the deterministic validators. Do not edit an authorization envelope on behalf of its approver.

### Step 7: Execute one controlled step

For each step:

- State the action and expected result.
- Execute the approved command or platform action.
- Capture timestamp, actor, environment, revision/artifact, command/action ID, and result.
- Stop on unexpected output, drift, partial failure, or health regression.

Do not run later steps merely because an earlier step returned zero exit status.

### Step 8: Verify deployment and activation

Verify the actual target:

- Artifact/version is running.
- Configuration and flags match the plan.
- Schema/data migration status and invariants are correct.
- Health checks and smoke tests pass.
- Critical user flows work.
- Logs, metrics, traces, alerts, security events, and costs are within thresholds.
- Old and new consumers remain compatible during the window.

### Step 9: Continue, pause, or roll back

Use predefined criteria:

- Continue exposure when evidence is healthy.
- Pause when evidence is incomplete or ambiguous.
- Roll back when trigger conditions are met and rollback is safer than continued exposure.
- Escalate when rollback is unsafe, incomplete, or an irreversible boundary has passed.

A rollback is a new operational change and must also be verified.

### Step 10: Complete post-release observation

During the observation window:

- Compare against baseline and guardrails.
- Monitor user, support, data, security, performance, and cost signals.
- Confirm background jobs, queues, webhooks, emails, exports, and downstream consumers.
- Record incidents, deviations, and follow-up tasks.

### Step 11: Produce the Release Record

```markdown
# Release Record

## Release Identity

## Scope and Approved Changes

## Target Environment / Platform

## Gate Evidence

## Permissions and Approvals

## Strategy and Exposure Sequence

## Migration / Configuration / Feature Flags

## Execution Timeline

## Health and Smoke Evidence

## Observation Results

## Rollback Status and Trigger

## Incidents / Deviations

## Outcome
RELEASED / PARTIALLY_RELEASED / ROLLED_BACK / FAILED / BLOCKED

## Follow-up and Project State Updates
```

## Quality Gates

Pass only when:

- Exact revision, artifact, target, and configuration are known.
- All required gates and permissions are current.
- Migration, backup, compatibility, health, and rollback are defined.
- Actual target behavior is verified.
- Exposure and observation are complete for the required depth.
- Project state and release evidence are updated.

## Failure and Return Routes

- Preflight failed or stale → `preflight-verification`.
- Security risk unresolved → `security-engineering`.
- Unknown deployment failure → `systematic-debugging`.
- Requirement or architecture conflict → owning upstream workflow.
- Release paused or completed → `project-state-handoff`.
