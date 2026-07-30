---
name: incremental-implementation
description: Implements an approved software change as small, complete, reversible, and independently verifiable vertical slices. Use after requirements, architecture, and an implementation plan are sufficiently ready, or for a bounded quick patch whose scope and verification are already clear. Do not use to discover product requirements, invent architecture, investigate an unexplained defect, or claim completion without fresh evidence.
---

# Incremental Implementation

## Purpose

Turn an approved requirement and implementation plan into the smallest complete production change that preserves existing behavior, keeps the repository recoverable, and produces evidence after every meaningful increment.

This workflow executes decisions already made. It must not silently redefine product behavior, architecture, public contracts, permissions, data policy, platform scope, or release policy.

## When to Use

Use this skill when:

- A feature or change has an approved specification and implementation plan.
- A Brownfield change has a repository baseline, blast radius, and approved delta.
- A Quick Patch has a clearly bounded target, known expected behavior, and a direct verification path.
- A task touches more than one file or more than one architectural layer and should be delivered as vertical slices.
- Work must be safe to pause, review, revert, or hand off between increments.

## Do Not Use

Do not use this skill when:

- The user outcome, business rule, permission, data lifecycle, or public behavior is materially unclear. Return to [Intent Interview](../intent-interview/SKILL.md) or [Requirements Specification](../requirements-specification/SKILL.md).
- The implementation would require inventing a new architecture or changing an approved boundary. Return to [Architecture Design](../architecture-design/SKILL.md).
- There is an unexplained failure, regression, performance anomaly, or incident. Use [Systematic Debugging](../systematic-debugging/SKILL.md).
- The request is only to audit, review, or test. Stay read-only and use the relevant assurance workflow.
- A deployment, merge, push, database write, destructive migration, or external side effect has not been authorized.

## Governing Inputs

Before implementation, read the smallest sufficient set of:

- The task classification and decision policy.
- The approved requirement or change delta.
- The architecture and ADRs that constrain the task.
- The implementation plan and target vertical slice.
- The repository discovery report and current revision.
- Existing tests, fixtures, design system, API contracts, migrations, and deployment conventions relevant to the slice.
- The current Project Ledger or handoff, then revalidate its freshness.

If a required source is missing, stale, contradictory, or unapproved, stop and return to its owning workflow.

## Implementation Modes

| Mode | Use | Required discipline |
|---|---|---|
| Quick Patch | Small, local, low-risk correction with known behavior | Minimal diff, direct regression verification, no scope expansion |
| Planned Slice | Normal implementation from an approved plan | One vertical slice at a time, test before expansion |
| Migration Slice | Schema, data, API, provider, or platform migration | Compatibility window, reversible stages, explicit rollback |
| Recovery Slice | Implementing a fix after root cause is established | Reproduction test first, smallest root-cause fix, regression evidence |
| Feature-Flagged Slice | Incomplete or risky behavior cannot be exposed | Flag disabled by default, cleanup and removal criteria recorded |

## Core Principles

1. **One increment has one observable purpose.**
2. **Complete a vertical path before broad horizontal construction.**
3. **Do not mix feature work, unrelated cleanup, dependency upgrades, and architectural refactors.**
4. **A working repository is the invariant after every increment.**
5. **The existing extension point is preferred over a parallel implementation.**
6. **Public interfaces remain stable unless an approved migration exists.**
7. **Tests prove behavior; compilation alone is not enough.**
8. **A feature that is not ready must not become visible without a safe flag or isolation boundary.**
9. **Database and infrastructure changes require an explicit reverse or recovery route.**
10. **The implementation must expose uncertainty rather than hide it behind fallbacks.**

## Scope Lock

At the start of each increment, record:

- Slice ID and objective.
- Requirement and acceptance scenario references.
- Files, symbols, contracts, data entities, and platforms in scope.
- Explicitly excluded files, concerns, and refactors.
- Expected tests and verification commands.
- Required permissions and external side effects.
- Stop conditions and rollback point.

Any newly discovered work must be classified as:

- Required to complete this slice.
- A defect or risk that blocks the slice.
- A separate follow-up task.
- An architecture or requirement change that returns upstream.

Do not absorb follow-up work merely because it is nearby.

## Workflow

### Step 1: Revalidate the baseline

Before editing:

- Confirm repository root, branch, revision, and working-tree state.
- Confirm the implementation plan still matches the current code.
- Confirm target files and extension points still exist.
- Run or inspect the relevant baseline tests when practical.
- Record pre-existing failures separately.
- Confirm no other Agent or person is modifying the same files or contracts.

If the baseline has materially changed, return to Repository Discovery or Implementation Planning.

### Step 2: Select the smallest complete vertical slice

A valid slice should connect as much of the real path as necessary to prove value, for example:

