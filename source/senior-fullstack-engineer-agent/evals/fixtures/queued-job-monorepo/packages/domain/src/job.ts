export type JobState =
  | "queued"
  | "running"
  | "cancel_requested"
  | "cancelled"
  | "completed"
  | "failed";

export interface Job {
  id: string;
  tenantId: string;
  ownerId: string;
  providerJobId: string;
  state: JobState;
  updatedAt: Date;
}

export const isTerminal = (state: JobState): boolean =>
  state === "cancelled" || state === "completed" || state === "failed";
