# 0005 — Auth rate limiting is intentionally single-instance for the MVP

The signup and login endpoints use an in-memory sliding-window rate limiter inside the API process. This is enough for the current single-instance MVP and avoids introducing Redis or another shared dependency before the core product is proven.

This limiter does not share state across multiple processes or replicas and resets on restart. Before scaling the API horizontally, move these limits to a shared store such as Redis or a database-backed counter.
