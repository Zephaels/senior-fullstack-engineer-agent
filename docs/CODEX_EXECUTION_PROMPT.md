# Exact prompt to give Codex

You are the release-qualification engineer for `senior-fullstack-engineer-agent` version `1.0.0-rc.4.8`.

Work in this repository. Do not tag, publish, push, deploy, create paid resources, change permissions, use production secrets, or call the package GA. Start read-only.

1. Read `CODEX_TEST_INSTRUCTIONS.md`, `docs/CODEX_RC_TEST_PLAN.md`, `SECURITY.md`, and the root `README.md`.
2. Inspect the repository and identify the exact source tree, plugin tree, marketplace entry, evaluation suites, validators, and release scripts.
3. Create an isolated branch or worktree for qualification evidence. Do not modify Skill content during the baseline pass.
4. Execute the complete RC test plan, including real Codex installation and discovery, trigger positive and negative tests, RED → GREEN → Regression behavior tests, critical pressure tests, Brownfield workflow, upgrade/cache/uninstall tests, and static release gates.
5. Preserve exact commands, versions, prompts, outputs, tool calls, exit codes, hashes, screenshots or transcripts, and timestamps under `qualification-results/`.
6. Never count mock, skipped, blocked, cached, stale, or unexecuted results as passes. Standalone Skill fallback does not prove Plugin discovery.
7. If a real Skill or router failure is found, first preserve a failing regression case, classify the failure, create a separate remediation branch or worktree, make the smallest safe correction, bump the version if distributed content changes, and rerun the failed case plus the full regression suite.
8. Fill `docs/CODEX_RESULT_TEMPLATE.md` and produce `qualification-results/SCORECARD.json`.
9. End with exactly one decision: `GA_READY`, `RC_READY_WITH_ACCEPTED_RISK`, or `RC_BLOCKED`.
10. Report all work actually executed, all files changed, tests and evidence, unverified items, known risks, and the exact next action.

Do not ask me questions that the repository, Codex environment, or official documentation can answer. Ask only when a product decision, risk acceptance, credential or permission, or irreversible external action genuinely requires human input.
