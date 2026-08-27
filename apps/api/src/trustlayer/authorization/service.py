from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import secrets
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from trustlayer.auth.dependencies import OrganizationPrincipal
from trustlayer.models.agent import Agent, AgentStatus
from trustlayer.models.approval import ApprovalRequest, ApprovalStatus
from trustlayer.models.audit import AuditLog
from trustlayer.models.authorization import AuthorizationRequest
from trustlayer.models.policy import Policy
from trustlayer.policy_engine.evaluator import evaluate
from trustlayer.schemas.common import RequestContext


@dataclass(frozen=True)
class AuthorizationDecisionResult:
    decision: str
    reason: str
    policy_version: int
    request_id: str
    approval_request_id: str | None


async def check_authorization(
    *,
    principal: OrganizationPrincipal,
    agent_id: str,
    action: str,
    resource: str,
    context: RequestContext,
    session: AsyncSession,
) -> AuthorizationDecisionResult:
    requested_agent_id = UUID(agent_id)
    if principal.agent_id is not None and principal.agent_id != requested_agent_id:
        raise LookupError("agent not found")

    agent = await session.scalar(
        select(Agent).where(
            Agent.id == requested_agent_id,
            Agent.organization_id == principal.organization_id,
        )
    )
    if agent is None:
        raise LookupError("agent not found")
    if agent.status is not AgentStatus.active:
        raise RuntimeError("agent is not active")

    policy = await session.scalar(
        select(Policy)
        .where(Policy.organization_id == principal.organization_id, Policy.is_active.is_(True))
        .order_by(desc(Policy.version))
    )
    if policy is None:
        raise RuntimeError("no active policy")

    decision, reason = evaluate(policy.rules, action, context)
    request_id = f"req_{secrets.token_hex(5)}"
    approval_request_id: str | None = None

    authorization_request = AuthorizationRequest(
        organization_id=principal.organization_id,
        agent_id=agent.id,
        action=action,
        resource=resource,
        context=context,
        policy_id=policy.id,
        policy_version=policy.version,
        decision=decision,
        reason=reason,
        request_id=request_id,
    )
    session.add(authorization_request)
    await session.flush()

    if decision == "REQUIRE_APPROVAL":
        approval = ApprovalRequest(
            authorization_request_id=authorization_request.id,
            status=ApprovalStatus.pending,
            expires_at=datetime.now(UTC) + timedelta(hours=24),
        )
        session.add(approval)
        await session.flush()
        approval_request_id = str(approval.id)

    session.add(
        AuditLog(
            organization_id=principal.organization_id,
            actor_type="agent",
            actor_id=str(agent.id),
            action=action,
            resource=resource,
            decision=decision,
            reason=reason,
            policy_version=policy.version,
            request_id=request_id,
        )
    )
    await session.commit()

    return AuthorizationDecisionResult(
        decision=decision,
        reason=reason,
        policy_version=policy.version,
        request_id=request_id,
        approval_request_id=approval_request_id,
    )
