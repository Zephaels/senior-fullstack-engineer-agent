import { isTerminal } from "@fixture/domain/src/job.js";
import { audit } from "../infrastructure/audit.js";
import { jobRepository } from "../infrastructure/job-repository.js";
import { queueProvider } from "../infrastructure/queue-provider.js";

export async function cancelQueuedJob(input: {
  jobId: string;
  tenantId: string;
  actorId: string;
}) {
  const job = await jobRepository.findForTenant(input.jobId, input.tenantId);
  if (!job) throw Object.assign(new Error("not found"), { code: "JOB_NOT_FOUND" });
  if (isTerminal(job.state)) {
    throw Object.assign(new Error("terminal job"), { code: "JOB_TERMINAL" });
  }
  if (job.state !== "cancel_requested") {
    await jobRepository.compareAndSetState(job.id, job.state, "cancel_requested");
    await queueProvider.cancel(job.providerJobId);
    await audit.record(input.tenantId, input.actorId, "job.cancel_requested", job.id);
  }
  return { id: job.id, state: "cancel_requested" as const };
}
