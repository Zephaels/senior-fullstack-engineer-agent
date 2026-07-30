---
name: preflight-verification
description: Runs the final project-specific evidence gate before claiming work complete, creating a PR, merging, releasing, deploying, or handing off as verified. Use after implementation and required reviews to discover and execute the repository's real formatting, static analysis, build, test, security, runtime, migration, and packaging checks. Do not infer success from partial, stale, skipped, or delegated results.
---

# Preflight Verification

## Purpose

Provide a fresh, auditable answer to: “Is this exact revision ready for the requested next action?”

Preflight does not create product behavior, replace code review, or hide missing tests. It discovers the project-specific Definition of Done, runs the applicable checks, reads complete results, and reports readiness without exaggeration.

## When to Use

Use immediately before:

- Claiming a task, fix, feature, or migration is complete.
- Creating or updating a PR as ready for review.
- Merging or pushing to a protected branch.
- Releasing, deploying, publishing, or distributing an artifact.
- Marking a handoff as verified.
- Moving to the next implementation phase when the current phase has a formal gate.

## Do Not Use

Do not use to:

- Replace focused test-driven feedback during implementation.
- Diagnose unexplained failures; route them to [Systematic Debugging](../systematic-debugging/SKILL.md).
- Approve code that has not received required review.
- Claim platforms or environments that were not actually tested.
- Treat a skipped CI job, neutral check, cached result, or old report as fresh proof.
- perform merge, push, release, or deployment without permission.

## Core Rule

```text
No completion or readiness claim without fresh evidence for the exact revision and environment.
```

Confidence, prior successful runs, author reports, passing lint, or a green unrelated CI job are not substitutes.

## Preconditions

Identify:

- Repository root, branch, head revision, working tree, and target action.
- Task class and required gates.
- Approved requirements, architecture, plan, and Definition of Done.
- Code review, QA, security, migration, and risk decisions.
- Supported platforms and environments.
- Known pre-existing failures and accepted risks.
- Required permissions for external actions.

## Preflight Profiles

| Profile | Minimum use |
|---|---|
| Patch | Focused tests, static checks/build for affected surface, runtime proof |
| Standard | Full relevant test suite, build, lint/type, review evidence, smoke test |
| Complex | Standard plus integration/E2E, migration/compatibility, security, platform, observability |
| Critical | Complex plus independent review, rollback/recovery drill, production-like evidence and explicit approval |
| Release | Artifact integrity, versioning, changelog, package/deploy config, health checks and post-release plan |

Task risk can only increase the profile.

## Workflow

### Step 1: Establish the exact verification target

Record:

- Head revision and whether the tree is dirty.
- Base revision or general availability.
- Target action: claim complete, PR, merge, release, deploy, or handoff.
- Included and excluded platforms/environments.
- Required acceptance criteria and standing Definition of Done.

If uncommitted changes exist, results apply to the working tree and must be labeled as such.

### Step 2: Discover the repository's real commands

Read:

- Package manager and lockfiles.
- Build scripts and task runners.
- Language/toolchain configuration.
- Test, lint, formatting, type, security, packaging, migration, and deployment files.
- CI workflows and required status checks.
- Project documentation and contribution rules.

Create a command matrix. Do not invent generic commands when the repository defines its own.

### Step 3: Validate prerequisite artifacts

Confirm:

- Requirements and acceptance criteria are addressed.
- Architecture and ADR changes are recorded.
- Implementation plan tasks are resolved or explicitly deferred.
- Code Review has no unresolved Critical/Required finding.
- Required QA, security, performance, accessibility, migration, and platform checks have evidence.
- Project state is current.

A passing test suite cannot compensate for missing product or security approval.

### Step 4: Run checks in failure-efficient order

A typical order is:

