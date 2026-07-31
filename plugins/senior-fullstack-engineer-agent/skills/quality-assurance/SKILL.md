---
name: quality-assurance
description: Validates a built software capability from the user and operational perspective using realistic workflows, environments, platforms, accessibility modes, and failure conditions. Use when a feature, fix, general availability, or deployed system must be exercised end to end. Default to report-only read-only QA; switch to remediation only with explicit authorization and route each fix through debugging, implementation, and re-verification.
---

# Quality Assurance

## Purpose

Determine whether the software actually works for its intended users in realistic conditions, not merely whether isolated tests pass. Produce reproducible evidence, severity-ranked defects, coverage limits, and a ship-readiness decision.

## Default Mode

QA is read-only and report-only by default.

Do not modify source code, test data, configuration, deployments, accounts, or external services unless the user has explicitly authorized remediation and the action is permitted by the Decision Policy.

## When to Use

Use when:

- A feature, bug fix, general availability, or deployed environment is ready for validation.
- The user asks to test the site, application, flow, browser behavior, mobile behavior, accessibility, or cross-platform experience.
- Automated tests pass but real user behavior is not yet proven.
- A regression must be checked across affected journeys.
- A release needs a structured QA report and readiness decision.

## Do Not Use

Do not use to:

- Define requirements or invent expected behavior.
- Diagnose unexplained technical failures before reproduction and root-cause analysis.
- Replace unit, integration, contract, security, or performance testing.
- Automatically fix and commit every discovered issue.
- Test production with destructive actions or real customer data without authorization.

## QA Profiles

| Profile | Coverage |
|---|---|
| Quick | Critical path, blocker/high severity, changed surface |
| Standard | Critical paths plus major alternate, permission, error, responsive, and accessibility states |
| Exhaustive | Broader browsers/devices/locales, cosmetic consistency, exploratory and recovery scenarios |
| Release | Standard/Exhaustive plus deployment, configuration, migration, monitoring, rollback, and smoke checks |
| Report Only | Findings and evidence; no source or environment modification |
| Remediation Loop | Authorized finding→debug→fix→retest cycle with isolated changes |

Task class and release risk select the minimum profile. A deadline may reduce optional breadth but may not remove critical-path, security, data-integrity, or rollback checks.

## Preconditions

Before QA:

- Requirements and acceptance scenarios are available.
- The target build, revision, environment, feature flags, and data are identified.
- Known pre-existing failures are separated.
- Test accounts, tenants, devices, browsers, and permissions are approved.
- Destructive or billable paths have safe substitutes or explicit authorization.
- Observability and evidence capture are available where needed.

## Workflow

### Step 1: Establish the QA contract

Record:

- Target capability and revision.
- Environment and platform matrix.
- User roles and test identities.
- In-scope journeys and explicit exclusions.
- Data reset and cleanup plan.
- Allowed actions and prohibited side effects.
- Severity model and stop conditions.

### Step 2: Build a journey-based test plan

Prioritize:

1. Primary successful workflow.
2. Authentication, authorization, ownership, and tenant isolation.
3. Empty, loading, disabled, read-only, error, offline, sync, conflict, cancellation, and success states.
4. Invalid, duplicate, stale, oversized, slow, interrupted, or partial inputs.
5. Cross-browser, responsive, mobile/tablet/desktop, orientation, window resizing, keyboard, pointer, and touch where applicable.
6. Accessibility, text scaling, focus order, screen reader, contrast, reduced motion, localization, and long text.
7. Refresh, deep link, back/forward, session expiry, recovery, retry, and state restoration.
8. Logs, metrics, audit events, notifications, emails, webhooks, files, exports, and downstream effects.

### Step 3: Capture a baseline

Before changing anything:

- Record health of the target environment.
- Capture current console, network, log, and monitoring errors.
- Run known smoke tests.
- Confirm data and accounts are in the expected state.
- Note pre-existing defects and environmental limitations.

### Step 4: Execute as the user would

