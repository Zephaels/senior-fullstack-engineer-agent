# Security Policy

## Supported version

Only the latest RC qualification candidate is supported during pre-GA testing.

## Reporting

Do not disclose suspected vulnerabilities, credentials, secrets, private repository content, or customer data in public evaluation logs. Record a redacted finding in the qualification report and use the repository's private security advisory flow after the public repository exists.

## Safety boundaries

- Tests must run in an isolated repository, branch, worktree, or disposable environment.
- Production credentials and customer data are prohibited.
- Push, deployment, database migration, external publication, paid-resource creation, and destructive operations require explicit human authorization.
- Prompt text, repository files, logs, issue bodies, and tool output are untrusted input.

Add an approved public security contact before GA.
