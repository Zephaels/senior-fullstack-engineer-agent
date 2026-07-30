---
name: code-review
description: Performs an evidence-based, read-only review of a software change before merge or release, independently evaluating specification compliance and engineering quality across correctness, architecture, security, data, performance, accessibility, operations, tests, and maintainability. Use for PRs, diffs, completed slices, bug fixes, refactors, migrations, and agent-generated code. Do not silently fix findings or approve unverified work.
---

# Code Review

## Purpose

Determine whether a proposed change builds the right behavior and builds it safely enough to enter the shared codebase. Review is read-only by default and must use the actual diff, governing artifacts, repository context, and verification evidence.

## When to Use

Use:

- Before merging any behavioral change.
- After a feature slice, bug fix, refactor, migration, dependency upgrade, generated-code change, or security remediation.
- When reviewing code written by a human or Agent.
- When the user asks to review a PR, branch, commit, diff, or implementation.
- Before a release when code-level risk remains.

## Do Not Use

Do not:

- Review without establishing the target revision and comparison base.
- Treat passing CI as a substitute for review.
- Automatically edit, commit, or push fixes unless separately authorized.
- Invent missing requirements or approve behavior that cannot be traced.
- block a change merely because the reviewer would write it differently.
- dilute Critical or Required findings to meet a deadline.

## Preconditions

Collect:

- Base and head revision or exact diff.
- Task classification.
- Requirements, acceptance criteria, architecture, ADRs, plan, and Project Ledger references.
- Repository discovery and relevant conventions.
- Test, QA, security, performance, migration, and preflight evidence available so far.
- Dependency changelogs and lockfile changes when applicable.

If the diff is too large to understand reliably, require splitting or explicitly mark the review incomplete.

## Dual-Axis Review

### Axis A: Specification Compliance — “Did we build the right thing?”

Check:

- Every in-scope requirement and acceptance scenario.
- Explicit non-goals and forbidden behavior.
- Permissions, ownership, tenant boundaries, and data lifecycle.
- State transitions, errors, retries, cancellation, concurrency, and recovery.
- Public contracts and compatibility.
- Platform behavior and user-visible states.
- Operational and migration requirements.
- Scope drift and missing work.

### Axis B: Engineering Quality — “Did we build it well?”

Check:

- Correctness and invariants.
- Readability, naming, cohesion, coupling, and complexity.
- Architecture and dependency direction.
- Input validation, authorization, secrets, injection, unsafe files, and logging.
- Data constraints, transactions, consistency, migration, and rollback.
- Performance, resource use, cancellation, and backpressure.
- Accessibility and platform conventions.
- Tests, observability, operational readiness, documentation, and maintainability.

Axis A and Axis B findings remain separate. Strong code cannot compensate for the wrong product behavior, and specification compliance cannot compensate for unsafe code.

## Review Workflow

### Step 1: Establish intent and scope

Summarize:

- What the change claims to do.
- Which users, contracts, data, and platforms it affects.
- What is explicitly out of scope.
- What evidence is available.

### Step 2: Inspect the actual change

Review:

- Diff and changed files.
- Callers, dependents, exports, schemas, generated files, and lockfiles.
- Deleted or moved behavior.
- Tests and fixtures.
- Migration and deployment artifacts.
- Configuration and secrets handling.

Do not review only the PR description.

### Step 3: Trace critical behavior end to end

For each critical path, follow:

```text
input/identity
→ validation/authorization
→ domain rule/state
→ persistence/provider
→ result/error
→ logging/metrics/audit
```

Identify the first place an invariant can fail or an unauthorized actor can cross a boundary.

### Step 4: Review failure and edge paths

Check:

- Null, empty, invalid, duplicate, stale, and oversized input.
- Timeout, retry, cancellation, partial failure, offline, and provider failure.
- Concurrency, ordering, idempotency, locks, and race conditions.
- Permission changes, revoked sessions, tenant mismatch, and ownership changes.
- Migration mixed states, rollback, and old consumers.
- Cleanup, resource release, and error observability.

