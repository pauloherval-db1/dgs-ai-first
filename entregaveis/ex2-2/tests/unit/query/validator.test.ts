import { describe, expect, it } from "vitest";

import { validateQueryRequest } from "../../../src/functions/query/validator";

describe("validateQueryRequest", () => {
  it("rejects a payload without question", () => {
    expect(() => validateQueryRequest({})).toThrow("question must be a string");
  });

  it("rejects an empty question", () => {
    expect(() => validateQueryRequest({ question: "   " })).toThrow("question must not be empty");
  });

  it("rejects a question above the maximum length", () => {
    const question = "a".repeat(1001);

    expect(() => validateQueryRequest({ question })).toThrow("question must be at most 1000 characters");
  });

  it("accepts a valid payload and trims question whitespace", () => {
    const result = validateQueryRequest({ question: "  What is the status?  ", session_id: "session-1" });

    expect(result).toEqual({
      question: "What is the status?",
      session_id: "session-1",
    });
  });
});