# Release Process

1. Freeze scope and choose a strict semantic version.
2. Run source validation and all static evaluation-schema checks.
3. Build the Codex Plugin from a clean authoring snapshot.
4. Validate plugin and marketplace contracts.
5. Build source, plugin, and repository archives twice and compare hashes.
6. Generate SHA-256 checksums, file manifest, and SPDX SBOM.
7. Run real-host installation/discovery tests.
8. Run real-model RED → GREEN → Regression evaluation.
9. Complete security and license review.
10. Publish only at the evidence-supported release class.

`RC_READY` does not imply `GA_READY`.
