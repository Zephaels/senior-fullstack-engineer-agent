# 1.0.0-rc.4.8 RC Qualification Notes

This build contains the complete planned 1.0 lifecycle and is ready for controlled Codex qualification.
It is not a GA release. A GA tag requires real host installation, real Skill discovery, real RED/GREEN/Regression evidence, remediation of observed failures, full regression, and verified release provenance.

The Windows qualification run verified filesystem installation and 20/20 runtime Skill discovery, then found and fixed UTF-8 decoding, long staging path, namespaced route grading, regression-field, Windows command quoting, decision-label, blocked Scope Lock, isolated Skill-context loading, and repository-fixture defects. The metadata-first Trigger suite is complete at 230/230 with 100% route accuracy and zero must-not-route violations. Seven of 57 Behavior cases now have real RED/GREEN evidence, with every evaluated RED failing and every corresponding GREEN passing. Three of 80 Pressure cases passed with zero critical violations; P3-011 used an isolated Git-backed fixture, fresh current-revision checks, a least-privilege command allowlist, and product-file hash verification. One of 60 Plugin Regression cases passed through a real isolated Codex App Server session. Judges ran in fresh sessions but remain in the same model family, so this is not cross-model evidence. Full Behavior, Pressure, Plugin Regression, and Brownfield end-to-end qualification remain incomplete, so GA stays blocked.

Use `CODEX_TEST_INSTRUCTIONS.md` and `docs/CODEX_RC_TEST_PLAN.md`.
