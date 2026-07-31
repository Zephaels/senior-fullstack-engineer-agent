import { cancelQueuedJob } from "../services/cancel-job.js";

export async function postCancelJob(request: {
  params: { jobId: string };
  auth: { tenantId: string; userId: string; permissions: string[] };
}) {
  if (!request.auth.permissions.includes("jobs:cancel")) {
    return { status: 403, body: { code: "FORBIDDEN" } };
  }
  const result = await cancelQueuedJob({
    jobId: request.params.jobId,
    tenantId: request.auth.tenantId,
    actorId: request.auth.userId,
  });
  return { status: 202, body: result };
}
