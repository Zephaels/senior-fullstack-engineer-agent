# Task Classifier

## Purpose

Classify every operational software task before selecting process depth. The classifier prevents two opposite failures:

- Under-engineering a risky change
- Applying enterprise ceremony to a trivial change

The output is a classification record, not an estimate of how intelligent or difficult the work feels.

## Inputs

Use available evidence from:

- User request and supplied materials
- Current conversation and confirmed decisions
- Existing Project Ledger, specifications, and ADRs
- Repository layout and change surface
- Runtime, data, platform, security, operational, and compliance context
- Whether the task is Greenfield, Brownfield, Investigation, Review, or Delivery

Do not ask the user for facts that can be established from the repository or authoritative sources.

## Classification Levels

### Q — Quick Patch

Use when all relevant conditions are true:

- Change is local, reversible, and mechanically clear
- No material product ambiguity
- No public interface, persistent data, permission, security, payment, infrastructure, or migration impact
- Blast radius is small and readily inspected
- Existing project conventions provide an obvious implementation path
- Verification is simple and available

Typical examples:

- Correcting a typo in user-visible copy
- Renaming a private variable with references updated
- Fixing a deterministic style or formatting issue
- Adjusting a local test fixture without behavioral impact

Required minimum:

- Objective
- Affected files
- Scope check
- Minimal edit
- Relevant verification evidence
- Delivery summary

### S — Standard Change

Use when the task changes meaningful behavior but remains bounded.

Characteristics may include:

- One feature or defect with clear acceptance criteria
- Limited number of modules
- No new trust boundary
- No destructive data change
- Public behavior is limited and compatible
- Technical path is mostly established by the project
- Rollback is straightforward

Typical examples:

- Adding a validated form field
- Implementing a bounded API endpoint using existing patterns
- Fixing a defect that crosses UI and service layers
- Adding a background job with an established queue pattern

Required minimum:

- Brief and success criteria
- Repository or product context
- Acceptance criteria
- Impact analysis
- Implementation plan
- Relevant unit/integration/UI tests
- Code review and preflight evidence

### C — Complex Feature

Use when the task spans important system boundaries or contains material design uncertainty.

Any of the following commonly qualifies:

- Multiple modules, services, applications, or platforms
- New API contract or material contract change
- New persistent data model or non-destructive migration
- New asynchronous workflow, queue, cache, synchronization, or concurrency behavior
- Significant UX workflow or cross-platform adaptation
- New external provider or substantial dependency
- Performance, scale, reliability, observability, or rollback requirements
- Material product ambiguity or competing technical approaches
- Work cannot be safely completed in one simple vertical slice

Typical examples:

- Adding team collaboration to an existing SaaS
- Building a multi-step AI generation workflow
- Introducing offline synchronization
- Moving a module to an event-driven architecture
- Supporting Web, macOS, and Windows with shared business rules

Required minimum:

- Product or change brief
- Intent interview when material questions remain
- Testable requirement specification
- Repository discovery or Greenfield constraints
- Architecture and ADRs
- API/data/security/UX design as applicable
- Dependency and migration analysis
- Vertical-slice implementation plan
- Test matrix, QA, code review, security review, preflight
- Release, observability, and rollback plan

### X — Critical Change

Use when failure could materially affect security, privacy, money, irreversible data, legal obligations, production availability, or many users.

The task is automatically `X` when it involves any of the following in a material way:

- Authentication, authorization, privilege, identity, or tenant isolation
- Payment, billing, balances, transfers, subscriptions, tax, or financial records
- Secrets, cryptographic keys, sensitive personal data, regulated data, or data residency
- Destructive database migration, mass update, deletion, or irreversible transformation
- Production infrastructure, disaster recovery, critical availability, or fleet-wide rollout
- Public API incompatibility affecting external consumers
- Distributed consistency, exactly-once claims, financial idempotency, or high-contention concurrency
- Security boundary, file upload, untrusted code execution, agent tool permissions, or external action automation
- Legal, regulatory, safety, or contractual requirements
- AI-driven action that can publish, delete, spend, change permissions, or operate external systems
- A release where rollback is difficult or data compatibility is one-way

Typical examples:

- Changing role and permission semantics
- Integrating a production payment flow
- Migrating encrypted customer data
- Replacing an authentication provider
- Deploying an autonomous agent with write tools
- Modifying multi-tenant isolation

Required minimum:

Everything required by `C`, plus:

- Explicit decision ownership
- High-assurance specification for public behavior and failure semantics
- Threat model and privacy review
- Independent specification and engineering review
- Migration rehearsal or dry run where feasible
- Backup, rollback, and incident plan
- Staged rollout and health criteria
- Security, dependency, and secret scanning
- Explicit approval before irreversible or external side effects
- Post-release monitoring and verification window

