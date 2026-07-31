---
name: test-engineering
description: Designs and executes risk-based automated and manual test evidence for new behavior, bug fixes, integrations, data changes, and platform experiences. Use before implementation to define proof, during implementation for test-driven slices, and after changes to demonstrate acceptance and prevent regression. Do not use as a substitute for runtime QA, security review, performance measurement, or preflight completion.
---

# Test Engineering

## Purpose

Translate requirements, risks, contracts, and failure modes into trustworthy, repeatable evidence that can detect the absence or breakage of required behavior.

Tests are not an activity count or a coverage percentage. A useful test must have a clear risk, observable behavior, failure reason, and maintenance owner.

## When to Use

Use this skill when:

- Implementing new logic, behavior, or state transitions.
- Fixing a bug or regression.
- Changing a public API, event, file format, schema, provider, or dependency.
- Designing the test strategy for a feature, migration, or release.
- Existing tests are missing, flaky, overly mocked, coupled to implementation, or insufficient for the risk.
- A failed test needs classification as product defect, test defect, environment defect, or flaky signal.

## Do Not Use

Do not use this skill alone when:

- A user-visible workflow must be exercised in a real browser, device, or deployed environment. Use `quality-assurance` as well.
- The root cause of an unexpected failure is unknown. Use `systematic-debugging`.
- The request is a general code review. Use `code-review`.
- The task is ready for final completion claims. Use `preflight-verification`.
- Security or performance requires specialized tooling and threat/risk analysis.

## Inputs

Read:

- Requirements and acceptance scenarios.
- Architecture, contracts, state transitions, data lifecycle, and permissions.
- Implementation plan and task classification.
- Existing test framework, fixtures, commands, CI, and coverage conventions.
- Repository facts and known pre-existing failures.
- Target platform and runtime environments.

## Test Strategy Principles

1. Test user-observable behavior and stable contracts, not incidental implementation details.
2. Prefer real implementations, then controlled fakes, then stubs; mock only unstable or expensive boundaries.
3. Isolate test state so tests can run independently and in any order.
4. A bug fix requires a reproduction that fails without the fix and passes with it.
5. Test the smallest layer that can prove the risk, then add broader tests only where integration creates new risk.
6. Cover failure paths and recovery, not only the happy path.
7. Never disable, skip, loosen, or snapshot-update a failing test without understanding why.
8. Coverage can reveal untested code but cannot prove meaningful behavior.
9. Flaky tests are defects in the delivery system and must be owned.
10. Manual verification must be explicit, repeatable, and captured as evidence.

## Test Levels

| Level | Best for | Avoid |
|---|---|---|
| Unit | Pure domain rules, validation, transformations, state transitions | Re-testing frameworks or databases |
| Component | UI behavior and states in controlled context | Coupling to CSS classes or internals |
| Contract | API, event, provider, schema, and consumer compatibility | Duplicating full E2E behavior |
| Integration | Real boundaries among application modules and infrastructure | Mocking every dependency |
| End-to-End | Critical user journeys and cross-system behavior | Exhaustively testing every branch |
| Migration | Forward, backward, mixed-version, rollback, and data invariants | Testing only an empty database |
| Property-Based | Invariants and broad input spaces | Using generators without meaningful properties |
| Exploratory/Manual | New UX, unknown risks, accessibility, device behavior | Treating unrecorded clicking as proof |

## Required Coverage by Risk

### Quick Patch

- Direct reproduction or focused behavior test.
- Relevant existing tests.
- One fresh runtime or command-based verification when executable behavior changes.

### Standard Change

- Acceptance behavior.
- Negative and boundary paths.
- Permission and error behavior when relevant.
- Integration at the changed boundary.
- Regression coverage for surrounding behavior.

### Complex Feature

Also include:

- State transition matrix.
- Concurrency, duplicate, retry, timeout, cancellation, and partial failure.
- Cross-platform or browser/device matrix.
- Contract, migration, and observability verification.
- Critical E2E journeys.

### Critical Change

Also include:

- Independent test review.
- Security and privacy abuse cases.
- Rollback and recovery drills.
- Mixed-version or compatibility tests.
- Failure injection, load, resilience, or data integrity tests as appropriate.
- Explicit evidence retention and release gates.

## Workflow

### Step 1: Build a risk-to-test matrix

For each material risk, record:

- Requirement or invariant.
- Failure impact.
- Likelihood or uncertainty.
- Best observable boundary.
- Test level.
- Environment and data needed.
- Expected failure signal.
- Owner and execution phase.

Do not start with “write unit tests.” Start with “what failure must this suite detect?”