1. Working-tree and generated-artifact sanity.
2. Format verification.
3. Static analysis, type check, lint, schema validation, and secret scan.
4. Focused tests.
5. Full relevant unit, integration, contract, component, and E2E suites.
6. Build and package.
7. Migration, compatibility, rollback, or data integrity checks.
8. Runtime smoke and platform-specific verification.
9. Security, performance, accessibility, and operational checks required by risk.
10. Artifact checksum, version, changelog, and release configuration.

Run the complete command, read the full output, capture exit status, and retain artifacts. Stop on a blocker unless continuing is necessary to collect independent failures safely.

### Step 5: Interpret CI and status checks carefully

- Identify which commit each check applies to.
- Distinguish success, failure, cancelled, skipped, neutral, stale, and pending.
- A skipped or neutral check may be treated as success by a platform but may not satisfy the project’s actual evidence requirement.
- Confirm required checks and branch protections rather than assuming all green indicators are equivalent.
- Do not trust an Agent-reported success without verifying the diff and results.

### Step 6: Reconcile failures

Classify each failure:

- Introduced by this change.
- Pre-existing and unrelated.
- Environment/tooling issue.
- Flaky/nondeterministic.
- Missing requirement or architecture decision.
- Missing permission or external dependency.

Do not waive failures silently. Route unexplained failures to Systematic Debugging and record the preflight as failed or blocked.

### Step 7: Verify completion claims line by line

For every claim such as “fixed,” “tests pass,” “build succeeds,” “works on mobile,” or “ready to deploy,” identify the exact evidence.

Examples:

- “All tests pass” requires the complete intended test command and counts.
- “Bug fixed” requires the original scenario and regression proof.
- “Build succeeds” requires the build command and exit 0.
- “Requirements complete” requires traceability against acceptance criteria.
- “Ready to deploy” requires release, environment, migration, health, monitoring, and rollback gates.

### Step 8: Produce a readiness decision

Use one:

- `PASS`: all mandatory evidence for the target action is fresh and successful.
- `PASS_WITH_ACCEPTED_RISK`: only explicitly approved, non-blocking risk remains.
- `FAIL`: a required check failed or a blocker remains.
- `BLOCKED`: required environment, permission, service, identity, or evidence was unavailable.
- `PARTIAL`: only a narrower claim is supported; state exactly what is and is not proven.

### Step 9: Update Project State

Record:

- Revision, environment, commands, timestamps, results, and artifacts.
- Accepted risks and approvals.
- Failed, skipped, unavailable, or stale evidence.
- Exact next action and required permission.

## Output Contract

```markdown
# Preflight Verification Report

## Target Action and Revision

## Task Class and Profile

## Working-Tree and Artifact State

## Governing Requirements and Definition of Done

## Prerequisite Review Evidence

## Command Matrix
| Check | Command | Environment | Required | Result | Evidence |

## CI and Status Checks

## Runtime, Platform, and User-Flow Evidence

## Security, Data, Migration, and Operational Evidence

## Failures, Skips, Flakes, and Pre-existing Issues

## Accepted Risks and Approvals

## Supported Claims

## Unsupported Claims

## Readiness Decision

## Exact Next Action and Permission Required
```

## Completion Gate

Preflight passes only when:

- Evidence applies to the exact revision/working tree.
- All required commands actually ran and their outputs were read.
- Acceptance criteria and Definition of Done are satisfied.
- Required review, QA, security, migration, and platform evidence is present.
- Skipped, neutral, flaky, stale, or unavailable checks are not misrepresented.
- No unresolved Critical/Required finding remains.
- The report distinguishes tested from untested platforms and environments.
- External actions remain gated by permission.

## Return Routes

- Test failure or missing test → Test Engineering / Systematic Debugging.
- Runtime user-flow gap → Quality Assurance.
- Code-quality or compliance issue → Code Review.
- Requirement or architecture gap → upstream owning workflow.
- PASS and release requested → Release/Deployment workflow when installed.
- Handoff requested → Project State and Handoff.
