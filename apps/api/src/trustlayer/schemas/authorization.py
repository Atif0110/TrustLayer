from pydantic import BaseModel, Field

from trustlayer.schemas.common import RequestContext


class AuthorizationCheckRequest(BaseModel):
    agent_id: str
    action: str = Field(min_length=1, max_length=200)
    resource: str = Field(min_length=1, max_length=500)
    context: RequestContext


class AuthorizationCheckResponse(BaseModel):
    decision: str
    reason: str
    policy_version: int
    request_id: str
    approval_request_id: str | None = None
