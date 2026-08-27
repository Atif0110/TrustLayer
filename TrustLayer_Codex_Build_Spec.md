# TrustLayer — Codex Build Specification
### Real MVP, not a mockup. Version 1.0

This document replaces the "Master Build Bible" as the working instruction set. It is scoped
deliberately smaller. Everything in here must actually run, actually persist data, and actually
make a real authorization decision. Nothing in this document should be implemented as a fake
state object or a hardcoded UI response. If a feature can't be built for real in the given phase,
it is cut, not faked.

Read this whole document before writing any code. Build the phases in order. Do not start Phase 2
until Phase 1 passes its acceptance test.

---

## 1. What we are actually building

A working authorization API for AI agents, with:

- A real backend, real database, real auth.
- One core decision endpoint: `POST /v1/authorization/check` that evaluates a real policy against
  a real request and returns ALLOW, DENY, or REQUIRE_APPROVAL.
- A real approval workflow for the REQUIRE_APPROVAL case.
- A real, append-only audit log of every decision.
- A minimal, well-designed dashboard that shows this real data — not scripted demo content.

That is the whole MVP. Verification platform, business verification, webhooks, risk ML models,
compliance frameworks, and the marketing site are explicitly **out of scope** for this build. They
are listed in Section 10 as future phases, described only so Codex understands where the
architecture is headed and doesn't paint itself into a corner — they are not to be implemented now.

---

## 2. Tech stack (fixed — do not substitute)

| Layer | Choice | Why |
|---|---|---|
| Backend | Python 3.12, FastAPI | Matches existing skill set, fast to iterate, good typing |
| ORM / DB access | SQLAlchemy 2.0 (async) + Alembic for migrations | Real schema, real migrations, no ORM magic |
| Database | PostgreSQL 16 | Relational integrity for tenants/policies/audit matters here |
| Auth | JWT access token (short-lived) + refresh token, Argon2id for password hashing | Standard, defensible, no custom crypto |
| Frontend | React + TypeScript + Vite | No Next.js needed for an app-only MVP, keeps it simple |
| Styling | Plain CSS with design tokens (see Section 7) — no Tailwind, no component library | This is what prevents the "made by an LLM" look |
| API client | Hand-written typed fetch wrapper, no generated SDK yet | Keep dependency surface small |
| Local dev | Docker Compose (postgres + api + web) | One command to run everything |
| Testing | pytest (backend), Vitest + Testing Library (frontend) | |

Do not introduce Redis, queues, Kubernetes, or microservices in this build. The spec explicitly
warns against this (see original Bible, Section 35/53) and it still applies. One deployable
backend, one Postgres database.

---

## 3. Repository structure

```
trustlayer/
  apps/
    api/
      src/
        trustlayer/
          main.py                  # FastAPI app factory, router registration
          config.py                # Settings via pydantic-settings, reads .env
          db/
            session.py             # async engine + session factory
            base.py                # declarative base
          models/                  # SQLAlchemy models, one file per aggregate
            user.py
            organization.py
            agent.py
            policy.py
            authorization.py
            approval.py
            audit.py
          schemas/                 # Pydantic request/response models, mirrors models/
          auth/
            security.py            # password hashing, JWT issue/verify
            dependencies.py        # get_current_user, get_current_org, etc.
            router.py
          policy_engine/
            evaluator.py           # pure function: (policy, request_context) -> Decision
            rules.py                # rule parsing / matching
            versioning.py
          authorization/
            router.py               # POST /v1/authorization/check
            service.py               # orchestrates: auth -> policy -> decision -> audit
          approvals/
            router.py
            service.py
          audit/
            router.py
            service.py
          agents/
            router.py
            service.py
          organizations/
            router.py
            service.py
        alembic/
          versions/
          env.py
      tests/
        unit/                      # policy_engine tests, no DB
        integration/                # DB-backed, uses a test Postgres via testcontainers
      pyproject.toml
      alembic.ini
      Dockerfile

    web/
      src/
        main.tsx
        app.tsx
        api/
          client.ts                 # typed fetch wrapper, one function per endpoint
          types.ts                  # mirrors backend Pydantic schemas by hand
        routes/
          auth/
            login.tsx
            signup.tsx
          dashboard/
            dashboard.tsx
          agents/
            agent-list.tsx
            agent-detail.tsx
          policies/
            policy-list.tsx
            policy-editor.tsx
          approvals/
            approval-queue.tsx
          audit/
            audit-log.tsx
        components/
          layout/
            app-shell.tsx
            sidebar.tsx
            topbar.tsx
          primitives/                # button.tsx, badge.tsx, table.tsx, input.tsx — built once, reused everywhere
          decision-badge/            # ALLOW / DENY / REQUIRE_APPROVAL visual, used in 3+ places
        styles/
          tokens.css                 # colors, spacing, type scale — see Section 7
          global.css
        hooks/
        lib/
      index.html
      package.json
      vite.config.ts

  infrastructure/
    docker-compose.yml
    .env.example

  docs/
    architecture-decisions/          # one short ADR .md file per significant decision, numbered
    api-reference.md                 # generated by hand from the router docstrings, kept current

  README.md
```

