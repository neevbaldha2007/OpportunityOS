import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    SmallInteger,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from app.db import Base, GUID, JSONList


def utcnow():
    return datetime.now(timezone.utc)


class CareerGoal(Base):
    __tablename__ = "career_goals"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    target_role = Column(String(120), nullable=False)
    goal_statement = Column(String(280), nullable=True)
    timeline_months = Column(SmallInteger, default=3, nullable=False)
    opportunity_types = Column(JSONList, default=lambda: ["internship"], nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    user = relationship("User", back_populates="career_goals")
    agent_sessions = relationship("AgentSession", back_populates="career_goal")

    __table_args__ = (
        CheckConstraint("timeline_months IN (1,3,6,12)", name="chk_career_goal_timeline"),
    )