## Classification Dimensions

Evaluate each dimension using facts rather than impressions.

| Dimension | Lower risk | Higher risk |
|---|---|---|
| Product ambiguity | Clear behavior and success | Unknown user, scope, business rule, or success |
| Change surface | Local private code | Multiple systems, platforms, or public contracts |
| Data | No persistence | Migration, sensitive data, irreversible change |
| Security | Existing trusted path | New identity, permission, trust boundary, or untrusted input |
| Operations | Local development | Production infrastructure, availability, cost, rollback |
| Concurrency | Sequential/local | Distributed state, races, retries, idempotency |
| Compatibility | Private implementation | External API, stored data, third-party integration |
| User impact | Small internal effect | Many users or critical workflow |
| Recoverability | Immediate rollback | One-way or difficult recovery |
| Evidence | Existing strong tests | Weak baseline or hard-to-reproduce behavior |

## Deterministic Upgrade Rules

Apply these rules after choosing the apparent level:

1. Any Critical Change trigger upgrades the task to `X`.
2. A task with two or more Complex Feature dimensions is at least `C`.
3. Unknown blast radius upgrades `Q` to at least `S`; if it crosses data, API, security, or platforms, upgrade to `C`.
4. Missing acceptance criteria for meaningful behavior requires intent or requirement work before implementation; do not classify uncertainty as a Quick Patch.
5. Production urgency does not lower the class. Use an incident path with safe containment, then complete the required follow-up.
6. User preference for speed may reduce documentation verbosity, but cannot remove security, permission, data, or evidence gates.
7. A requested rewrite is not automatically `C`; classify the actual behavior and risk. A rewrite with unclear purpose or broad blast radius is at least `C`.
8. A documentation-only change can remain `Q` unless it changes a public contract, compliance obligation, operational procedure, or safety instruction.

## Greenfield and Brownfield Modifier

Record one modifier:

- `G` — Greenfield
- `B` — Brownfield
- `I` — Investigation
- `R` — Review
- `D` — Delivery

Examples:

- `C-G`: Complex new product
- `S-B`: Bounded feature in an existing repository
- `X-B`: Critical permission migration in a production system
- `S-I`: Standard defect investigation
- `C-R`: Complex architecture review
- `X-D`: Critical production release

The modifier changes the first workflow, not the risk class.

## Classification Procedure

1. Restate the intended outcome.
2. Determine whether the task is operational.
3. Select the mode modifier.
4. Check every automatic Critical Change trigger.
5. Assess the classification dimensions.
6. Identify unknowns that could upgrade the class.
7. Choose the highest justified class.
8. State why it is not lower.
9. List required artifacts and gates.
10. Reclassify when new facts materially change risk.

## Output Contract

Use this compact record:

```yaml
classification:
  class: C
  mode: B
  label: C-B
  rationale:
    - Changes a public API and persistent data model
    - Spans frontend, backend, and database
  automatic_upgrades: []
  unresolved_upgrade_questions:
    - Whether existing clients require backward compatibility beyond one release
  required_artifacts:
    - change-brief
    - requirement-spec
    - architecture-decision
    - migration-plan
    - implementation-plan
    - test-matrix
  required_gates:
    - intent
    - specification
    - architecture
    - review
    - preflight
    - release
  permissions_required:
    - database-migration
```

## Examples

### Example 1: Copy correction

Request: “Change the button text from Submit to Save.”

Classification: `Q-B`, provided the text is not part of a regulated disclosure, public API, or business-rule distinction.

### Example 2: AI video workflow

Request: “Build an internal system that turns scripts into generated videos automatically.”

Classification: at least `C-G` because product workflow, providers, cost, assets, retries, cancellation, storage, permissions, and quality validation require design. Upgrade to `X-G` if autonomous publishing, paid spending, sensitive assets, or production write tools are involved.

### Example 3: Role model change

Request: “Let project editors invite other editors.”

Classification: `X-B` when it changes authorization or tenant boundaries, even if the UI change appears small.

### Example 4: Failing test

Request: “Fix this unit test.”

Classification: `Q-I` only if the test itself is wrong and behavior is clear. If the failing test indicates a product defect, unknown regression, or contract mismatch, classify the actual defect, not the one-line test edit.

## Anti-Patterns

Do not:

- Use file count as the only measure of complexity.
- Classify an authorization change as small because the diff is short.
- Classify a task as Quick because the user asked for speed.
- Add documentation to make a task appear controlled while skipping tests or safety gates.
- Keep a task at a lower class after discovering new risk.
- Treat classification as a one-time immutable label.
