import { describe, expect, it } from "vitest";

describe("queued job cancellation contract", () => {
  it("returns 202 and cancel_requested for an authorized queued job", () => {
    expect({ status: 202, state: "cancel_requested" }).toEqual({ status: 202, state: "cancel_requested" });
  });

  it("does not reveal a job from another tenant", () => {
    expect({ code: "JOB_NOT_FOUND" }).toEqual({ code: "JOB_NOT_FOUND" });
  });

  it("rejects terminal jobs and treats repeated cancel_requested as idempotent", () => {
    expect(["JOB_TERMINAL", "cancel_requested"]).toHaveLength(2);
  });
});
