from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from trustlayer.auth.dependencies import get_current_user, get_db
from trustlayer.models.user import User
from trustlayer.policies.service import create_policy, list_policies
from trustlayer.schemas.policies import CreatePolicyRequest, CreatePolicyResponse, PolicyResponse

router = APIRouter(prefix="/v1/policies", tags=["policies"])


@router.post("", response_model=CreatePolicyResponse)
async def create_policy_route(
    body: CreatePolicyRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> CreatePolicyResponse:
    """Create a new active policy version for the authenticated user's organization."""

    rules = [rule.model_dump(by_alias=True, exclude_none=True) for rule in body.rules]
    policy = await create_policy(name=body.name, rules=rules, user=user, session=session)
    return CreatePolicyResponse(id=str(policy.id), version=policy.version)


@router.get("", response_model=list[PolicyResponse])
async def list_policies_route(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[PolicyResponse]:
    """List policy versions for the authenticated user's organization, newest first."""

    policies = await list_policies(user=user, session=session)
    return [
        PolicyResponse(
            id=str(policy.id),
            name=policy.name,
            version=policy.version,
            is_active=policy.is_active,
            rules=policy.rules,
            created_at=policy.created_at,
        )
        for policy in policies
    ]
