from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from trustlayer.auth.security import create_access_token, create_refresh_token, hash_password, verify_password
from trustlayer.models.organization import Organization
from trustlayer.models.user import User, UserRole


@dataclass(frozen=True)
class AuthTokens:
    access_token: str
    refresh_token: str
    organization_id: str
    email: str


async def signup(*, name: str, email: str, password: str, session: AsyncSession) -> AuthTokens:
    normalized_email = email.lower()

    organization = Organization(name=name)
    user = User(
        organization_id=organization.id,
        email=normalized_email,
        password_hash=hash_password(password),
        role=UserRole.OWNER,
    )

    session.add(organization)
    await session.flush()
    user.organization_id = organization.id
    session.add(user)
    await session.commit()

    return AuthTokens(
        access_token=create_access_token(user_id=user.id, organization_id=organization.id),
        refresh_token=create_refresh_token(user_id=user.id, organization_id=organization.id),
        organization_id=str(organization.id),
        email=user.email,
    )


async def login_for_organization(
    *,
    email: str,
    password: str,
    organization_name: str | None,
    session: AsyncSession,
) -> AuthTokens:
    normalized_email = email.lower()
    statement = (
        select(User, Organization)
        .join(Organization, Organization.id == User.organization_id)
        .where(User.email == normalized_email)
    )
    rows = (await session.execute(statement)).all()
    if len(rows) == 0:
        raise ValueError("invalid credentials")

    if organization_name is not None:
        requested_name = organization_name.strip().lower()
        rows = [row for row in rows if row[1].name.lower() == requested_name]
        if len(rows) == 0:
            raise ValueError("invalid credentials")

    if len(rows) > 1:
        raise ValueError("multiple organizations use this email; provide organization name")

    user, _organization = rows[0]
    if not verify_password(user.password_hash, password):
        raise ValueError("invalid credentials")

    return AuthTokens(
        access_token=create_access_token(user_id=user.id, organization_id=user.organization_id),
        refresh_token=create_refresh_token(user_id=user.id, organization_id=user.organization_id),
        organization_id=str(user.organization_id),
        email=user.email,
    )


async def refresh_access_token(*, refresh_token: str, session: AsyncSession) -> str:
    from trustlayer.auth.security import decode_token

    payload = decode_token(refresh_token, expected_type="refresh")
    user = await session.get(User, UUID(payload.subject))
    if user is None or str(user.organization_id) != payload.organization_id:
        raise ValueError("invalid refresh token")
    return create_access_token(user_id=user.id, organization_id=user.organization_id)
