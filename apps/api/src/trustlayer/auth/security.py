from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from fastapi import Response
from jwt import InvalidTokenError

from trustlayer.config import settings

password_hasher = PasswordHasher()


@dataclass(frozen=True)
class TokenPayload:
    subject: str
    organization_id: str
    token_type: str


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return password_hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def _encode_token(
    *, user_id: UUID, organization_id: UUID, token_type: str, expires_at: datetime
) -> str:
    payload = {
        "sub": str(user_id),
        "org": str(organization_id),
        "type": token_type,
        "iss": settings.jwt_issuer,
        "exp": expires_at,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def create_access_token(*, user_id: UUID, organization_id: UUID) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_minutes)
    return _encode_token(
        user_id=user_id,
        organization_id=organization_id,
        token_type="access",
        expires_at=expires_at,
    )


def create_refresh_token(*, user_id: UUID, organization_id: UUID) -> str:
    expires_at = datetime.now(UTC) + timedelta(days=settings.refresh_token_days)
    return _encode_token(
        user_id=user_id,
        organization_id=organization_id,
        token_type="refresh",
        expires_at=expires_at,
    )


def decode_token(token: str, *, expected_type: str) -> TokenPayload:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"],
            issuer=settings.jwt_issuer,
        )
    except InvalidTokenError as error:
        raise ValueError("invalid token") from error

    if payload.get("type") != expected_type:
        raise ValueError("invalid token type")

    subject = payload.get("sub")
    organization_id = payload.get("org")
    if not isinstance(subject, str) or not isinstance(organization_id, str):
        raise ValueError("invalid token payload")
    return TokenPayload(subject=subject, organization_id=organization_id, token_type=expected_type)


def attach_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=settings.refresh_token_days * 24 * 60 * 60,
        domain=settings.cookie_domain,
        path="/",
    )


def clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.refresh_cookie_name,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        domain=settings.cookie_domain,
        path="/",
    )


def issue_api_key() -> tuple[str, str, str]:
    prefix = secrets.token_hex(6)
    secret = secrets.token_urlsafe(24)
    raw_key = f"tlk_{prefix}_{secret}"
    hashed_key = hash_api_key(raw_key)
    return raw_key, prefix, hashed_key


def verify_api_key(raw_key: str, stored_hash: str | None) -> bool:
    if stored_hash is None:
        return False
    computed = hash_api_key(raw_key)
    return hmac.compare_digest(computed, stored_hash)
