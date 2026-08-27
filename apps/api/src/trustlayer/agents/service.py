from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import cast, select
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.asyncio import AsyncSession

from trustlayer.auth.security import issue_api_key
from trustlayer.models.agent import Agent, AgentStatus
from trustlayer.models.agent_key import AgentKey
from trustlayer.models.user import User


async def create_agent(*, name: str, user: User, session: AsyncSession) -> Agent:
    agent = Agent(
        organization_id=user.organization_id,
        owner_id=user.id,
        name=name,
        status=AgentStatus.active,
    )
    session.add(agent)
    await session.commit()
    return agent


async def list_agents(*, user: User, session: AsyncSession) -> list[Agent]:
    result = await session.scalars(
        select(Agent)
        .where(Agent.organization_id == user.organization_id)
        .order_by(Agent.created_at)
    )
    return list(result.all())


async def get_agent(*, agent_id: str, user: User, session: AsyncSession) -> Agent:
    agent = await session.scalar(
        select(Agent).where(Agent.id == cast(agent_id, PGUUID(as_uuid=True)), Agent.organization_id == user.organization_id)
    )
    if agent is None:
        raise LookupError("agent not found")
    return agent


async def list_agent_keys(*, agent_id: str, user: User, session: AsyncSession) -> list[AgentKey]:
    await get_agent(agent_id=agent_id, user=user, session=session)
    result = await session.scalars(
        select(AgentKey)
        .where(AgentKey.agent_id == cast(agent_id, PGUUID(as_uuid=True)), AgentKey.organization_id == user.organization_id)
        .order_by(AgentKey.created_at.desc())
    )
    return list(result.all())


async def rotate_agent_key(*, agent_id: str, user: User, session: AsyncSession) -> tuple[AgentKey, str]:
    agent = await get_agent(agent_id=agent_id, user=user, session=session)
    active_keys = await session.scalars(
        select(AgentKey).where(
            AgentKey.agent_id == agent.id,
            AgentKey.organization_id == user.organization_id,
            AgentKey.revoked_at.is_(None),
        )
    )
    now = datetime.now(UTC)
    for key in active_keys:
        key.revoked_at = now
        session.add(key)

    raw_key, key_prefix, key_hash = issue_api_key()
    agent_key = AgentKey(
        organization_id=user.organization_id,
        agent_id=agent.id,
        key_prefix=key_prefix,
        key_hash=key_hash,
    )
    session.add(agent_key)
    await session.commit()
    return agent_key, raw_key


async def revoke_agent_key(*, agent_id: str, key_id: str, user: User, session: AsyncSession) -> AgentKey:
    await get_agent(agent_id=agent_id, user=user, session=session)
    agent_key = await session.scalar(
        select(AgentKey).where(
            AgentKey.id == cast(key_id, PGUUID(as_uuid=True)),
            AgentKey.agent_id == cast(agent_id, PGUUID(as_uuid=True)),
            AgentKey.organization_id == user.organization_id,
        )
    )
    if agent_key is None:
        raise LookupError("agent key not found")
    if agent_key.revoked_at is None:
        agent_key.revoked_at = datetime.now(UTC)
        session.add(agent_key)
        await session.commit()
    return agent_key