### Step 2: Discover the actual test stack

Read repository commands and configuration. Identify:

- Frameworks and versions.
- Test locations and naming.
- Fixtures, factories, seeds, containers, and service dependencies.
- Parallelism, isolation, retries, timeouts, and sharding.
- CI environments and required checks.
- Coverage collection and thresholds.
- Existing flaky, skipped, quarantined, or slow suites.

Never invent commands that the repository does not support.

### Step 3: Define test data and isolation

Specify:

- Data ownership and cleanup.
- Tenant/user identities and permission states.
- Deterministic time, randomness, locale, and network behavior.
- Sensitive data restrictions.
- Idempotent setup and teardown.
- Concurrency and ordering requirements.

Tests must not depend on execution order or leak state to other tests.

### Step 4: Write the failing proof

For behavior changes:

1. Write the smallest test expressing the desired public behavior.
2. Run it before implementation.
3. Confirm it fails for the expected behavioral reason, not syntax, setup, environment, or typo.
4. Save the RED evidence.

For bug fixes, the test must reproduce the original symptom or invariant violation.

### Step 5: Implement and reach GREEN

During `incremental-implementation`:

- Write the minimum code to make the focused proof pass.
- Run affected tests after each meaningful code change.
- Keep output clean; investigate warnings and flakes.
- Refactor only while the suite remains green.

### Step 6: Add risk-complete coverage

After the minimum behavior passes, add only the tests justified by the matrix:

- Empty, invalid, oversized, stale, duplicate, or conflicting input.
- Unauthorized, expired, revoked, cross-tenant, or read-only actors.
- Timeout, retry exhaustion, provider failure, offline, partial success, and cancellation.
- Concurrent updates, ordering, idempotency, and race conditions.
- Data retention, deletion, restore, migration, and rollback.
- Platform, localization, text scaling, keyboard, and accessibility states.

### Step 7: Validate the tests themselves

Check:

- The test fails when the protected behavior is removed or reverted.
- Assertions are specific enough to catch the defect.
- Tests do not pass because of stale state, broad exception handling, retries, or snapshots.
- Mocks preserve the actual boundary contract.
- No skipped or focused-only test remains.
- Flakiness is not hidden with blind retries or sleep.

### Step 8: Execute the appropriate suite

Run:

- Focused tests for fast feedback.
- Integration and contract suites for changed boundaries.
- Full relevant suite before review or handoff.
- CI-equivalent commands before release when available.

Record command, environment, revision, timestamp, exit status, pass/fail count, skips, retries, and artifacts.

### Step 9: Classify failures

A failure must be categorized as one of:

- Product code defect.
- Test defect.
- Requirement ambiguity.
- Environment or dependency issue.
- Flaky or nondeterministic signal.
- Expected baseline failure unrelated to the change.

Route unexplained failures to Systematic Debugging. Do not update expected output merely to make the suite green.

## Browser and UI Testing Rules

For browser tests:

- Prefer user-facing roles, names, labels, and explicit test contracts.
- Avoid CSS classes, DOM shape, internal state, and arbitrary sleep.
- Use auto-waiting/actionability where supported.
- Isolate storage, cookies, session, test data, and accounts.
- Capture traces, screenshots, console, and network evidence on failure.
- Keep visual-regression operating system, browser, fonts, and viewport controlled.

## Output Contract

```markdown
# Test Engineering Record

## Scope and Revision

## Requirements, Invariants, and Risks

## Existing Test Baseline

## Risk-to-Test Matrix
| Risk | Requirement | Level | Environment | Expected Signal | Status |

## RED Evidence

## GREEN Evidence

## Regression Coverage

## Commands Actually Run
| Command | Environment | Exit | Passed | Failed | Skipped | Evidence |

## Test Data and Isolation

## Flaky, Quarantined, or Pre-existing Failures

## Coverage Gaps and Deferred Tests

## Release-Relevant Test Decision
```

## Quality Gate

Test evidence is acceptable only when:

- It maps to requirements or explicit risks.
- Behavior-changing tests were observed failing for the expected reason when required.
- Tests pass with the implementation using fresh output.
- Test state is isolated and deterministic enough to trust.
- Critical failure and permission paths are covered.
- Skips, retries, flakes, and unexecuted suites are disclosed.
- The evidence identifies the exact revision and environment.

## Return Routes

- Unclear expected behavior → Requirements Specification.
- Missing testability or unstable boundary → Architecture Design.
- Unexpected failure → Systematic Debugging.
- User-visible flow verification → Quality Assurance.
- Implementation ready for assessment → Code Review.
- Full delivery gate → Preflight Verification.
