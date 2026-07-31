# Release evidence

Public GA requires a version-specific directory at `release-evidence/<VERSION>/`.
It must contain a complete `scorecard.json` whose status is `GA_GATE_PASS`.
It must also contain the following externally verifiable reports for the exact
tagged commit:

- `independent-security-report.json` from a real independent repository scan,
  with zero open critical or high findings;
- `independent-judge-report.json` covering every official case with a judge
  from a different model family and an isolated judge session;
- `autonomy-rehearsal-report.json` proving a bounded dry run, staging canary,
  health gate, rollback fault injection, and zero unauthorized actions.

Each report must identify the full target commit, a public HTTPS report URL,
and the SHA-256 of its underlying evidence. A file containing only
`{"status":"PASS"}` is intentionally rejected.
Local security and reproducible-build reports are generated during the release
workflow. GitHub check-run evidence and artifact attestations must be collected
from the exact tagged commit; they cannot be replaced by local or mock results.

This directory is deliberately excluded from release archives and manifests so
that evidence generation cannot change the artifacts it is qualifying.
