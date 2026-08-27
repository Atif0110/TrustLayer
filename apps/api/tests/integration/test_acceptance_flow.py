from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from testcontainers.community.postgres import PostgresContainer


@pytest.fixture(scope="session")
def test_database_url() -> str:
    configured = os.environ.get("TRUSTLAYER_TEST_DATABASE_URL")
    if configured is not None and configured != "":
        yield configured
        return

    with PostgresContainer("postgres:16") as postgres:
        yield postgres.get_connection_url().replace(
            "postgresql+psycopg2://", "postgresql+asyncpg://"
        )


@pytest.fixture
async def client(test_database_url: str, monkeypatch: pytest.MonkeyPatch) -> AsyncClient:
    monkeypatch.setenv("TRUSTLAYER_JWT_SECRET", "integration-test-secret-with-32-byte-minimum")
    monkeypatch.setenv("TRUSTLAYER_API_DATABASE_URL", test_database_url)

    for module_name in [name for name in sys.modules if name.startswith("trustlayer")]:
        del sys.modules[module_name]

    engine = create_async_engine(test_database_url)
    async with engine.begin() as connection:
        await connection.execute(text("DROP SCHEMA public CASCADE"))
        await connection.execute(text("CREATE SCHEMA public"))
    await engine.dispose()

    config = importlib.import_module("alembic.config").Config(
        str(Path(__file__).resolve().parents[2] / "alembic.ini")
    )
    config.set_main_option(
        "script_location", str(Path(__file__).resolve().parents[2] / "src/alembic")
    )
    importlib.import_module("alembic.command").upgrade(config, "head")

    app = importlib.import_module("trustlayer.main").create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client


async def expire_approval(test_database_url: str, approval_id: str) -> None:
    engine = create_async_engine(test_database_url)
    async with engine.begin() as connection:
        await connection.execute(
            text(
                "UPDATE approval_requests "
                "SET expires_at = NOW() - INTERVAL '1 hour' "
                "WHERE id = :approval_id"
            ),
            {"approval_id": approval_id},
        )
    await engine.dispose()


@pytest.mark.asyncio
async def test_section_five_acceptance_flow(client: AsyncClient) -> None:
    signup_one = await client.post(
        "/v1/auth/signup",
        json={"name": "Acme", "email": "owner@acme.test", "password": "supersecret123"},
    )
    assert signup_one.status_code == 200
    owner_one = signup_one.json()
    owner_one_headers = {"Authorization": f"Bearer {owner_one['access_token']}"}

    agent_one = await client.post("/v1/agents", json={"name": "ops-bot"}, headers=owner_one_headers)
    assert agent_one.status_code == 200
    agent_one_id = agent_one.json()["id"]

    policy_rules = [
        {"if": {"action": "refund.create", "amount_lte": 100}, "then": "ALLOW"},
        {"if": {"action": "refund.create", "amount_gt": 100}, "then": "REQUIRE_APPROVAL"},
        {"if": {"action": "customer.delete"}, "then": "DENY"},
    ]
    policy_one = await client.post(
        "/v1/policies",
        json={"name": "default refunds", "rules": policy_rules},
        headers=owner_one_headers,
    )
    assert policy_one.status_code == 200

    allow_response = await client.post(
        "/v1/authorization/check",
        json={
            "agent_id": agent_one_id,
            "action": "refund.create",
            "resource": "refund_50",
            "context": {"amount": 50, "currency": "USD"},
        },
        headers=owner_one_headers,
    )
    assert allow_response.status_code == 200
    assert allow_response.json()["decision"] == "ALLOW"

    approval_response = await client.post(
        "/v1/authorization/check",
        json={
            "agent_id": agent_one_id,
            "action": "refund.create",
            "resource": "refund_500",
            "context": {"amount": 500, "currency": "USD"},
        },
        headers=owner_one_headers,
    )
    assert approval_response.status_code == 200
    assert approval_response.json()["decision"] == "REQUIRE_APPROVAL"
    approval_id = approval_response.json()["approval_request_id"]
    assert UUID(approval_id)

    approve = await client.post(f"/v1/approvals/{approval_id}/approve", headers=owner_one_headers)
    assert approve.status_code == 200
    assert approve.json()["status"] == "approved"

    deny_response = await client.post(
        "/v1/authorization/check",
        json={
            "agent_id": agent_one_id,
            "action": "customer.delete",
            "resource": "customer_01",
            "context": {},
        },
        headers=owner_one_headers,
    )
    assert deny_response.status_code == 200
    assert deny_response.json()["decision"] == "DENY"

    audit = await client.get("/v1/audit-events", headers=owner_one_headers)
    assert audit.status_code == 200
    decisions = [entry["decision"] for entry in audit.json()]
    assert decisions == ["ALLOW", "REQUIRE_APPROVAL", "APPROVED", "DENY"]

    signup_two = await client.post(
        "/v1/auth/signup",
        json={"name": "Other Org", "email": "owner@other.test", "password": "supersecret123"},
    )
    assert signup_two.status_code == 200
    owner_two_headers = {"Authorization": f"Bearer {signup_two.json()['access_token']}"}

    foreign_approval = await client.post(
        f"/v1/approvals/{approval_id}/approve", headers=owner_two_headers
    )
    assert foreign_approval.status_code == 404


