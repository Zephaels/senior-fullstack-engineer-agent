import type { Job, JobState } from "@fixture/domain/src/job.js";

export const jobRepository: {
  findForTenant(id: string, tenantId: string): Promise<Job | null>;
  compareAndSetState(id: string, from: JobState, to: JobState): Promise<void>;
} = {} as never;
