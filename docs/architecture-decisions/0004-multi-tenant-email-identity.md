# 0004 — Email is unique per organization, not globally

TrustLayer is a multi-tenant system, so different organizations can legitimately have users with the same email address. The database now enforces uniqueness on `(organization_id, email)` instead of a global email unique constraint.

This means login identity is effectively `(organization, email, password)`. The current MVP login flow still accepts email and password first, but if multiple organizations share the same email, the backend now rejects the attempt and asks the caller to provide the organization context rather than guessing.
