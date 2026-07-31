# Release Process

1. Freeze scope and choose a strict semantic version.
2. Run source validation and all static evaluation-schema checks.
3. Build the Codex Plugin from a clean authoring snapshot.
4. Validate Plugin and Marketplace contracts.
5. Build source, Plugin, and repository archives twice and compare hashes.
6. Generate SHA-256 checksums, file manifests, and SPDX SBOMs.
7. Run real-host installation and discovery tests.
8. Run real-model RED -> GREEN -> Regression, Pressure, and Brownfield Plugin E2E evaluation.
9. Qualify bounded production autonomy, including trusted executables, health gates, deadlines, and rollback.
10. Complete local security review and an independent deep security assessment with zero open critical or high findings.
11. Complete a cross-model isolated Judge pass and a real staging autonomy rehearsal with rollback fault injection.
12. Complete GitHub CodeQL, license, public metadata, support, privacy, and terms review.
13. Create a draft release, generate mandatory attestations, and verify every archive with `gh attestation verify`.
14. Publish only after `validate_public_release.py` passes for the exact tagged commit.

`RC_READY` does not imply `GA_READY`.