@pytest.mark.asyncio
async def test_expired_approval_cannot_be_approved(client: AsyncClient) -> None:
    signup = await client.post(
        "/v1/auth/signup",
        json={"name": "Acme", "email": "owner@acme.test", "password": "supersecret123"},
    )
    assert signup.status_code == 200
    headers = {"Authorization": f"Bearer {signup.json()['access_token']}"}

    agent = await client.post("/v1/agents", json={"name": "ops-bot"}, headers=headers)
    assert agent.status_code == 200
    policy = await client.post(
        "/v1/policies",
        json={
            "name": "refund policy",
            "rules": [
                {"if": {"action": "refund.create", "amount_gt": 100}, "then": "REQUIRE_APPROVAL"}
            ],
        },
        headers=headers,
    )
    assert policy.status_code == 200
    approval_response = await client.post(
        "/v1/authorization/check",
        json={
            "agent_id": agent.json()["id"],
            "action": "refund.create",
            "resource": "refund_500",
            "context": {"amount": 500},
        },
        headers=headers,
    )
    approval_id = approval_response.json()["approval_request_id"]
    await expire_approval(os.environ["TRUSTLAYER_API_DATABASE_URL"], approval_id)

    expire = await client.post(f"/v1/approvals/{approval_id}/approve", headers=headers)
    assert expire.status_code == 409
    assert expire.json()["detail"] == "approval has expired"


@pytest.mark.asyncio
async def test_login_requires_organization_name_when_email_exists_in_multiple_orgs(
    client: AsyncClient,
) -> None:
    signup_one = await client.post(
        "/v1/auth/signup",
        json={"name": "Acme", "email": "shared@acme.test", "password": "supersecret123"},
    )
    assert signup_one.status_code == 200

    signup_two = await client.post(
        "/v1/auth/signup",
        json={"name": "Beta", "email": "shared@acme.test", "password": "supersecret123"},
    )
    assert signup_two.status_code == 200

    ambiguous = await client.post(
        "/v1/auth/login",
        json={"email": "shared@acme.test", "password": "supersecret123"},
    )
    assert ambiguous.status_code == 401
    assert (
        ambiguous.json()["detail"]
        == "multiple organizations use this email; provide organization name"
    )

    resolved = await client.post(
        "/v1/auth/login",
        json={
            "email": "shared@acme.test",
            "password": "supersecret123",
            "organization_name": "Beta",
        },
    )
    assert resolved.status_code == 200
