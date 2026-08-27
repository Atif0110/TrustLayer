from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from trustlayer.models.policy import Policy


async def next_policy_version(*, organization_id: object, session: AsyncSession) -> int:
    latest_version = await session.scalar(
        select(Policy.version)
        .where(Policy.organization_id == organization_id)
        .order_by(desc(Policy.version))
    )
    return (latest_version or 0) + 1
