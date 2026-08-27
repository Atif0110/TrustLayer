from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from trustlayer.agents.service import (
    create_agent,
    get_agent,
    list_agent_keys,
    list_agents,
    revoke_agent_key,
    rotate_agent_key,
)
from trustlayer.auth.dependencies import get_current_user, get_db
from trustlayer.models.user import User
from trustlayer.schemas.agents import (
    AgentKeyResponse,
    AgentResponse,
    CreateAgentRequest,
    CreateAgentResponse,
    RotateAgentKeyResponse,
)

router = APIRouter(prefix="/v1/agents", tags=["agents"])


def build_key_hint(*, revoked_at: object, last_used_at: object) -> str:
    if revoked_at is not None:
        return "Revoked key"
    if last_used_at is not None:
        return "Active key used recently"
    return "Active key never used"


@router.post("", response_model=CreateAgentResponse)
async def create_agent_route(
    body: CreateAgentRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> CreateAgentResponse:
    """Create an organization-scoped agent owned by the authenticated user."""

    agent = await create_agent(name=body.name, user=user, session=session)
    return CreateAgentResponse(id=str(agent.id))


@router.get("", response_model=list[AgentResponse])
async def list_agents_route(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[AgentResponse]:
    """List agents that belong to the authenticated user's organization."""

    agents = await list_agents(user=user, session=session)
    return [
        AgentResponse(
            id=str(agent.id),
            name=agent.name,
            status=agent.status.value,
            created_at=agent.created_at,
        )
        for agent in agents
    ]


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent_route(
    agent_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> AgentResponse:
    """Fetch a single agent that belongs to the authenticated user's organization."""

    try:
        agent = await get_agent(agent_id=agent_id, user=user, session=session)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return AgentResponse(id=str(agent.id), name=agent.name, status=agent.status.value, created_at=agent.created_at)


@router.get("/{agent_id}/keys", response_model=list[AgentKeyResponse])
async def list_agent_keys_route(
    agent_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[AgentKeyResponse]:
    """List key metadata for one agent. Raw key material is never returned here."""

    try:
        keys = await list_agent_keys(agent_id=agent_id, user=user, session=session)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return [
        AgentKeyResponse(
            id=str(key.id),
            key_prefix=key.key_prefix,
            hint=build_key_hint(revoked_at=key.revoked_at, last_used_at=key.last_used_at),
            created_at=key.created_at,
            revoked_at=key.revoked_at,
            last_used_at=key.last_used_at,
        )
        for key in keys
    ]


@router.post("/{agent_id}/keys/rotate", response_model=RotateAgentKeyResponse)
async def rotate_agent_key_route(
    agent_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> RotateAgentKeyResponse:
    """Rotate the active key set for one agent and return the new raw key exactly once."""

    try:
        agent_key, raw_key = await rotate_agent_key(agent_id=agent_id, user=user, session=session)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return RotateAgentKeyResponse(key_id=str(agent_key.id), api_key=raw_key)


@router.post("/{agent_id}/keys/{key_id}/revoke", response_model=AgentKeyResponse)
async def revoke_agent_key_route(
    agent_id: str,
    key_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> AgentKeyResponse:
    """Revoke one existing agent key without creating a replacement."""

    try:
        agent_key = await revoke_agent_key(agent_id=agent_id, key_id=key_id, user=user, session=session)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return AgentKeyResponse(
        id=str(agent_key.id),
        key_prefix=agent_key.key_prefix,
        hint=build_key_hint(revoked_at=agent_key.revoked_at, last_used_at=agent_key.last_used_at),
        created_at=agent_key.created_at,
        revoked_at=agent_key.revoked_at,
        last_used_at=agent_key.last_used_at,
    )
