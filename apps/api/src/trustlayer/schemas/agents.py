from datetime import datetime

from pydantic import BaseModel, Field


class CreateAgentRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class AgentResponse(BaseModel):
    id: str
    name: str
    status: str
    created_at: datetime


class CreateAgentResponse(BaseModel):
    id: str


class AgentKeyResponse(BaseModel):
    id: str
    key_prefix: str
    hint: str
    created_at: datetime
    revoked_at: datetime | None
    last_used_at: datetime | None


class RotateAgentKeyResponse(BaseModel):
    key_id: str
    api_key: str
