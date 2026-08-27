from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from trustlayer.auth.security import issue_api_key
from trustlayer.models.organization import Organization
from trustlayer.models.user import User, UserRole


async def create_api_key(*, user: User, session: AsyncSession) -> str:
    if user.role not in {UserRole.OWNER, UserRole.ADMIN}:
        raise PermissionError("only owners or admins can issue API keys")

    organization = await session.get(Organization, user.organization_id)
    if organization is None:
        raise LookupError("organization not found")

    raw_key, hashed_key = issue_api_key()
    organization.api_key_hash = hashed_key
    session.add(organization)
    await session.commit()
    return raw_key
