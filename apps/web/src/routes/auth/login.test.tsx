import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { LoginPage } from "./login";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("login screen", () => {
  it("renders the real auth form", () => {
    render(<LoginPage />);
    expect(screen.getByLabelText("Email")).toBeTruthy();
    expect(screen.getByLabelText("Password")).toBeTruthy();
    expect(screen.getByLabelText("Organization name")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Sign in" })).toBeTruthy();
  });

  it("submits credentials to the login API", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        access_token: "token",
        token_type: "bearer",
        expires_in: 900,
        email: "owner@example.com",
        organization_id: "org-1",
      }),
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<LoginPage />);
    fireEvent.change(screen.getByLabelText("Email"), { target: { value: "owner@example.com" } });
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "supersecret12" } });
    fireEvent.change(screen.getByLabelText("Organization name"), { target: { value: "Acme" } });
    fireEvent.submit(screen.getByRole("button", { name: "Sign in" }).closest("form") as HTMLFormElement);

    await vi.waitFor(() => {
      expect(fetchMock).toHaveBeenCalled();
    });
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toContain("/v1/auth/login");
    expect(init.body).toBe(JSON.stringify({ email: "owner@example.com", password: "supersecret12", organization_name: "Acme" }));
  });
});
