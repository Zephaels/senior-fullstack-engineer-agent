// The worker observes cancel_requested before committing completed state.
export async function shouldCommitCompletion(state: string): Promise<boolean> {
  return state !== "cancel_requested" && state !== "cancelled";
}
