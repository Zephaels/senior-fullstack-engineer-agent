# Queued Job Service Fixture

Synthetic pnpm monorepo for qualification. The API exposes queued-job operations. PostgreSQL is the system of record, and `QueueProvider` owns provider-side cancellation.

The production deployment runs the API and worker separately. Cancellation behavior is implemented through the existing API route, application service, repository, queue adapter, and audit boundary.
