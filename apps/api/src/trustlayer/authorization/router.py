from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from trustlayer.auth.dependencies import OrganizationPrincipal, get_current_organization_principal, get_db
from trustlayer.authorization.service import check_authorization
from trustlayer.schemas.authorization import AuthorizationCheckRequest, AuthorizationCheckResponse

router = APIRouter(prefix="/v1/authorization", tags=["authorization"])


@router.post("/check", response_model=AuthorizationCheckResponse)
async def authorization_check_route(
    body: AuthorizationCheckRequest,
    principal: OrganizationPrincipal = Depends(get_current_organization_principal),
    session: AsyncSession = Depends(get_db),
) -> AuthorizationCheckResponse:
    """Evaluate the active organization policy for an agent action and persist the audited result."""

    try:
        result = await check_authorization(
            principal=principal,
            agent_id=body.agent_id,
            action=body.action,
            resource=body.resource,
            context=body.context,
            session=session,
        )
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

    return AuthorizationCheckResponse(
        decision=result.decision,
        reason=result.reason,
        policy_version=result.policy_version,
        request_id=result.request_id,
        approval_request_id=result.approval_request_id,
    )
