from datetime import datetime

from pydantic import BaseModel


class PendingApprovalResponse(BaseModel):
    id: str
    request_id: str
    action: str
    resource: str
    expires_at: datetime


class ApprovalActionResponse(BaseModel):
    status: str
