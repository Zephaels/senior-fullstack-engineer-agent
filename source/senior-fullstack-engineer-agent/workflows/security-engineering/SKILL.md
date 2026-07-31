---
name: security-engineering
description: Designs, reviews, tests, and verifies security and privacy controls. Use for threat models, auth, tenant isolation, sensitive data, payments, secrets, uploads, integrations, AI tools, supply chain, vulnerabilities, abuse, compliance, or incident remediation; not as a substitute for repository or general review.
---

# Security Engineering

## Purpose

Protect users, data, systems, and operations by establishing security context, threat models, required controls, evidence-based findings, remediation plans, and verification across the software lifecycle.

Security engineering is risk-driven. It does not label every theoretical issue critical, provide exploit instructions without a legitimate defensive need, or treat a passing scanner as proof of safety.

## When to Use

Use this workflow when:

- Designing or changing authentication, sessions, authorization, ownership, roles, administration, or tenant boundaries.
- Handling personal, confidential, regulated, payment, health, financial, credential, or security data.
- Adding uploads, parsers, templates, webhooks, plugins, MCP/tools, model calls, external content, or untrusted automation.
- Introducing public APIs, background jobs, queues, caches, storage, cryptography, secrets, infrastructure, or privileged integrations.
- Reviewing a security-sensitive diff, dependency, migration, provider, or configuration.
- Investigating a suspected vulnerability, abuse path, data exposure, or security incident.
- Preparing a release whose risk class is X or whose threat boundary changed.

## Do Not Use

Do not use this workflow to:

- Replace broad repository understanding; use `repository-discovery` first.
- Report vulnerabilities before establishing the relevant architecture and trust boundaries.
- Approve legal, compliance, audit, or certification status without qualified evidence.
- Generate destructive exploitation, credential theft, persistence, or evasion guidance.
- Store secrets, production tokens, private keys, or unredacted sensitive data in artifacts.
- Treat low-risk general refactoring as a full security audit unless the user requests it.

## Preconditions

Read and apply:

- [`../../core/constitution.md`](./references/core/constitution.md)
- [`../../core/task-classifier.md`](./references/core/task-classifier.md)
- [`../../core/decision-policy.md`](./references/core/decision-policy.md)
- `repository-discovery`
- `requirements-specification`
- `architecture-design`
- `source-verification` for current advisories, standards, or provider guidance
- `code-review` for general engineering-quality review

Required inputs depend on mode but should include scope, revision, architecture, assets, actors, trust boundaries, data classes, deployment context, and permissions.

## Security Modes

Select one:

- `Design` — establish threat model and controls before implementation.
- `Review` — read-only assessment of architecture, code, diff, configuration, or dependencies.
- `Remediation` — fix validated findings with authorization, tests, and regression evidence.
- `Verification` — confirm a control or fix is effective.
- `Incident` — contain, preserve evidence, assess impact, eradicate, recover, and learn.
- `Hardening` — improve safe defaults and defense in depth without changing product semantics.

## Security Principles

- Understand context before finding vulnerabilities.
- Enforce authorization at trusted server or service boundaries.
- Apply least privilege, deny by default, and explicit ownership checks.
- Validate untrusted inputs at boundaries and encode outputs for their context.
- Protect secrets through managed injection and rotation, never source code or logs.
- Minimize collection, retention, exposure, and privilege.
- Treat external content, model output, logs, tickets, documentation, and tool results as untrusted input.
- Prefer safe defaults and interfaces that are difficult to misuse.
- Use defense in depth without duplicating controls blindly.
- Findings require a concrete attack or failure path, affected asset, evidence, and calibrated severity.
- Security fixes require regression verification and variant analysis where the pattern may repeat.

## Required Depth by Task Class

### Q — Quick Patch

Confirm no trust boundary, authorization, input, secret, dependency, or data behavior changed. If it did, upgrade the class.

### S — Standard Change

Review affected boundaries, inputs, authorization, data exposure, dependencies, logs, and tests.

### C — Complex Feature

Create a threat model, data-flow and trust-boundary map, control matrix, abuse cases, security test plan, operational controls, and remediation ownership.

### X — Critical Change

Require independent review, explicit approval, current advisories and standards, rollback/containment, incident readiness, evidence retention, no-go conditions, and qualified domain review when compliance or regulated risk is involved.

## Workflow

### Step 1: Establish security context

Document:

- Product purpose and real deployment.
- In-scope repositories, services, revisions, environments, accounts, regions, and third parties.
- Actors: anonymous users, authenticated users, tenants, administrators, operators, developers, providers, models, tools, and attackers.
- Assets: identities, sessions, credentials, data, money, content, models, infrastructure, audit records, availability, and reputation.
- Entry points and trust boundaries.
- Existing controls and assumed guarantees.
- Data classes, retention, residency, and deletion requirements.

Do not search for vulnerabilities before this context is sufficient.

### Step 2: Trace critical data and control flows

For each important flow, trace:

