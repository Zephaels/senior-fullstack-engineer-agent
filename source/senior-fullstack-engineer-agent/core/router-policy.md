# Router Policy v2

## Objective

Select the smallest sufficient Skill while preserving lifecycle safety. The root orchestrator coordinates complex, ambiguous, or multi-phase work; it does not compete with a specialist Skill for a bounded request.

## Selection Order

1. **Direct specialist match** — If one Skill clearly covers the requested outcome, select it.
2. **Ambiguity resolution** — If the route depends on a material product decision, use `intent-interview`; if it depends on repository facts, use `repository-discovery`; if it depends on current external facts, use `source-verification`.
3. **Full-lifecycle orchestration** — Use the root orchestrator only when the task crosses at least three phases, changes major system semantics, or has no clear specialist route.
4. **Safety upgrade** — Add security, migration, or release gates only when risk requires them; do not trigger them merely because they exist.

## Tie-Break Rules

- `systematic-debugging` beats implementation when the cause is unknown.
- `requirements-specification` beats architecture when product behavior is unresolved.
- `architecture-design` beats implementation planning when interfaces, state, data, migration, or failure semantics are unresolved.
- `test-engineering` designs test evidence; `quality-assurance` executes user-facing validation.
- `code-review` evaluates the diff; `preflight-verification` executes exact release/merge checks.
- `source-verification` verifies external claims; `repository-discovery` establishes local facts.
- `release-deployment` performs authorized deployment; `preflight-verification` does not deploy.

## Full-Lifecycle Threshold

Use the root orchestrator when any condition is true:

- Greenfield product or system.
- Three or more lifecycle phases are explicitly requested.
- A change spans product semantics, architecture, implementation, and delivery.
- Public contract, authorization model, persistence model, deployment topology, or cross-platform behavior changes materially.
- The user explicitly requests end-to-end ownership.

Do not use the root orchestrator merely because a bounded task is important.

## Routing Evidence

Record:

- selected Skill or route;
- reason and rejected alternatives;
- task class and risk upgrades;
- missing facts or permissions;
- expected next artifact and completion evidence.
