# TrustLayer review notes

## Alignment check against the spec

- Phase 0 scaffold is present and the project structure follows the required router/service split.
- Phase 1 core loop is implemented with real DB writes, approval rows, audit rows, and cross-tenant denial.
- Phase 2 dashboard uses the real API and has loading, empty, error, and populated states.
- Phase 3 includes a real demo agent script.
- Phase 4 includes a real demo seed script, refreshed docs, and a final acceptance transcript.

## Security pass applied

- Removed the committed runtime secret file from the project output.
- Added Docker ignore files so host `node_modules` and virtualenv artifacts do not pollute image builds.
- Enforced active-agent-only authorization decisions.
- Restricted approvals to owner/admin roles and rejected expired requests.
- Added DB constraints for unique policy versions and an append-only trigger for `audit_logs`.

## Remaining caveat

- Auth rate limiting is intentionally in-memory for this MVP. It protects a single running API instance but does not yet coordinate limits across multiple replicas.
