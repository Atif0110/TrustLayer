from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from trustlayer.models.audit import AuditLog
from trustlayer.models.user import User


async def list_audit_events(*, user: User, session: AsyncSession) -> list[AuditLog]:
    events = await session.scalars(
        select(AuditLog)
        .where(AuditLog.organization_id == user.organization_id)
        .order_by(AuditLog.created_at)
    )
    return list(events.all())
