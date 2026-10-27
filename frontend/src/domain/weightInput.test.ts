import { describe, expect, it } from "vitest";

import { checkWeight } from "./weightInput";

describe("checkWeight", () => {
  it("normalizes a comma decimal", () => {
    expect(checkWeight("2,5")).toEqual({ ok: true, value: "2.5" });
  });

  it("rejects letters", () => {
    const result = checkWeight("abc");
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.pending).toBe(false);
    }
  });

  it("rejects three decimal places", () => {
    const result = checkWeight("1.234");
    expect(result.ok).toBe(false);
  });

  it("rejects an empty scale", () => {
    const result = checkWeight("   ");
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.message).toContain("peso");
    }
  });

  it("waits while the decimal is incomplete", () => {
    expect(checkWeight("2.")).toEqual({ ok: false, pending: true, message: "" });
  });

  it("allows a negative weight through so the API can reject it", () => {
    expect(checkWeight("-1")).toEqual({ ok: true, value: "-1" });
  });
});
