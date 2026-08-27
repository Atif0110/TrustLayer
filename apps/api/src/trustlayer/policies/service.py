from __future__ import annotations

from sqlalchemy import desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from trustlayer.models.policy import Policy
from trustlayer.models.user import User
from trustlayer.policy_engine.versioning import next_policy_version
from trustlayer.schemas.common import ScalarValue

RuleRecord = dict[str, dict[str, ScalarValue] | str]


async def create_policy(
    *, name: str, rules: list[RuleRecord], user: User, session: AsyncSession
) -> Policy:
    version = await next_policy_version(organization_id=user.organization_id, session=session)
    await session.execute(
        update(Policy).where(Policy.organization_id == user.organization_id).values(is_active=False)
    )
    policy = Policy(
        organization_id=user.organization_id,
        name=name,
        version=version,
        is_active=True,
        rules=rules,
    )
    session.add(policy)
    await session.commit()
    return policy


async def list_policies(*, user: User, session: AsyncSession) -> list[Policy]:
    result = await session.scalars(
        select(Policy)
        .where(Policy.organization_id == user.organization_id)
        .order_by(desc(Policy.version))
    )
    return list(result.all())
