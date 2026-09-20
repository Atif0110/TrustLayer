# TrustLayer

TrustLayer is a real authorization API for AI agents, with a minimal dashboard and approval workflow.

## What ships in this MVP

- FastAPI + PostgreSQL authorization API
- First-match policy engine with default DENY
- ALLOW, DENY, and REQUIRE_APPROVAL authorization decisions
- Approval queue for REQUIRE_APPROVAL
- Approval expiration and explicit approve/reject actions
- Append-only audit log
- Multi-tenant organization isolation
- Agent-scoped machine credentials with rotation and revocation
- React dashboard that reads and writes the live API
- Demo seed and demo-agent scripts
- Backend unit and integration tests
- Frontend tests, type checking, and production build

The backend makes authorization decisions. It does not itself execute the requested AI-agent action.

---

## How it works

```text
AI agent / client
       |
       | Authorization request
       v
+-------------------------+
| TrustLayer API          |
| FastAPI                 |
+------------+------------+
             |
             v
+-------------------------+
| Policy Engine           |
| first-match evaluation  |
| default DENY            |
+------------+------------+
             |
       +-----+------------------+
       |                        |
       v                        v
     ALLOW                 REQUIRE_APPROVAL
       |                        |
       |                        v
       |                 Approval Queue
       |                        |
       |                 APPROVED / REJECTED
       |                        |
       +------------+-----------+
                    |
                    v
              Audit Log
```

For a matching policy rule, the first applicable rule determines the decision. If no rule matches, TrustLayer returns DENY.

A REQUIRE_APPROVAL decision creates an approval request instead of immediately authorizing the action. The request can then be approved or rejected through the API/dashboard.

---

## Core authorization model

TrustLayer supports three authorization outcomes:

**ALLOW**

The requested action is authorized immediately.

**DENY**

The requested action is rejected immediately.

**REQUIRE_APPROVAL**

The action requires human approval before it can proceed.

Approval requests have an explicit lifecycle and can expire. Approval actions are recorded in the audit trail.

---

## Multi-tenant isolation

TrustLayer is organization-scoped.

Authenticated users, agents, policies, approval requests, audit records, and related resources are resolved within the caller's organization.

A resource belonging to another organization is not exposed through the normal API flow. Cross-organization approval access is explicitly covered by the integration tests and returns 404.

This keeps the authorization and approval data isolated between organizations.

---

## Agent credentials

Machine credentials are scoped to individual agents.

The dashboard/API supports creating, rotating, and revoking agent credentials.

Raw credentials are returned only when they are generated or rotated. Credential metadata can then be used to identify and manage the credential without exposing the secret again.

The demo-agent flow accepts either:

- `TRUSTLAYER_ACCESS_TOKEN`
- `TRUSTLAYER_API_KEY`

along with the target:

- `TRUSTLAYER_AGENT_ID`

---

## Audit log

TrustLayer records authorization and approval activity in an append-only audit log.

The database protects audit records against updates and deletes, so existing audit history cannot be modified through normal database operations.

The audit trail records the authorization lifecycle, including decisions such as:

- ALLOW
- REQUIRE_APPROVAL
- APPROVED
- DENY

---

## Prerequisites

- Docker with Compose
- Python 3.12+ (only for the demo scripts)
- Node.js/npm for frontend development and verification

---

## Five-command local run

From the repository root:

### 1. Create the environment file

```bash
cp infrastructure/.env.example infrastructure/.env
```

### 2. Generate a development secret

On macOS/Linux:

```bash
python - <<'PY'
from pathlib import Path
import secrets

p = Path("infrastructure/.env")
p.write_text(
    p.read_text().replace(
        "replace-with-a-long-random-secret",
        secrets.token_hex(32),
    )
)
PY
```

On Windows PowerShell:

```powershell
$envFile = "infrastructure/.env"
$content = Get-Content $envFile -Raw
$content = $content.Replace("replace-with-a-long-random-secret", ([System.Guid]::NewGuid().ToString("N") + [System.Guid]::NewGuid().ToString("N")))
Set-Content $envFile $content
```

### 3. Start the backend and database

```bash
docker compose -f infrastructure/docker-compose.yml up --build -d
```

