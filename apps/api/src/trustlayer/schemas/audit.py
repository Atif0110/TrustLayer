from datetime import datetime

from pydantic import BaseModel


class AuditEventResponse(BaseModel):
    request_id: str
    decision: str
    action: str
    resource: str
    reason: str
    policy_version: int
    created_at: datetime
