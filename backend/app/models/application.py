import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Date,
    DateTime,
    Text,
    JSON,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from app.db import Base, GUID


def utcnow():
    return datetime.now(timezone.utc)


class Application(Base):
    __tablename__ = "applications"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    opportunity_id = Column(GUID, ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(15), default="planned", nullable=False, index=True)
    applied_on = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    status_history = Column(JSON, default=list, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    user = relationship("User", back_populates="applications")
    opportunity = relationship("Opportunity", back_populates="applications")

    __table_args__ = (
        UniqueConstraint("user_id", "opportunity_id", name="uq_application_user_opportunity"),
        CheckConstraint(
            "status IN ('planned','applied','interviewing','offer','rejected','withdrawn')",
            name="chk_application_status",
        ),
    )
