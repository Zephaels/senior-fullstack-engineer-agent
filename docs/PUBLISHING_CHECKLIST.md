# Publishing Checklist

Every item is mandatory for public `v1.0.0` GA.

- [ ] `VERSION` is exactly `1.0.0` and the signed tag is exactly `v1.0.0`.
- [ ] Source, Plugin, Marketplace, link, schema, manifest, and SBOM validation pass.
- [ ] Root and Eval Engine unit tests pass on the exact tagged commit.
- [ ] Trigger, Behavior RED/GREEN, Pressure, Plugin Regression, Brownfield E2E, installer, and bounded-autonomy gates all pass in `release-evidence/1.0.0/scorecard.json`.
- [ ] Public metadata is explicitly approved and every required HTTPS URL exists.
- [ ] Local deterministic release security review passes with zero findings.
- [ ] An independent deep repository security assessment for the exact commit reports zero open critical or high findings and has a verifiable evidence digest.
- [ ] A different-model-family, isolated Judge verifies all 230 Trigger, 57 Behavior, 80 Pressure, and 60 Regression cases.
- [ ] A real staging or preproduction autonomy rehearsal proves dry run, canary, health gates, rollback fault injection, and zero unauthorized actions.
- [ ] GitHub CodeQL and CI checks pass on the exact tagged commit.
- [ ] Archives build twice with identical SHA-256 values and a fixed `SOURCE_DATE_EPOCH`.
- [ ] License, NOTICE, third-party notices, SECURITY, support, privacy, and terms are reviewed.
- [ ] Release notes and packaged content match.
- [ ] A draft GitHub Release contains all archives, checksums, manifests, SBOM, and qualification evidence.
- [ ] Artifact attestations are generated for every release archive and `gh attestation verify` succeeds.
- [ ] Immutable Releases, branch protection, secret scanning, and push protection are enabled.
- [ ] The draft is published only after every preceding gate passes.
