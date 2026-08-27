from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column
from trustlayer.db.base import Base


class AuthorizationRequest(Base):
    __tablename__ = "authorization_requests"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    agent_id: Mapped[UUID] = mapped_column(ForeignKey("agents.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(200), nullable=False)
    resource: Mapped[str] = mapped_column(String(500), nullable=False)
    context: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    policy_id: Mapped[UUID] = mapped_column(ForeignKey("policies.id"), nullable=False)
    policy_version: Mapped[int] = mapped_column(Integer, nullable=False)
    decision: Mapped[str] = mapped_column(String(32), nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    request_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
