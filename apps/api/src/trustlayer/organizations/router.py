from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from trustlayer.auth.dependencies import get_current_user, get_db
from trustlayer.models.user import User
from trustlayer.organizations.service import create_api_key
from trustlayer.schemas.organizations import ApiKeyResponse

router = APIRouter(prefix="/v1/organizations", tags=["organizations"])


@router.post("/api-key", response_model=ApiKeyResponse)
async def create_api_key_route(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> ApiKeyResponse:
    """Generate a new organization API key and return the raw key exactly once."""

    try:
        api_key = await create_api_key(user=user, session=session)
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return ApiKeyResponse(api_key=api_key)
