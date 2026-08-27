#!/usr/bin/env python3
"""Seed a clean demo organization using the real TrustLayer API."""

from __future__ import annotations

import json
import os
import time

import httpx


def main() -> int:
    base_url = os.environ.get("TRUSTLAYER_API_URL", "http://localhost:8000").rstrip("/")
    owner_email = os.environ.get("TRUSTLAYER_DEMO_EMAIL")
    owner_password = os.environ.get("TRUSTLAYER_DEMO_PASSWORD", "supersecret123")
    organization_name = os.environ.get("TRUSTLAYER_DEMO_ORG", "TrustLayer Demo")
    if owner_email is None:
        owner_email = f"owner+{int(time.time())}@demo.test"

    signup = httpx.post(
        f"{base_url}/v1/auth/signup",
        json={"name": organization_name, "email": owner_email, "password": owner_password},
        timeout=30,
    )
    signup.raise_for_status()
    token = signup.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    agent = httpx.post(f"{base_url}/v1/agents", headers=headers, json={"name": "demo-agent"}, timeout=30)
    agent.raise_for_status()

    policy = httpx.post(
        f"{base_url}/v1/policies",
        headers=headers,
        json={
            "name": "demo-policy",
            "rules": [
                {"if": {"action": "refund.create", "amount_lte": 100}, "then": "ALLOW"},
                {"if": {"action": "refund.create", "amount_gt": 100}, "then": "REQUIRE_APPROVAL"},
                {"if": {"action": "customer.delete"}, "then": "DENY"},
            ],
        },
        timeout=30,
    )
    policy.raise_for_status()

    print(json.dumps({
        "organization_id": signup.json()["organization_id"],
        "access_token": token,
        "agent_id": agent.json()["id"],
        "policy_version": policy.json()["version"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
