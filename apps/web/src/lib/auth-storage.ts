import type { AuthSession } from "../api/types";

const SESSION_KEY = "trustlayer.session";

function storage(): Storage {
  return window.sessionStorage;
}

export function readSession(): AuthSession | null {
  const raw = storage().getItem(SESSION_KEY);
  if (raw === null) {
    return null;
  }
  try {
    const parsed: unknown = JSON.parse(raw);
    if (
      typeof parsed !== "object" ||
      parsed === null ||
      !("accessToken" in parsed) ||
      !("email" in parsed)
    ) {
      return null;
    }
    const record = parsed as {
      accessToken: unknown;
      email: unknown;
      organizationId?: unknown;
    };
    if (typeof record.accessToken !== "string" || typeof record.email !== "string") {
      return null;
    }
    return {
      accessToken: record.accessToken,
      email: record.email,
        organizationId: typeof record.organizationId === "string" ? record.organizationId : "",
      };
  } catch {
    return null;
  }
}

export function writeSession(session: AuthSession): void {
  storage().setItem(SESSION_KEY, JSON.stringify(session));
}

export function clearSession(): void {
  storage().removeItem(SESSION_KEY);
}

export function getAccessToken(): string | null {
  return readSession()?.accessToken ?? null;
}

export function updateAccessToken(accessToken: string): void {
  const session = readSession();
  if (session === null) {
    return;
  }
  writeSession({ ...session, accessToken });
}