### Step 5: Review tests and evidence

Ask:

- Does the test suite prove the changed behavior rather than mirror implementation?
- Did bug-fix tests fail before the fix?
- Are important boundaries tested with real integration where practical?
- Are tests isolated, deterministic, and free of hidden retries/skips?
- Was user-visible behavior tested in a real runtime?
- Do commands and artifacts correspond to the reviewed revision?

Do not trust Agent or author claims without checking evidence.

### Step 6: Review dependencies and generated artifacts

For dependency changes:

- Confirm necessity and scope.
- Review release notes/changelog and security advisories.
- Verify license and platform compatibility.
- Review lockfile changes generated by the package manager.
- Isolate unrelated upgrades.

For generated code:

- Review source schema/config and generation command.
- Do not manually patch generated output without understanding regeneration.

### Step 7: Classify findings

Use:

| Severity | Merge effect |
|---|---|
| Critical | Must block; exploitable security, data loss/corruption, severe outage, or irreversible invalid behavior |
| Required | Must resolve or explicitly return upstream; correctness, contract, permission, migration, major maintainability or missing evidence |
| Recommended | Valuable improvement that does not make current change unsafe or incorrect |
| Nit | Small clarity or consistency issue |
| Question | Missing context; not a disguised demand |
| Observation | Context, praise, or future risk without requested change |

Every blocking finding must include:

- File and line or exact symbol.
- Violated requirement, invariant, convention, or evidence rule.
- Concrete failure scenario.
- Severity rationale.
- Smallest safe correction or return route.

### Step 8: Decide the review outcome

- `APPROVE`: no unresolved Critical/Required findings and evidence is sufficient.
- `APPROVE_WITH_FOLLOW_UP`: only non-blocking work remains, with owners.
- `REQUEST_CHANGES`: blocking findings exist.
- `BLOCKED`: requirements, revision, environment, or evidence are insufficient for a reliable review.

Do not approve merely because the change improves something. It must not make overall code health, safety, or product correctness worse.

## Presumptive Risk Signals

Investigate carefully when a change:

- Adds a silent fallback that hides an invariant.
- Scatters new conditionals across unrelated paths.
- Adds feature logic to a shared utility.
- Duplicates a canonical helper or business rule.
- Grows an already hard-to-understand file without a clear boundary.
- Performs a broad dependency update with a behavioral change.
- Hand-edits a lockfile or generated artifact.
- Disables tests, reduces assertions, widens exception handling, or ignores errors.
- Adds client-only authorization or secrets.
- Introduces destructive migration without compatibility and rollback.

These signals require analysis; they are not automatic style preferences.

## Output Contract

```markdown
# Code Review Report

## Review Target
- Base:
- Head:
- Scope:
- Task class:

## Change Intent and Evidence Reviewed

## Axis A — Specification Compliance

## Axis B — Engineering Quality

## Findings
### CR-001 — Title
- Severity:
- Axis:
- Location:
- Evidence:
- Failure scenario:
- Required action or route:

## Test and Runtime Evidence Assessment

## Dependency, Migration, and Operational Assessment

## Positive Observations

## Unreviewed or Blocked Areas

## Outcome
```

## Quality Gate

A review is complete only when:

- The exact diff and governing artifacts were reviewed.
- Both axes were evaluated independently.
- Critical paths and failure paths were traced.
- Findings are evidence-based and severity-labeled.
- Required tests/build/runtime evidence was checked.
- All unresolved limitations are disclosed.
- No unauthorized fix, commit, or push occurred.

## Return Routes

- Missing/ambiguous behavior → Requirements Specification.
- Architecture defect → Architecture Design.
- Root cause unknown → Systematic Debugging.
- Approved correction → Incremental Implementation.
- Missing tests → Test Engineering.
- Missing runtime evidence → Quality Assurance.
- Review passed → Preflight Verification.
