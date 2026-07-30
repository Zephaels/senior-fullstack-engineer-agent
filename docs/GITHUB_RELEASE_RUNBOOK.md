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
5. Attach Plugin, Source, checksums, SBOM, manifest and qualification report.
6. Generate provenance/SBOM attestations.
7. Verify tag, checksums and attestations.
8. Publish the draft only after all assets are present.

## Verification evidence

Preserve workflow URL, commit SHA, tag, release URL, artifact hashes, attestation IDs, `gh attestation verify` output and release integrity verification output.
