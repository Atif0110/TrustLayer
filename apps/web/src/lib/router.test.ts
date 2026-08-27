import { describe, expect, it } from "vitest";

import { parsePath, toPath } from "./router";

describe("router", () => {
  it("parses dashboard and nested agent routes", () => {
    expect(parsePath("/")).toEqual({ name: "dashboard" });
    expect(parsePath("/agents/abc")).toEqual({ name: "agent-detail", id: "abc" });
    expect(parsePath("/policies/new")).toEqual({ name: "policy-editor" });
  });

  it("round-trips known routes", () => {
    expect(parsePath(toPath({ name: "approvals" }))).toEqual({ name: "approvals" });
    expect(parsePath(toPath({ name: "audit" }))).toEqual({ name: "audit" });
  });
});
