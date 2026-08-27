from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from trustlayer.approvals.service import decide_approval, list_pending_approvals
from trustlayer.auth.dependencies import get_current_user, get_db
from trustlayer.models.user import User
from trustlayer.schemas.approvals import ApprovalActionResponse, PendingApprovalResponse

router = APIRouter(prefix="/v1/approvals", tags=["approvals"])


@router.get("", response_model=list[PendingApprovalResponse])
async def list_approvals_route(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[PendingApprovalResponse]:
    """List pending approval requests that belong to the authenticated user's organization."""

    rows = await list_pending_approvals(user=user, session=session)
    return [
        PendingApprovalResponse(
            id=str(approval.id),
            request_id=request.request_id,
            action=request.action,
            resource=request.resource,
            expires_at=approval.expires_at,
        )
        for approval, request in rows
    ]


@router.post("/{approval_id}/approve", response_model=ApprovalActionResponse)
async def approve_route(
    approval_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> ApprovalActionResponse:
    """Approve a pending request for the authenticated user's organization."""

    try:
        status_value = await decide_approval(approval_id=approval_id, user=user, session=session, approve=True)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return ApprovalActionResponse(status=status_value)


@router.post("/{approval_id}/deny", response_model=ApprovalActionResponse)
async def deny_route(
    approval_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> ApprovalActionResponse:
    """Deny a pending request for the authenticated user's organization."""

    try:
        status_value = await decide_approval(approval_id=approval_id, user=user, session=session, approve=False)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return ApprovalActionResponse(status=status_value)
