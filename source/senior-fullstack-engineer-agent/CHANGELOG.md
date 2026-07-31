## [1.0.0-rc.4.8] - 2026-07-30

- Added a self-contained, default-dry-run bounded autonomy supervisor with exact run plans, leases, checkpoints, hard deadlines, deterministic transient retry rules, health gates, redacted evidence, and preauthorized rollback.
- Bound every production command to an absolute trusted executable and SHA-256 digest; artifact and executable identities are revalidated during execution.
- Added a real Brownfield Plugin E2E fixture and gate that verifies automatic specialist routing, exact changed-file scope, and independent post-run tests.
- Added bounded-autonomy and Brownfield E2E requirements to the GA scorecard. Real Codex runtime qualification remains blocked by the current host transport failure.
- Removed shell-based Eval Runner and Judge execution, pinned every GitHub Action to a verified commit, made artifact attestation mandatory, and added pre-publication metadata, check-run, security, and reproducible-build gates.
- Added strict public-GA evidence contracts for an independent deep security assessment, a different-model-family isolated Judge, and a real staging autonomy rehearsal; sparse `PASS` placeholders are rejected.
- Classified the exhausted Brownfield probe as a Codex host/runtime blocker while preserving its original failed probe evidence and keeping the GA gate closed.
- Restricted unattended child processes to an explicit environment-variable allowlist with required-value digests, switched workspace drift checks to content hashes, durably flushed evidence journals, and made snapshot failures fail closed with rollback after deployment.

## [1.0.0-rc.4.7] - 2026-07-30

- Added bounded production autonomy with explicit preauthorization envelopes, default-deny scopes, watchdogs, circuit breakers, health gates, and automatic rollback boundaries.
- Added a deterministic autonomy-envelope schema, template, validator, and policy regression tests.
- Added fresh-session retries for classified Codex App Server transport failures and structured exhaustion evidence; non-transient policy or validation failures are never retried.
- Added isolated RED/GREEN configuration selection so failed or blocked evidence can be resumed without rerunning completed configurations.
- Confirmed the current Codex host remains transport-blocked after two fresh supervised retries; GA remains blocked and no model score was fabricated.

## [1.0.0-rc.4.6] - 2026-07-30

- Proved real RED/GREEN improvement for seven Behavior cases; every evaluated RED failed and every corresponding GREEN passed under fresh same-model-family Judge sessions.
- Expanded Behavior coverage from 13 to all 19 specialist Skills with 57 official cases and added bounded case selection.
- Added a deterministic synthetic Brownfield monorepo fixture and isolated read-only workspace materialization for repository-aware evaluation.
- Fixed Behavior resume provenance so repeated resumes retain input fingerprints and do not rerun valid evidence.
- Hardened the Scorecard so partial Behavior, Pressure, or Plugin Regression success cannot satisfy GA coverage gates.
- Completed Trigger at 230/230 with 100% precision/recall, 0% false-positive rate, 100% route accuracy, and zero must-not-route violations.
- Added declared companion-route contracts without weakening undeclared-extra-Skill detection.
- Added pressure-runner revision provenance, isolated Git-backed fixtures, least-privilege App Server command approval, and product-file hash verification.
- Proved the first three real Pressure cases at 3/80 with 100% pass rate and zero critical violations; full Pressure coverage remains a GA blocker.

## [1.0.0-rc.4.5] - 2026-07-30

- Completed all 230 metadata-first Trigger runs with 100% precision, recall, and false-positive compliance; exact route accuracy is 99.13% with one valid security companion route retained as evidence.
- Added checkpoint/resume, stale-definition rejection, and provenance fingerprints to Trigger, Behavior, Pressure, and Plugin Regression runners.
- Corrected the official Trigger suite from 288 mixed cases to 230 canonical cases and separated the 60 Plugin Regression cases.
- Made specialist Skill references self-contained and removed runtime cross-Skill file links.
- Generated the Skill catalog from canonical frontmatter and validated catalog drift.
- Proved isolated Marketplace installation and discovery of exactly 20 candidate Skills in a real Codex App Server session.

## [1.0.0-rc.4.4] - 2026-07-30

- Fixed Windows UTF-8 validation and long-path transactional installation failures.
- Fixed Windows runner/judge command quoting and added functional protocol regression tests.
- Fixed Plugin-namespaced Skill normalization and the regression grader's expected-route field.
- Corrected the qualification decision to the allowed `RC_BLOCKED` value when gates remain incomplete.
- Clarified specialist routing for bounded authorization audits and rebalanced architecture trigger cases.
- Required blocked incremental implementations to emit an explicit partial Scope Lock; the failing real GREEN case passed after remediation.
- Recorded 20/20 runtime Skill discovery and the upstream Plugin-enabled `codex exec` timeout blocker without claiming GA.

## [1.0.0-rc.4.3] - 2026-07-30

- Narrowed the root Skill to multi-phase orchestration and explicit end-to-end work.
- Added Router v2 policy, routing matrix, and root trigger evaluations.
- Added metadata-first Trigger Eval, isolated RED/GREEN Behavior Eval, and true Plugin runtime Regression adapter contracts.
- Added deterministic routing graders, independent semantic judge protocol, and GA-blocking Scorecard generation.
- Added transactional install, upgrade, rollback, uninstall, verify, lock, state, atomic marketplace writes, and failure recovery.
- Expanded static validation for Skill sync, Eval IDs, Trigger balance, UI metadata, schemas, generated caches, and RC evidence.

## [1.0.0-rc.3] - 2026-07-30

### Status

- Reclassified the feature-complete 1.0 package as an RC qualification candidate.
- Added a real Codex installation, discovery, trigger, behavior, pressure, regression, upgrade, and uninstall test plan.
- Added a Codex execution prompt and qualification result template.
- Preserved all 20 lifecycle Skills, templates, schemas, evaluation data, validators, plugin metadata, and release engineering files.

### GA blockers

- Real Codex runtime discovery must pass.
- Real RED → GREEN → Regression model evidence must pass.
- Failures must be remediated and the full regression suite rerun.
- GitHub Release and artifact attestation must be generated and verified.
