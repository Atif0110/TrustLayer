from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from fastapi import Cookie, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from trustlayer.auth.security import decode_token, verify_api_key
from trustlayer.config import settings
from trustlayer.db.session import SessionLocal
from trustlayer.models.agent_key import AgentKey
from trustlayer.models.user import User


@dataclass(frozen=True)
class OrganizationPrincipal:
    organization_id: UUID
    actor_id: str
    actor_type: str
    agent_id: UUID | None = None


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


async def get_current_user(
    authorization: str | None = Header(default=None),
    session: AsyncSession = Depends(get_db),
) -> User:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing access token")

    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = decode_token(token, expected_type="access")
        user_id = UUID(payload.subject)
        organization_id = UUID(payload.organization_id)
    except ValueError as error:
        raise HTTPException(status_code=401, detail="invalid access token") from error

    user = await session.get(User, user_id)
    if user is None or user.organization_id != organization_id:
        raise HTTPException(status_code=401, detail="invalid access token")
    return user


async def get_current_organization_principal(
    authorization: str | None = Header(default=None),
    session: AsyncSession = Depends(get_db),
) -> OrganizationPrincipal:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing credentials")

    credential = authorization.removeprefix("Bearer ").strip()
    try:
        payload = decode_token(credential, expected_type="access")
        user_id = UUID(payload.subject)
        organization_id = UUID(payload.organization_id)
        user = await session.get(User, user_id)
        if user is None or user.organization_id != organization_id:
            raise HTTPException(status_code=401, detail="invalid access token")
        return OrganizationPrincipal(
            organization_id=user.organization_id,
            actor_id=str(user.id),
            actor_type="user",
            agent_id=None,
        )
    except ValueError:
        parts = credential.split("_", 2)
        if len(parts) != 3 or parts[0] != "tlk":
            raise HTTPException(status_code=401, detail="invalid credentials")
        prefix = parts[1]
        agent_key = await session.scalar(
            select(AgentKey).where(AgentKey.key_prefix == prefix, AgentKey.revoked_at.is_(None))
        )
        if agent_key is None or not verify_api_key(credential, agent_key.key_hash):
            raise HTTPException(status_code=401, detail="invalid credentials")
        agent_key.last_used_at = datetime.now(UTC)
        session.add(agent_key)
        await session.commit()
        return OrganizationPrincipal(
            organization_id=agent_key.organization_id,
            actor_id=str(agent_key.agent_id),
            actor_type="agent",
            agent_id=agent_key.agent_id,
        )


def get_refresh_token_cookie(
    refresh_token: str | None = Cookie(default=None, alias=settings.refresh_cookie_name),
) -> str:
    if refresh_token is None or refresh_token == "":
        raise HTTPException(status_code=401, detail="missing refresh token")
    return refresh_token