```text
User/API input
→ trusted validation
→ business rule
→ persistence or provider boundary
→ observable output
→ test evidence
```

Avoid creating all database types, then all services, then all APIs, then all UI when a thinner end-to-end path can validate the design earlier.

### Step 3: Establish a failing proof when behavior changes

Route to [Test Engineering](../test-engineering/SKILL.md) and create or identify a test that:

- Expresses the required behavior.
- Fails for the expected reason before the implementation.
- Uses the most stable public or observable boundary available.
- Does not merely mirror the implementation.

Documented exceptions are allowed for throwaway prototypes, generated artifacts, pure static content, or configurations that cannot be meaningfully tested in isolation. The exception must still define another fresh verification method.

### Step 4: Implement the minimum complete change

- Follow existing architecture and naming when they remain appropriate.
- Keep domain rules out of UI, transport, or provider-specific code.
- Validate untrusted input at trusted boundaries.
- Enforce authorization in trusted code, not only in presentation logic.
- Handle cancellation, timeout, retry, duplicate submission, stale state, and concurrency when required by the specification.
- Preserve logs, metrics, privacy, and error semantics.
- Add dependencies only after checking necessity, maintenance, license, size, security, and platform support.
- Avoid speculative abstractions before there is a demonstrated second or third use.

### Step 5: Verify the increment immediately

Run only commands that can change confidence after this increment:

- Targeted unit or component tests.
- Contract or integration tests.
- Type-check, compile, or build for the affected surface.
- Runtime smoke test or browser/mobile verification where behavior is user-visible.
- Migration dry-run or compatibility check when relevant.

Read the complete output and exit status. Do not rerun an unchanged successful command merely to create activity.

### Step 6: Inspect the diff and blast radius

Check:

- The diff matches the Scope Lock.
- No unrelated files changed.
- Generated files and lockfiles changed only for an understood reason.
- No secrets, debug output, dead branches, or temporary bypasses remain.
- Public contracts, data, platform behavior, and error semantics are preserved or intentionally changed.
- Tests fail without the behavior and pass with it where regression proof is required.

### Step 7: Update state and artifacts

After every accepted increment:

- Update task status and evidence references.
- Record new facts, decisions, risks, and follow-ups.
- Update specifications or ADRs only when the approved truth changed.
- Mark implementation as `implemented_unverified` until the required evidence is complete.
- Record an exact resume point when pausing.

Use [Project State and Handoff](../project-state-handoff/SKILL.md) for cross-session or cross-Agent continuation.

### Step 8: Continue, stop, or return upstream

Continue only when the increment is verified and the next slice remains valid.

Stop and route upstream when:

- The requirement is ambiguous or contradictory.
- The architecture cannot support the behavior without a new decision.
- The change exceeds the approved blast radius.
- A security, data, compatibility, or migration risk appears.
- Tests expose a different defect or the baseline is unreliable.
- Three attempts have not produced a verified result.

## Change Separation Rules

Separate these into different increments or tasks unless inseparable:

- Feature implementation and broad refactoring.
- Dependency upgrade and business behavior change.
- Database migration and irreversible cleanup.
- Public API change and consumer migration.
- Security hardening and unrelated formatting.
- Generated-code update and manual behavioral changes.

## Output Contract

Produce or update an Increment Record with:

```markdown
# Increment Record

## Identity
- Slice ID:
- Task class:
- Repository revision:
- Status:

## Objective and Acceptance References

## Scope Lock
### In scope
### Explicitly out of scope

## Files and Contracts Changed

## Implementation Summary

## Test-First or Verification Strategy

## Commands Actually Run
| Command | Purpose | Exit | Result | Evidence |

## Runtime Verification

## Data, Security, Platform, and Operational Effects

## Diff and Blast-Radius Review

## New Facts, Decisions, Risks, and Follow-ups

## Rollback Point

## Next Slice or Return Route
```

## Quality Gate

An increment may be marked verified only when:

- Its acceptance behavior is demonstrated.
- Targeted tests and required checks pass with fresh evidence.
- The diff is limited to the approved scope.
- Existing relevant behavior has not regressed.
- No unresolved Critical or Required issue remains.
- Data, permission, compatibility, platform, and operational effects are accounted for.
- Project state and evidence are updated.

Passing one targeted test does not prove the entire feature or release is complete. Route the completed set of increments to QA, Code Review, Security Review, and Preflight as required by task class.

## Failure and Return Routes

| Failure | Route |
|---|---|
| Product behavior unclear | Intent Interview / Requirements Specification |
| Architecture decision missing | Architecture Design |
| Plan stale or incomplete | Implementation Planning |
| Unexpected failure or regression | Systematic Debugging |
| Test design or coverage unclear | Test Engineering |
| User-visible flow needs validation | Quality Assurance |
| Slice implemented and ready for review | Code Review |
| All review issues resolved | Preflight Verification |
