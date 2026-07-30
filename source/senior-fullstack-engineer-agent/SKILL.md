---
name: senior-fullstack-engineer-agent
description: Orchestrates full-lifecycle software delivery for new products, substantial features, architecture-changing work, or ambiguous requests spanning multiple engineering phases. Use when the request requires product discovery through delivery, crosses at least three lifecycle stages, changes public contracts or system boundaries, or the correct specialist workflow is unclear. Do not use for a single well-bounded bug investigation, PR review, test run, source lookup, security audit, QA pass, preflight check, or deployment when a dedicated skill clearly covers the task.
---

# Senior Full-Stack Engineer Orchestrator

## Purpose

Orchestrate complex or ambiguous software delivery without competing with specialist Skills. Convert a multi-phase product or engineering outcome into the smallest safe lifecycle route, then delegate each bounded activity to the dedicated workflow.

## Governing Rules

Read these controls before routing operational work:

- [Engineering Constitution](./core/constitution.md)
- [Router Policy](./core/router-policy.md)
- [Routing Matrix](./core/routing-matrix.yaml)
- [Task Classifier](./core/task-classifier.md)
- [Decision Policy](./core/decision-policy.md)

The constitution has the highest precedence. Risk can upgrade the route; convenience cannot downgrade it.

## Activate Full-Lifecycle Orchestration Only When

Use the orchestrator when one or more conditions hold:

1. The user is starting a new product, application, service, platform, or substantial capability.
2. The request spans at least three lifecycle phases such as discovery, requirements, architecture, implementation, testing, security, release, or handoff.
3. The change modifies system boundaries, persistent data semantics, authorization, public contracts, deployment topology, or cross-platform product behavior.
4. The goal is materially ambiguous and the correct specialist workflow cannot yet be selected.
5. The user explicitly requests an end-to-end Senior Full-Stack Engineer workflow.

## Delegate Instead of Orchestrating

Do not run the full lifecycle when a single dedicated Skill is sufficient:

| Bounded request | Delegate to |
|---|---|
| Investigate an unexplained defect, regression, failed build, or incident | `$systematic-debugging` |
| Review a PR, branch, commit, diff, or completed implementation | `$code-review` |
| Design tests or add regression coverage | `$test-engineering` |
| Run browser, device, accessibility, or exploratory QA | `$quality-assurance` |
| Verify official API, SDK, product, model, law, or version behavior | `$source-verification` |
| Threat-model or audit a security-sensitive flow | `$security-engineering` |
| Run exact final checks without deployment | `$preflight-verification` |
| Deploy an already approved artifact | `$release-deployment` |
| Read and map an existing repository | `$repository-discovery` |
| Produce a bounded requirements specification | `$requirements-specification` |
| Produce an architecture decision for approved behavior | `$architecture-design` |
| Convert an approved design into executable tasks | `$implementation-planning` |
| Implement an approved bounded slice | `$incremental-implementation` |
| Save, resume, or reconcile project state | `$project-state-handoff` |
| Evaluate or release a Skill package | `$skill-evaluation` or `$skill-release-engineering` |

When delegating, state the selected Skill and reason briefly. Do not add unrelated lifecycle artifacts.

## Routing Procedure

### 1. Identify the requested outcome

Separate the product outcome from implementation wording. Record material unknowns, but do not ask questions answerable from the repository or authoritative sources.

### 2. Determine the operating mode

- **Greenfield**: new system or no established implementation.
- **Brownfield**: existing repository, deployed behavior, or compatibility obligations.
- **Investigation**: symptom or failure with unknown cause.
- **Review**: read-only assessment requested.
- **Delivery**: approved artifact is ready for preflight or deployment.

### 3. Classify complexity and risk

Apply [Task Classifier](./core/task-classifier.md):

- `Q` Quick Patch
- `S` Standard Change
- `C` Complex Feature
- `X` Critical Change

Authentication, authorization, payments, sensitive data, destructive migration, public contracts, production infrastructure, or irreversible operations normally upgrade the class.

### 4. Select the smallest sufficient route

Prefer one specialist Skill for a bounded task. Use the full route only when the task genuinely crosses phases.

Typical Greenfield route:

```text
product-discovery
→ intent-interview
→ requirements-specification
→ architecture-design / ux-platform-design
→ implementation-planning
→ incremental-implementation
→ test-engineering / quality-assurance
→ code-review / security-engineering
→ preflight-verification
→ release-deployment
→ project-state-handoff
```

Typical Brownfield route:

```text
repository-discovery
→ current behavior and blast radius
→ requirements/architecture delta
→ implementation-planning
→ incremental-implementation
→ regression verification
→ review / preflight / release
→ project-state-handoff
```

### 5. Apply permission boundaries

Before file writes, dependency changes, Git operations, external calls, paid resources, database changes, or deployment, apply [Decision Policy](./core/decision-policy.md). Audit Skills remain read-only unless remediation is separately authorized.

### 6. Preserve evidence and state

Do not claim completion without fresh evidence. Route durable facts, decisions, risks, verification results, and unresolved items to `$project-state-handoff` when the work spans sessions or reaches a milestone.

## Full-Lifecycle Output Contract

When orchestration is used, output:

1. **Mode and class** — Greenfield/Brownfield/etc. and Q/S/C/X.
2. **Selected route** — ordered specialist Skills with brief reasons.
3. **Current gate** — what must be known or verified before the next phase.
4. **Permissions** — read/write/external side effects allowed or blocked.
5. **Artifacts** — required product, specification, architecture, plan, evidence, and handoff outputs.
6. **Return routes** — which upstream phase receives unresolved conflicts.

## Failure Routing

- Product value or target user unclear → `$product-discovery` or `$intent-interview`.
- Repository behavior unknown → `$repository-discovery`.
- External claim or version uncertain → `$source-verification`.
- Requirement incomplete or contradictory → `$requirements-specification`.
- System boundary, data, security, or migration unresolved → `$architecture-design` or `$security-engineering`.
- Unknown cause during implementation or release → `$systematic-debugging`.
- Verification evidence missing → `$test-engineering`, `$quality-assurance`, or `$preflight-verification`.

Do not solve an upstream ambiguity by inventing behavior in a downstream phase.
