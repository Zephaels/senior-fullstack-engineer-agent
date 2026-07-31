export const audit: {
  record(tenantId: string, actorId: string, action: string, subjectId: string): Promise<void>;
} = {} as never;
