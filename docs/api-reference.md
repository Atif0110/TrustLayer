# API Reference

## `GET /health`

Returns service health for the API process.

## `POST /v1/auth/signup`

Creates an organization and owner account, then returns a bearer access token and sets a refresh cookie.

## `POST /v1/auth/login`

Verifies email/password credentials, returns a bearer access token, and rotates the refresh cookie. If the same email exists in multiple organizations, the caller must also provide the organization name.

## `POST /v1/auth/refresh`

Issues a new short-lived access token from the httpOnly refresh cookie.

## `POST /v1/auth/logout`

Clears the refresh cookie for the current browser session.

## `POST /v1/agents`

Creates an organization-scoped agent owned by the authenticated user.

## `GET /v1/agents`

Lists agents for the authenticated user's organization.

## `GET /v1/agents/{agent_id}`

Fetches one agent that belongs to the authenticated user's organization.

## `GET /v1/agents/{agent_id}/keys`

Lists machine key metadata for one agent. Raw key material is never returned here.

## `POST /v1/agents/{agent_id}/keys/rotate`

Revokes any active keys for the agent, creates a new one, and returns the raw key exactly once.

## `POST /v1/agents/{agent_id}/keys/{key_id}/revoke`

Revokes one existing agent key without creating a replacement.

## `POST /v1/policies`

Creates a new active policy version for the authenticated user's organization.

## `GET /v1/policies`

Lists policy versions for the authenticated user's organization, newest first.

## `POST /v1/authorization/check`

Evaluates the active organization policy for an agent action, persists the authorization request, optionally creates an approval request, and appends an audit log row in the same transaction.

## `GET /v1/approvals`

Lists pending approval requests for the authenticated user's organization.

## `POST /v1/approvals/{approval_id}/approve`

Approves a pending request for the authenticated user's organization and appends an audit event.

## `POST /v1/approvals/{approval_id}/deny`

Deny a pending request for the authenticated user's organization and append an audit event.

## `GET /v1/audit-events`

Returns append-only audit events for the authenticated user's organization in time order.