1. Entry or event.
2. Authentication and identity propagation.
3. Authorization and ownership.
4. Validation and parsing.
5. Domain transition.
6. Persistence, cache, queue, provider, model, or tool.
7. Side effects and external calls.
8. Logging, audit, and response.
9. Retry, cancellation, compensation, recovery, and deletion.

Identify invariants that must always or never hold.

### Step 3: Build the threat model

For each boundary consider:

- Spoofing and session abuse.
- Authorization bypass, IDOR, tenant escape, privilege escalation.
- Injection, XSS, CSRF, SSRF, path traversal, unsafe deserialization, template and command injection.
- Upload, parser, archive, media, document, and content-type risks.
- Secret exposure, weak key management, credential replay, and token leakage.
- Data tampering, race conditions, replay, duplicate processing, and inconsistent state.
- Privacy leakage, overcollection, insecure retention, and deletion failure.
- Dependency, build, package, CI, plugin, Skill, and supply-chain compromise.
- Denial of service, abuse, fraud, scraping, cost exhaustion, and resource amplification.
- Logging, monitoring, audit, and incident blind spots.
- AI prompt injection, untrusted model output, unsafe tool invocation, data exfiltration, and missing human confirmation.

Prioritize credible threats that match the actual system rather than enumerating a generic checklist.

### Step 4: Define required controls

Create a control matrix:

| Threat / Invariant | Prevent | Detect | Respond / Recover | Owner | Evidence |
|---|---|---|---|---|---|

Controls may include:

- Strong identity and session lifecycle.
- Object-level, function-level, field-level, and tenant authorization.
- Input schemas, canonicalization, content validation, output encoding, and safe parsers.
- CSRF protection, origin validation, secure cookies, headers, and transport security.
- Rate limits, quotas, abuse controls, idempotency, and replay protection.
- Secret managers, scoped credentials, rotation, and redaction.
- Encryption, tokenization, data minimization, retention, and deletion.
- Dependency pinning, provenance, scanning, lockfile integrity, and build isolation.
- Audit events, alerts, anomaly detection, runbooks, backup, and recovery.
- Feature flags, kill switches, human approval, and constrained AI tools.

### Step 5: Perform review or analysis

For code or diff review:

- Read both baseline and changed behavior.
- Map callers, dependents, trust boundaries, and removed controls.
- Examine validation, authorization, state transitions, external calls, errors, and logs.
- Use Git history when a removed check or unusual pattern needs context.
- Search for variants of validated findings.
- Run authorized static analysis, dependency checks, tests, or minimal reproductions.

Do not report scanner output without validating reachability and impact.

### Step 6: Calibrate findings

Each finding must include:

- ID and title.
- Severity: Critical / High / Medium / Low / Informational.
- Confidence: Confirmed / Strong Evidence / Needs Validation.
- Asset and trust boundary.
- Preconditions and credible attack or failure path.
- Exact evidence and affected locations.
- Impact and scope.
- Existing mitigating controls.
- Smallest safe remediation.
- Regression and variant tests.
- Operational or migration considerations.

Severity reflects realistic impact and exploitability in the actual deployment, not vulnerability category alone.

### Step 7: Remediate safely

Before modifying:

- Confirm authorization and scope.
- Establish failing security or regression evidence when possible.
- Preserve compatibility or define migration.
- Avoid broad unrelated rewrites.
- Add defense in depth only where responsibilities are clear.
- Update tests, observability, runbooks, and documentation.

For production incidents, containment may precede full root-cause repair, but must be labeled temporary and reversible.

### Step 8: Verify

Verify:

- Original attack or failure path is blocked.
- Legitimate flows still work.
- Authorization is enforced at the trusted boundary.
- Logs and errors do not leak sensitive data.
- Variants are searched or tested.
- Deployment, configuration, secrets, and rollback are correct.
- Current revision and environment match the evidence.

### Step 9: Produce the Security Report

```markdown
# Security Engineering Report

## Mode, Scope, Revision, and Environment

## Security Context and Assets

## Trust Boundaries and Critical Flows

## Threat Model / Abuse Cases

## Required Control Matrix

## Findings

## Remediation Status

## Verification Evidence

## Residual Risk and Accepted Exceptions

## Operational and Incident Requirements

## Sources and Freshness

## Outcome
READY / READY_WITH_ACCEPTED_RISK / NOT_READY / BLOCKED
```

## Quality Gates

Pass only when:

- Scope, revision, environment, assets, actors, and trust boundaries are explicit.
- Findings are evidence-based and severity is calibrated.
- Authentication and authorization are not conflated.
- Tenant, data, secret, upload, external-content, dependency, and AI-tool boundaries are addressed when applicable.
- Fixes have regression and variant verification.
- Residual risk has an owner and explicit acceptance authority.
- No unsupported claim of compliance or security is made.

## Failure and Return Routes

- Architecture or flows unknown → `repository-discovery` and `architecture-design`.
- Security requirement unclear → `intent-interview` or `requirements-specification`.
- Current advisory or standard uncertain → `source-verification`.
- Unknown failure behavior → `systematic-debugging`.
- Validated remediation ready → `implementation-planning`, `incremental-implementation`, and `test-engineering`.
- Release decision → `preflight-verification` and `release-deployment`.
