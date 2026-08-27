# 0003 — Split API by router/service and add refresh-cookie auth

The initial backend concentrated routing, database access, and policy decisions in `main.py`, which made the core loop hard to test and harder to audit. The codebase now follows the spec's router/service split for auth, agents, policies, authorization, approvals, audit, and organizations.

For browser auth, the dashboard now uses a short-lived access token plus an httpOnly refresh cookie. The frontend keeps only the access token in session storage, retries once through `/v1/auth/refresh`, and clears local session state if refresh fails.
