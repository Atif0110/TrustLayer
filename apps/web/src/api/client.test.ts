import { afterEach, describe, expect, it, vi } from "vitest";

import { api } from "./client";
import { writeSession } from "../lib/auth-storage";

afterEach(() => {
  window.sessionStorage.clear();
  vi.unstubAllGlobals();
});

describe("api client", () => {
  it("sends Authorization Bearer from stored JWT", async () => {
    writeSession({
      accessToken: "test-token",
      email: "owner@example.com",
      organizationId: "org-1",
    });
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => [],
    });
    vi.stubGlobal("fetch", fetchMock);

    await api.listAgents();

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    const headers = new Headers(init.headers);
    expect(headers.get("Authorization")).toBe("Bearer test-token");
  });

  it("posts login without a stored token", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ access_token: "abc" }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await api.login({ email: "owner@example.com", password: "supersecret12" });

    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toContain("/v1/auth/login");
    expect(init.method).toBe("POST");
    const headers = new Headers(init.headers);
    expect(headers.get("Authorization")).toBeNull();
    expect(init.body).toBe(JSON.stringify({ email: "owner@example.com", password: "supersecret12" }));
  });

  it("retries once after refreshing the access token", async () => {
    writeSession({
      accessToken: "expired-token",
      email: "owner@example.com",
      organizationId: "org-1",
    });
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({ ok: false, status: 401, json: async () => ({ detail: "expired" }) })
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ access_token: "fresh-token", token_type: "bearer", expires_in: 900 }) })
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => [] });
    vi.stubGlobal("fetch", fetchMock);

    await api.listAgents();

    const [, retryInit] = fetchMock.mock.calls[2] as [string, RequestInit];
    const retryHeaders = new Headers(retryInit.headers);
    expect(retryHeaders.get("Authorization")).toBe("Bearer fresh-token");
  });
});
