# GitHub Release and Attestation Runbook

## Repository preparation

- Use a dedicated repository for this project.
- Enable Actions and required workflow permissions.
- Decide public/private visibility. Artifact attestations on Free/Pro/Team require a public repository; private/internal attestation requires Enterprise Cloud.
- Enable release immutability before GA.
- Protect the default branch and require CI.

## RC release

1. Merge only validated source.
2. Create and push the exact SemVer tag.
3. Build archives from the tagged commit.
4. Create a draft release.
5. Require `release-evidence/<VERSION>/scorecard.json` with `GA_GATE_PASS`.
6. Require the independent security, independent Judge, and staging autonomy rehearsal reports defined in `release-evidence/README.md`.
7. Query GitHub check runs for the exact tagged commit and require successful CI and CodeQL.
8. Attach Plugin, Source, checksums, SBOM, manifest and every qualification report.
9. Generate provenance attestations for every release archive; attestation is not optional.
10. Verify tag, checksums and every attestation with `gh attestation verify`.
11. Publish the draft only after `validate_public_release.py` and every previous step pass.

## Verification evidence

Preserve workflow URL, commit SHA, tag, release URL, artifact hashes, attestation IDs, `gh attestation verify` output and release integrity verification output.