### 4. Check the API

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"ok"}
```

### 5. Seed the demo environment

```bash
PYTHONPATH=apps/api/src python scripts/demo_seed.py
```

The seed script creates a clean demo organization, default policy, and demo agent through the real API.

The dashboard runs at:

```text
http://localhost:5173
```

The API runs at:

```text
http://localhost:8000
```

If the seed command prints an `access_token`, `agent_id`, and `organization_id`, the backend, database, and seed flow are working.

Then sign in at:

```text
http://localhost:5173
```

using the seeded credentials.

---

## Backend verification

**Unit tests**

```bash
PYTHONPATH=apps/api/src pytest apps/api/tests/unit -q
```

**Integration tests**

```bash
PYTHONPATH=apps/api/src pytest apps/api/tests/integration -q
```

The integration suite uses:

```text
testcontainers[postgres]
```

by default.

If your machine already has a PostgreSQL instance that you want to reuse, set:

```text
TRUSTLAYER_TEST_DATABASE_URL
```

explicitly.

The integration tests cover important behavior including authorization decisions, approval workflows, expiration, authentication, organization isolation, and audit behavior.

### Rate limiting

The signup/login rate limiter is intentionally in-memory for this MVP.

It protects a single API instance but does not coordinate rate-limit state across multiple replicas.

A production multi-instance deployment should replace the in-memory limiter with shared state.

---

## Frontend verification

From the repository root:

**Tests**

```bash
npm --prefix apps/web test
```

**Typecheck**

```bash
npm --prefix apps/web run typecheck
```

**Production build**

```bash
npm --prefix apps/web run build
```

The frontend is a React application that communicates with the live TrustLayer API.

---

## Demo scripts

### `scripts/demo_seed.py`

Creates a clean demo organization, default policy, and demo agent through the real API.

By default, it generates a unique demo email on each run so repeated demos do not collide.

The script prints the credentials and identifiers needed to access the seeded environment.

### `scripts/demo_agent.py`

The demo agent shows how an external AI-agent workflow can use TrustLayer for authorization.

It requires:

- `OPENAI_API_KEY`
- `TRUSTLAYER_AGENT_ID`
- either `TRUSTLAYER_ACCESS_TOKEN` or `TRUSTLAYER_API_KEY`

Example:

```bash
python scripts/demo_agent.py "refund this $500 order"
```

The script uses the OpenAI API to turn the natural-language request into a structured action and then sends that action to TrustLayer for authorization.

The OpenAI dependency is therefore part of the demo-agent integration, not a requirement for the core TrustLayer authorization API.

---

## Example authorization flow

A typical request can move through the following sequence:

```text
Agent request
     |
     v
TrustLayer authorization check
     |
     +---- matching ALLOW rule --------> ALLOW
     |
     +---- matching DENY rule ---------> DENY
     |
     +---- REQUIRE_APPROVAL -----------> Approval Queue
                                           |
                                  +--------+--------+
                                  |                 |
                                  v                 v
                               APPROVED          REJECTED
```

The authorization decision is persisted together with the relevant audit information.

---

## 90-second demo recording steps

1. Start Compose and show `GET /health` returning `{"status":"ok"}`.
2. Run `python scripts/demo_seed.py` and copy the returned `agent_id` and access token.
3. Open the dashboard, sign in as the seeded owner, and show the empty approval queue.
4. Run an ALLOW check for a small refund.
5. Run a REQUIRE_APPROVAL check for a large refund.
6. Run a DENY check for `customer.delete`.
7. Approve the pending refund in the dashboard.
8. Refresh the audit log and show ALLOW, REQUIRE_APPROVAL, APPROVED, and DENY in order.
9. Demonstrate organization isolation by showing that a second organization cannot access the first organization's approval request and receives 404.

---

## Repository structure

```text
TrustLayer/
├── apps/
│   ├── api/
│   │   ├── src/
│   │   └── tests/
│   └── web/
├── infrastructure/
│   ├── .env.example
│   └── docker-compose.yml
├── scripts/
│   ├── demo_seed.py
│   └── demo_agent.py
└── README.md
```

The API contains the authorization, policy, approval, authentication, organization, agent, credential, and audit functionality.

The web application contains the dashboard and its API integration.

---

## API responsibilities

The TrustLayer API is responsible for:

- authenticating users and agents
- resolving organization context
- evaluating authorization policies
- returning ALLOW, DENY, or REQUIRE_APPROVAL
- creating and managing approval requests
- recording audit events
- managing agent-scoped credentials

The API does not execute the underlying business action.

For example, if an agent asks:

```text
refund this $500 order
```

TrustLayer decides whether the action is:

- ALLOW
- DENY
- REQUIRE_APPROVAL

The calling agent/application remains responsible for actually executing the action after receiving authorization.

---

## Security boundaries

TrustLayer separates:

```text
Identity
   |
   v
Organization context
   |
   v
Agent / user authorization
   |
   v
Policy evaluation
   |
   v
Approval workflow
   |
   v
Audit trail
```

Agent credentials are scoped to individual agents, and application resources are scoped to organizations.

The MVP deliberately keeps the login/signup rate limiter in memory, which is suitable for a single API instance but not for coordinated rate limiting across multiple replicas.

---

## Current MVP scope

TrustLayer currently provides:

- FastAPI authorization API
- PostgreSQL persistence
- first-match policy evaluation
- default DENY
- ALLOW
- DENY
- REQUIRE_APPROVAL
- approval queue
- approval expiration
- approval actions
- append-only audit logging
- organization isolation
- agent-scoped credentials
- credential rotation and revocation
- React dashboard
- demo seed flow
- OpenAI-backed demo-agent integration
- backend unit tests
- backend PostgreSQL integration tests
- frontend tests
- frontend type checking
- production frontend build

The project is an MVP authorization layer for AI-agent workflows. It is not an AI model, an LLM inference service, or a replacement for the business system that ultimately executes an authorized action.
