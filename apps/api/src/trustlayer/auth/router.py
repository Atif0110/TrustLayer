from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from trustlayer.auth.dependencies import get_db, get_refresh_token_cookie
from trustlayer.auth.rate_limit import (
    LOGIN_EMAIL_RULE,
    LOGIN_IP_RULE,
    SIGNUP_EMAIL_RULE,
    SIGNUP_IP_RULE,
    limiter,
)
from trustlayer.auth.security import attach_refresh_cookie, clear_refresh_cookie
from trustlayer.auth.service import login_for_organization, refresh_access_token, signup
from trustlayer.config import settings
from trustlayer.schemas.auth import AuthResponse, LoginRequest, RefreshResponse, SignupRequest

router = APIRouter(prefix="/v1/auth", tags=["auth"])


@router.post("/signup", response_model=AuthResponse)
async def signup_route(
    body: SignupRequest,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """Create an organization and owner account, then issue access and refresh credentials."""

    client_ip = request.client.host if request.client is not None else "unknown"
    if not limiter.allow(f"signup:ip:{client_ip}", SIGNUP_IP_RULE) or not limiter.allow(
        f"signup:email:{body.email}", SIGNUP_EMAIL_RULE
    ):
        raise HTTPException(status_code=429, detail="too many signup attempts")

    try:
        result = await signup(
            name=body.name, email=body.email, password=body.password, session=session
        )
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

    attach_refresh_cookie(response, result.refresh_token)
    return AuthResponse(
        access_token=result.access_token,
        expires_in=settings.access_token_minutes * 60,
        email=result.email,
        organization_id=result.organization_id,
    )


@router.post("/login", response_model=AuthResponse)
async def login_route(
    body: LoginRequest,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """Verify email/password credentials and rotate the refresh cookie for the signed-in user."""

    client_ip = request.client.host if request.client is not None else "unknown"
    if not limiter.allow(f"login:ip:{client_ip}", LOGIN_IP_RULE) or not limiter.allow(
        f"login:email:{body.email}", LOGIN_EMAIL_RULE
    ):
        raise HTTPException(status_code=429, detail="too many login attempts")

    try:
        result = await login_for_organization(
            email=body.email,
            password=body.password,
            organization_name=body.organization_name,
            session=session,
        )
    except ValueError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error

    attach_refresh_cookie(response, result.refresh_token)
    return AuthResponse(
        access_token=result.access_token,
        expires_in=settings.access_token_minutes * 60,
        email=result.email,
        organization_id=result.organization_id,
    )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_route(
    refresh_token: str = Depends(get_refresh_token_cookie),
    session: AsyncSession = Depends(get_db),
) -> RefreshResponse:
    """Issue a new short-lived access token from the httpOnly refresh cookie."""

    try:
        access_token = await refresh_access_token(refresh_token=refresh_token, session=session)
    except ValueError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error
    return RefreshResponse(
        access_token=access_token,
        expires_in=settings.access_token_minutes * 60,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_route(response: Response) -> Response:
    """Clear the refresh cookie for the current browser session."""

    clear_refresh_cookie(response)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
