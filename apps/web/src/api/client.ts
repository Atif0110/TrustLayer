import { clearSession, getAccessToken, updateAccessToken } from "../lib/auth-storage";
import { navigate } from "../lib/router";
import type {
  Agent,
  AgentKey,
  AgentKeyIssueResponse,
  ApprovalActionResponse,
  AuditEvent,
  CreateAgentRequest,
  CreateAgentResponse,
  CreatePolicyRequest,
  CreatePolicyResponse,
  LoginRequest,
  LoginResponse,
  PendingApproval,
  Policy,
  RefreshResponse,
  SignupRequest,
  SignupResponse,
} from "./types";

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function apiBaseUrl(): string {
  const configured = import.meta.env.VITE_API_BASE_URL;
  if (typeof configured === "string" && configured.length > 0) {
    return configured.replace(/\/$/, "");
  }
  return "http://localhost:8000";
}

function messageFromBody(body: unknown, status: number): string {
  if (typeof body === "object" && body !== null && "detail" in body) {
    const detail = (body as { detail: unknown }).detail;
    if (typeof detail === "string") {
      return detail;
    }
    if (Array.isArray(detail)) {
      return detail
        .map((item) => {
          if (typeof item === "object" && item !== null && "msg" in item) {
            return String((item as { msg: unknown }).msg);
          }
          return String(item);
        })
        .join("; ");
    }
  }
  return `Request failed (${status})`;
}

async function refreshAccessToken(): Promise<boolean> {
  try {
    const response = await fetch(`${apiBaseUrl()}/v1/auth/refresh`, {
      method: "POST",
      credentials: "include",
    });
    if (!response.ok) {
      return false;
    }
    const body = (await response.json()) as RefreshResponse;
    updateAccessToken(body.access_token);
    return true;
  } catch {
    return false;
  }
}

export async function apiRequest<T>(
  path: string,
  init: RequestInit = {},
  allowRetry = true,
): Promise<T> {
  const headers = new Headers(init.headers);
  if (!headers.has("Content-Type") && init.body !== undefined) {
    headers.set("Content-Type", "application/json");
  }
  const token = getAccessToken();
  if (token !== null && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${apiBaseUrl()}${path}`, {
    ...init,
    headers,
    credentials: "include",
  });

  if (response.status === 401) {
    if (allowRetry && path !== "/v1/auth/refresh") {
      const refreshed = await refreshAccessToken();
      if (refreshed) {
        return apiRequest<T>(path, init, false);
      }
    }
    clearSession();
    if (window.location.pathname !== "/login" && window.location.pathname !== "/signup") {
      navigate("/login");
    }
  }

  if (!response.ok) {
    let body: unknown = null;
    try {
      body = await response.json();
    } catch {
      body = null;
    }
    throw new ApiError(response.status, messageFromBody(body, response.status));
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export const api = {
  signup(body: SignupRequest): Promise<SignupResponse> {
    return apiRequest<SignupResponse>("/v1/auth/signup", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },
  login(body: LoginRequest): Promise<LoginResponse> {
    return apiRequest<LoginResponse>("/v1/auth/login", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },
  listAgents(): Promise<Agent[]> {
    return apiRequest<Agent[]>("/v1/agents");
  },
  getAgent(agentId: string): Promise<Agent> {
    return apiRequest<Agent>(`/v1/agents/${agentId}`);
  },
  createAgent(body: CreateAgentRequest): Promise<CreateAgentResponse> {
    return apiRequest<CreateAgentResponse>("/v1/agents", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },
  listPolicies(): Promise<Policy[]> {
    return apiRequest<Policy[]>("/v1/policies");
  },
  createPolicy(body: CreatePolicyRequest): Promise<CreatePolicyResponse> {
    return apiRequest<CreatePolicyResponse>("/v1/policies", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },
  listApprovals(): Promise<PendingApproval[]> {
    return apiRequest<PendingApproval[]>("/v1/approvals");
  },
  approve(approvalId: string): Promise<ApprovalActionResponse> {
    return apiRequest<ApprovalActionResponse>(`/v1/approvals/${approvalId}/approve`, {
      method: "POST",
    });
  },
  deny(approvalId: string): Promise<ApprovalActionResponse> {
    return apiRequest<ApprovalActionResponse>(`/v1/approvals/${approvalId}/deny`, {
      method: "POST",
    });
  },
  listAuditEvents(): Promise<AuditEvent[]> {
    return apiRequest<AuditEvent[]>("/v1/audit-events");
  },
  listAgentKeys(agentId: string): Promise<AgentKey[]> {
    return apiRequest<AgentKey[]>(`/v1/agents/${agentId}/keys`);
  },
  rotateAgentKey(agentId: string): Promise<AgentKeyIssueResponse> {
    return apiRequest<AgentKeyIssueResponse>(`/v1/agents/${agentId}/keys/rotate`, {
      method: "POST",
    });
  },
  revokeAgentKey(agentId: string, keyId: string): Promise<AgentKey> {
    return apiRequest<AgentKey>(`/v1/agents/${agentId}/keys/${keyId}/revoke`, {
      method: "POST",
    });
  },
  logout(): Promise<void> {
    return apiRequest<void>("/v1/auth/logout", {
      method: "POST",
    });
  },
};
