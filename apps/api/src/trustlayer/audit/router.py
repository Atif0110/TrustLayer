from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from trustlayer.audit.service import list_audit_events
from trustlayer.auth.dependencies import get_current_user, get_db
from trustlayer.models.user import User
from trustlayer.schemas.audit import AuditEventResponse

router = APIRouter(prefix="/v1/audit-events", tags=["audit"])


@router.get("", response_model=list[AuditEventResponse])
async def list_audit_route(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[AuditEventResponse]:
    """Return append-only audit events for the authenticated user's organization in time order."""

    events = await list_audit_events(user=user, session=session)
    return [
        AuditEventResponse(
            request_id=event.request_id,
            decision=event.decision,
            action=event.action,
            resource=event.resource,
            reason=event.reason,
            policy_version=event.policy_version,
            created_at=event.created_at,
        )
        for event in events
    ]
