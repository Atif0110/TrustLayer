# TrustLayer

TrustLayer is a real authorization API for AI agents, with a minimal dashboard and approval workflow.

## What ships in this MVP

- FastAPI + PostgreSQL authorization API
- First-match policy engine with default DENY
- Approval queue for `REQUIRE_APPROVAL`
- Append-only audit log
- React dashboard that reads and writes the live API
- Demo seed and demo-agent scripts

## Prerequisites

- Docker with Compose
- Python 3.12+ (only for the demo scripts)

## Five-command local run

1. `cp infrastructure/.env.example infrastructure/.env`
2. `python - <<'PY'`
   `from pathlib import Path; import secrets; p = Path('infrastructure/.env'); p.write_text(p.read_text().replace('replace-with-a-long-random-secret', secrets.token_hex(32)))`
   `PY`
3. `docker compose -f infrastructure/docker-compose.yml up --build -d`
4. `curl http://localhost:8000/health`
5. `PYTHONPATH=apps/api/src python scripts/demo_seed.py`

The dashboard runs at `http://localhost:5173` and the API runs at `http://localhost:8000`.

If step 5 prints an `access_token`, `agent_id`, and `organization_id`, the backend, database, and seed flow are working. Then sign in at `http://localhost:5173` with the seeded credentials.

## Backend verification

- Unit tests: `PYTHONPATH=apps/api/src pytest apps/api/tests/unit -q`
- Integration tests: `PYTHONPATH=apps/api/src pytest apps/api/tests/integration -q`

The integration suite now uses `testcontainers[postgres]` by default. If your machine already has a local Postgres you want to reuse, set `TRUSTLAYER_TEST_DATABASE_URL` explicitly.

The signup/login rate limiter is intentionally in-memory for this MVP. It protects a single API instance but does not coordinate across multiple replicas yet.

## Frontend verification

- Tests: `npm --prefix apps/web test`
- Typecheck: `npm --prefix apps/web run typecheck`
- Production build: `npm --prefix apps/web run build`

## Demo scripts

### `scripts/demo_seed.py`

Creates a clean demo organization, default policy, and demo agent through the real API. By default it generates a unique demo email on each run so repeated demos do not collide.

### `scripts/demo_agent.py`

Requires:

- `OPENAI_API_KEY`
- `TRUSTLAYER_AGENT_ID`
- either `TRUSTLAYER_ACCESS_TOKEN` or `TRUSTLAYER_API_KEY`

Machine credentials are now agent-scoped. Generate or rotate them from the agent detail page in the dashboard.

Example:

`python scripts/demo_agent.py "refund this $500 order"`

## 90-second demo recording steps

1. Start Compose and show `GET /health` returning `{"status":"ok"}`.
2. Run `python scripts/demo_seed.py` and copy the returned `agent_id` and access token.
3. Open the dashboard, sign in as the seeded owner, and show the empty approval queue becoming populated after a large refund check.
4. Run an ALLOW check for a small refund, then a `REQUIRE_APPROVAL` check for a large refund, then a DENY check for `customer.delete`.
5. Approve the pending refund in the dashboard and refresh the audit log to show `ALLOW`, `REQUIRE_APPROVAL`, `APPROVED`, and `DENY` in order.
6. Mention that a second organization receives `404` when it tries to access the first organization's approval request.
