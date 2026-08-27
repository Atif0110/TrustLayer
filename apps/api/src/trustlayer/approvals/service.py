from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from trustlayer.models.approval import ApprovalRequest, ApprovalStatus
from trustlayer.models.audit import AuditLog
from trustlayer.models.authorization import AuthorizationRequest
from trustlayer.models.user import User, UserRole


async def list_pending_approvals(*, user: User, session: AsyncSession) -> list[tuple[ApprovalRequest, AuthorizationRequest]]:
    rows = await session.execute(
        select(ApprovalRequest, AuthorizationRequest)
        .join(AuthorizationRequest)
        .where(
            AuthorizationRequest.organization_id == user.organization_id,
            ApprovalRequest.status == ApprovalStatus.pending,
        )
        .order_by(ApprovalRequest.requested_at)
    )
    return list(rows.all())


async def decide_approval(
    *,
    approval_id: str,
    user: User,
    session: AsyncSession,
    approve: bool,
) -> str:
    if user.role not in {UserRole.OWNER, UserRole.ADMIN}:
        raise PermissionError("only owners or admins can approve requests")

    approval = await session.scalar(
        select(ApprovalRequest)
        .join(AuthorizationRequest)
        .where(
            ApprovalRequest.id == UUID(approval_id),
            AuthorizationRequest.organization_id == user.organization_id,
        )
    )
    if approval is None:
        raise LookupError("approval not found")
    if approval.status != ApprovalStatus.pending:
        raise RuntimeError("approval is not pending")
    if approval.expires_at <= datetime.now(UTC):
        approval.status = ApprovalStatus.expired
        session.add(approval)
        await session.commit()
        raise RuntimeError("approval has expired")

    request = await session.get(AuthorizationRequest, approval.authorization_request_id)
    if request is None:
        raise LookupError("authorization request not found")

    approval.status = ApprovalStatus.approved if approve else ApprovalStatus.denied
    approval.decided_by = user.id
    approval.decided_at = datetime.now(UTC)

    audit_decision = "APPROVED" if approve else "DENIED"
    audit_reason = "approval granted" if approve else "approval denied"
    audit_action = "approval.approve" if approve else "approval.deny"

    session.add(approval)
    session.add(
        AuditLog(
            organization_id=user.organization_id,
            actor_type="user",
            actor_id=str(user.id),
            action=audit_action,
            resource=str(approval.id),
            decision=audit_decision,
            reason=audit_reason,
            policy_version=request.policy_version,
            request_id=request.request_id,
        )
    )
    await session.commit()

    return approval.status.value
