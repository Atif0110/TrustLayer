export type Decision = "ALLOW" | "DENY" | "REQUIRE_APPROVAL";
export type AuditDecision = Decision | "APPROVED" | "DENIED";
export type AgentStatus = "active" | "suspended" | "revoked";

export type AuthSession = {
  accessToken: string;
  email: string;
  organizationId: string;
};

export type SignupRequest = {
  name: string;
  email: string;
  password: string;
};

export type LoginRequest = {
  email: string;
  password: string;
  organization_name?: string;
};

export type SignupResponse = {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
  email: string;
  organization_id: string;
};

export type LoginResponse = {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
  email: string;
  organization_id: string;
};

export type RefreshResponse = {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
};

export type AgentKeyIssueResponse = {
  key_id: string;
  api_key: string;
};

export type AgentKey = {
  id: string;
  key_prefix: string;
  hint: string;
  created_at: string;
  revoked_at: string | null;
  last_used_at: string | null;
};

export type Agent = {
  id: string;
  name: string;
  status: AgentStatus;
  created_at: string;
};

export type CreateAgentRequest = {
  name: string;
};

export type CreateAgentResponse = {
  id: string;
};

export type PolicyRuleCondition = {
  action: string;
  amount_lte?: number;
  amount_gt?: number;
};

export type PolicyRule = {
  if: PolicyRuleCondition;
  then: Decision;
};

export type Policy = {
  id: string;
  name: string;
  version: number;
  is_active: boolean;
  rules: PolicyRule[];
};

export type CreatePolicyRequest = {
  name: string;
  rules: PolicyRule[];
};

export type CreatePolicyResponse = {
  id: string;
  version: number;
};

export type PendingApproval = {
  id: string;
  request_id: string;
  action: string;
  resource: string;
  expires_at: string;
};

export type ApprovalActionResponse = {
  status: string;
};

export type AuditEvent = {
  request_id: string;
  decision: AuditDecision;
  action: string;
  resource: string;
  reason: string;
  policy_version: string;
  created_at: string;
};
