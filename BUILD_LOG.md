# Build Log

## Phase 0 — Scaffold

- Built: repository scaffold, Docker Compose wiring, FastAPI health endpoint, and Vite React shell.

## Phase 1 — Core authorization loop

- Built: auth, organizations, agents, policies, authorization checks, approvals, audit log, Alembic migration, active-agent enforcement, owner/admin-only approvals, expired-approval handling, append-only audit trigger, and policy uniqueness constraints.
- Acceptance summary: clean-database flow produced ALLOW, REQUIRE_APPROVAL, APPROVED, DENY, ordered audit events, and cross-tenant denial.

## Phase 2 — Minimal dashboard

- Built: reusable primitives, typed API client, signup/login, dashboard shell, agents, policies, approvals, audit log, refresh-aware auth flow, and agent-key management on the agent detail page.

## Phase 3 — Demo agent

- Built: scripts/demo_agent.py for natural-language authorization demos.

## Phase 4 — Demo polish

- Built: demo seed, ADR updates, API reference updates, CI integration coverage, review notes, final transcript, and release zip.