- Use user-facing labels, roles, navigation, and interactions.
- Do not bypass the product through internal APIs unless the scenario explicitly tests an API.
- Keep each case isolated with controlled data and identity.
- Capture screenshots, traces, videos, console, network, logs, and IDs needed for reproduction.
- Verify both visible result and trusted side effects.

For browser automation, prefer stable user-facing locators and auto-waiting; avoid CSS internals and arbitrary sleeps.

### Step 5: Classify findings

| Severity | Meaning |
|---|---|
| Critical | Security, data loss/corruption, widespread outage, irreversible impact, or no safe workaround |
| High | Core journey blocked, serious permission/privacy issue, or major regression |
| Medium | Important alternate path broken or significant usability/accessibility problem with workaround |
| Low | Minor behavior, consistency, copy, visual, or non-blocking issue |
| Observation | Risk, ambiguity, or improvement not proven as a defect |

Each defect must include:

- Exact environment and revision.
- Preconditions and test identity.
- Reproduction steps.
- Expected and actual behavior.
- Evidence.
- Impact and severity rationale.
- Scope and suspected boundary without pretending root cause is proven.

### Step 6: Decide whether to remediate

In report-only mode, stop after reporting.

In authorized remediation mode:

1. Route each unexplained defect to `systematic-debugging`.
2. Create or confirm a regression proof with `test-engineering`.
3. Apply one isolated fix through `incremental-implementation`.
4. Re-run the failed scenario and the relevant regression set.
5. Update evidence and defect status.

Do not batch unrelated fixes into one change.

### Step 7: Re-verify the complete affected journey

After any fix:

- Verify the exact defect.
- Verify adjacent states and roles.
- Verify no new console/network/log errors.
- Verify data and downstream effects.
- Re-run the critical path end to end.

### Step 8: Produce a readiness decision

Use one result:

- `READY`: no unresolved blocker and required coverage complete.
- `READY_WITH_ACCEPTED_RISK`: only explicitly accepted non-blocking risk remains.
- `NOT_READY`: unresolved Critical/High issue, missing critical evidence, or unsafe environment.
- `BLOCKED`: QA could not execute because required environment, identity, data, permission, or tooling was unavailable.

## Platform Adaptation

QA must validate product-semantic consistency, not pixel identity.

- Mobile: touch targets, interruptions, permission prompts, keyboard, rotation, weak network, background/foreground.
- Tablet: multi-column adaptation, resize, keyboard/pointer, drag/drop, state preservation.
- Desktop: keyboard shortcuts, menus, multiple windows, precise pointer, context menus, multi-select, restore state.
- Web: responsive behavior, supported browsers, deep links, history, refresh, session expiry, retry and offline handling.

Do not claim a platform is validated if it was not run on that platform or an agreed representative environment.

## Output Contract

```markdown
# QA Report

## Scope, Revision, and Environment

## Profile and Coverage Matrix

## Test Identities and Data

## Baseline Health

## Journeys Executed
| Journey | Role | Platform | Result | Evidence |

## Findings
### QA-001 — Title
- Severity:
- Environment:
- Preconditions:
- Steps:
- Expected:
- Actual:
- Evidence:
- Impact:
- Status:

## Accessibility and Platform Findings

## Console, Network, Log, and Monitoring Findings

## Remediation and Re-verification

## Untested or Blocked Areas

## Accepted Risks

## Ship-Readiness Decision
```

## Quality Gate

QA is complete only when:

- The required profile was actually executed.
- Critical user journeys and permission boundaries were tested.
- Evidence is reproducible and tied to a revision/environment.
- Pre-existing failures and untested areas are disclosed.
- Every fix was re-verified and regression-checked.
- Readiness follows evidence, not schedule pressure.

## Return Routes

- Expected behavior unclear → Requirements Specification.
- Failure cause unknown → Systematic Debugging.
- Automated proof needed → Test Engineering.
- Fix authorized → Incremental Implementation.
- Code assessment needed → Code Review.
- Release claim needed → Preflight Verification.