Rules Codex must follow on structure:

- No file may mix HTTP routing and business logic. Routers call services; services call the DB and
  the policy engine. This is not optional — it's what makes the authorization logic testable and
  auditable, which is the entire point of the product.
- No barrel files (`index.ts` that just re-exports everything). Import from the real file.
- Every backend router file maps to exactly one service file. No service handles more than one
  aggregate (agents, policies, approvals, audit stay separate even though they're related).

---

## 4. Data model (Phase 1 scope only)

Implement exactly these tables first. Do not add columns or tables "for later."

```
organizations
  id (uuid, pk)
  name
  created_at

users
  id (uuid, pk)
  organization_id (fk)
  email (unique)
  password_hash
  role            # enum: OWNER, ADMIN, DEVELOPER, AUDITOR
  created_at

agents
  id (uuid, pk)
  organization_id (fk)
  name
  owner_id (fk -> users.id)
  status          # enum: active, suspended, revoked
  created_at

policies
  id (uuid, pk)
  organization_id (fk)
  name
  version (int)
  is_active (bool)
  rules (jsonb)   # see rule format below
  created_at

authorization_requests
  id (uuid, pk)
  organization_id (fk)
  agent_id (fk)
  action (string)         # e.g. "refund.create"
  resource (string)
  context (jsonb)         # e.g. {"amount": 500, "currency": "USD"}
  policy_id (fk)
  policy_version (int)
  decision (string)       # ALLOW, DENY, REQUIRE_APPROVAL
  reason (string)
  request_id (string, unique)  # public-facing id, e.g. req_92A81
  created_at

approval_requests
  id (uuid, pk)
  authorization_request_id (fk)
  status            # enum: pending, approved, denied, expired
  requested_at
  decided_by (fk -> users.id, nullable)
  decided_at (nullable)
  expires_at

audit_logs
  id (uuid, pk)
  organization_id (fk)
  actor_type       # user | agent
  actor_id
  action
  resource
  decision
  reason
  policy_version
  request_id
  created_at
```

**Policy rule format (stored in `policies.rules` as JSON):**

```json
[
  { "if": { "action": "refund.create", "amount_lte": 100 }, "then": "ALLOW" },
  { "if": { "action": "refund.create", "amount_gt": 100 }, "then": "REQUIRE_APPROVAL" },
  { "if": { "action": "customer.delete" }, "then": "DENY" }
]
```

Rules are evaluated top to bottom, first match wins. If no rule matches, the default decision is
`DENY`. This default-deny behavior is a hard requirement, not a suggestion — an authorization
system that fails open is a broken authorization system.

---

## 5. The core flow (this is the product — get this right before anything else)

```
POST /v1/authorization/check
Headers: Authorization: Bearer <api key or JWT>
Body:
{
  "agent_id": "uuid",
  "action": "refund.create",
  "resource": "refund_8F31",
  "context": { "amount": 500, "currency": "USD" }
}
```

Server-side sequence (implement exactly this order, each step is testable independently):

1. Authenticate the caller. Reject if invalid.
2. Resolve the agent, confirm it belongs to the caller's organization. Reject cross-tenant access
   with a 404, not a 403 (don't confirm the resource exists to a caller who shouldn't see it).
3. Load the organization's active policy (highest version where `is_active = true`).
4. Run `policy_engine.evaluator.evaluate(policy.rules, action, context)` — a pure function, unit
   tested with no database involved.
5. If decision is `REQUIRE_APPROVAL`, create an `approval_requests` row with status `pending`.
6. Write the `authorization_requests` row.
7. Write the `audit_logs` row. This write must happen in the same DB transaction as step 6 — an
   authorization decision that isn't audited is not a valid decision.
8. Return the decision, `policy_version`, `request_id`, and (if applicable) `approval_request_id`.

**Acceptance test for Phase 1 (must pass before moving on):**

- Create an org, a user, an agent, and a policy with the three example rules above, all through
  real API calls, no seed script shortcuts.
- Call `refund.create` with amount 50 → real response is `ALLOW`.
- Call `refund.create` with amount 500 → real response is `REQUIRE_APPROVAL`, and a real approval
  row now exists.
- Approve it through `POST /v1/approvals/{id}/approve` as the org owner.
- Call `customer.delete` → real response is `DENY`.
- Open `GET /v1/audit-events` → all four events are there, in order, with correct request IDs.
- Do this whole sequence again from a second organization's agent and confirm it cannot see or
  approve the first organization's approval request (403/404).

If this sequence works end to end, for real, that is the demo. That is what goes in a video, a
GitHub README, a Show HN post. Nothing else in this document matters until this works.

---

## 6. Auth (kept intentionally minimal for MVP)

- Email + password signup/login, Argon2id hashing. Passkeys and MFA are Phase 2, not now — don't
  build the plumbing for them yet, it adds surface area before the core loop is proven.
- JWT access token, 15 minute expiry. Refresh token, 7 day expiry, stored httpOnly cookie.
- One API key per organization for machine-to-machine calls (agents calling
  `/v1/authorization/check` directly). Store a hash, show the raw key exactly once on creation.
- Every request must resolve `organization_id` server-side from the authenticated principal — never
  trust an `organization_id` field sent in a request body.

---

## 7. UI/UX — how to make sure this does not look AI-generated

This is the part most likely to go wrong, so be explicit. A generic AI-generated UI has a specific,
recognizable signature: purple-to-blue gradients, generic rounded cards with soft shadows on a
white background, emoji as icons, Inter font at default weight everywhere, centered hero text with
a gradient headline, and identical spacing on every section. Avoid all of that specifically.

**Design direction: technical, quiet, high-contrast, information-dense.** Think developer tool
(Linear, Stripe Dashboard, Vercel), not marketing SaaS template.

Concrete rules:

- **Color:** near-black background (`#0B0C0E`), off-white text (`#EDEEF0`), one accent color used
  sparingly for interactive elements and decision states only — not for decoration. Define exact
  values in `tokens.css`, do not invent new colors inline anywhere else in the codebase.
- **Decision colors are semantic and consistent everywhere:** ALLOW = a controlled green, DENY = a
  controlled red, REQUIRE_APPROVAL = amber. These three colors appear nowhere else in the UI. That
  reservation is what makes them mean something when a user sees them.
- **Typography:** one serif or one distinctive sans for headings (not Inter/system default), one
  monospace for anything technical — request IDs, policy JSON, API keys, audit log entries. The
  monospace font doing double duty as "this is real machine data" is a small detail that reads as
  deliberate, not templated.
- **No decorative gradients, no glassmorphism, no floating blob shapes, no stock illustration.**
  If a visual is needed, it's a real screenshot of the real dashboard or an actual data
  visualization, never generic decoration.
- **Density over whitespace.** This is a security/ops tool. Tables should look like tables real
  engineers use — tight rows, monospace numeric columns, real timestamps, real request IDs. Do not
  pad it out with big empty cards the way marketing templates do.
- **Every state must exist for real:** loading, empty, error, and populated. An empty policy list
  should say "No policies yet" with a real create action, not be hidden behind fake seeded data.
- **Motion:** minimal. A 120–150ms opacity/transform transition on state changes is enough. No
  scroll-triggered animations, no bouncing, no parallax.
- **Build the primitives once** (`Button`, `Table`, `Badge`, `Input`, `Card`) in
  `components/primitives/`, and reuse them everywhere. A UI built from five consistent primitives
  reads as "one person designed a system." A UI where every page invents its own button style reads
  as generated page-by-page — which is exactly the tell you're trying to avoid.

Before writing any component, Codex should look at the actual dashboards of Linear, Stripe, and
Vercel for reference, not generic "SaaS landing page" inspiration.

---

## 8. Coding standards Codex must follow throughout

- Every backend function that makes an authorization decision must have a unit test with at least
  the three cases: allow, deny, require_approval, and one edge case (no matching rule → deny).
- No silent excepts. Every caught exception is logged with context or re-raised.
- No `Any` types in Pydantic schemas or TypeScript interfaces. If the shape is genuinely dynamic
  (policy `context` field), type it as `dict[str, str | int | float | bool]`, not `Any`.
- Every migration is reversible (`downgrade()` implemented, not `pass`).
- Every new endpoint gets a docstring describing the real behavior, and that docstring is what
  `docs/api-reference.md` is built from — keep them in sync in the same commit.
- Commit messages describe what changed and why in one line, not "update files."
- No commented-out code left in. No `TODO` without a linked issue or a one-line reason it's
  deferred.

---

## 9. Build order (do not skip ahead)

**Phase 0 — Scaffolding (half a day)**
Docker Compose brings up Postgres + empty FastAPI + empty Vite app. Health check endpoint returns
200. CI runs lint + type check on an empty repo. Nothing else.

**Phase 1 — The core loop (this is the actual product, see Section 5)**
Auth, organizations, agents, policies, the `/v1/authorization/check` endpoint, approvals, audit
log. Backend only, tested via curl/pytest, no frontend needed yet to prove it works.
*Do not proceed past this phase until the acceptance test in Section 5 passes for real.*

**Phase 2 — Minimal dashboard**
Login/signup screens, agent list, policy list + a simple rule editor (form-based, not raw JSON
initially), approval queue with real approve/deny buttons, audit log table. All of it reading and
writing the real Phase 1 API. No mock data anywhere in the frontend codebase, ever.

**Phase 3 — Demo agent**
A small standalone script (`scripts/demo_agent.py`) that uses an LLM to propose an action in
natural language ("refund this $500 order"), translates it to a structured `authorization.check`
call, and prints the real decision. This is what makes the "AI agent authorization" story concrete
and demoable instead of theoretical.

**Phase 4 — Polish for demo**
Real seed script for a clean demo org (clearly labeled as a demo seed, not fake production data),
README with the exact five-command run instructions, a 90-second screen recording of the Section 5
flow.

Stop here for the initial release. Ship it, get it in front of real people, before building
anything further.

---

## 10. Explicitly deferred (do not build yet, but architecture shouldn't block it later)

Passkeys/MFA, business/document verification, risk scoring engine, webhooks, business verification,
public Trust Profile pages, admin panel, SDKs, compliance program. These come from the original
Master Build Bible and remain the long-term direction — they are not being discarded, just
sequenced after there's proof the core loop is something people actually want.

---

## 11. Definition of done for this build

Not "every screen exists." Done means: a stranger can clone the repo, run one Docker Compose
command, hit the real API, watch a real agent action get allowed, denied, or sent to approval by a
real policy engine, approve it through a real UI, and see the whole thing in a real audit log —
with nothing in that sequence faked, scripted, or hardcoded.
