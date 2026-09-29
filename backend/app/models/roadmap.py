import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    SmallInteger,
    Float,
    Text,
    JSON,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from app.db import Base, GUID, JSONList


def utcnow():
    return datetime.now(timezone.utc)


class SkillGap(Base):
    __tablename__ = "skill_gaps"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_session_id = Column(GUID, ForeignKey("agent_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(GUID, ForeignKey("skills.id", ondelete="RESTRICT"), nullable=False, index=True)
    demand_count = Column(SmallInteger, nullable=False)
    demand_pct = Column(Float, nullable=False)
    avg_uplift = Column(Float, default=0.0, nullable=False)
    priority_score = Column(Float, nullable=False)
    priority = Column(String(6), nullable=False)
    rank = Column(SmallInteger, nullable=False, index=True)
    opportunity_ids = Column(JSONList, default=list, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    user = relationship("User")
    agent_session = relationship("AgentSession", back_populates="skill_gaps")
    skill = relationship("Skill", back_populates="skill_gaps")

    __table_args__ = (
        UniqueConstraint("agent_session_id", "skill_id", name="uq_session_skill_gap"),
        CheckConstraint("priority IN ('high','medium','low')", name="chk_gap_priority"),
    )


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_session_id = Column(GUID, ForeignKey("agent_sessions.id", ondelete="CASCADE"), unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    summary = Column(Text, nullable=True)
    total_weeks = Column(SmallInteger, nullable=True)
    generation_method = Column(String(10), default="llm", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    user = relationship("User")
    agent_session = relationship("AgentSession", back_populates="roadmap")
    steps = relationship("RoadmapStep", back_populates="roadmap", cascade="all, delete-orphan", order_by="RoadmapStep.step_order")

    __table_args__ = (
        CheckConstraint("generation_method IN ('llm','template')", name="chk_roadmap_gen_method"),
    )


class RoadmapStep(Base):
    __tablename__ = "roadmap_steps"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    roadmap_id = Column(GUID, ForeignKey("roadmaps.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(GUID, ForeignKey("skills.id", ondelete="SET NULL"), nullable=True)
    opportunity_id = Column(GUID, ForeignKey("opportunities.id", ondelete="SET NULL"), nullable=True)
    step_order = Column(SmallInteger, nullable=False)
    step_type = Column(String(6), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    reason = Column(String(300), nullable=True)
    estimated_hours = Column(SmallInteger, nullable=True)
    action = Column(String(300), nullable=True)
    resource_query = Column(String(200), nullable=True)
    resources = Column(JSON, default=list, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    roadmap = relationship("Roadmap", back_populates="steps")
    skill = relationship("Skill")
    opportunity = relationship("Opportunity", back_populates="roadmap_steps")

    __table_args__ = (
        UniqueConstraint("roadmap_id", "step_order", name="uq_roadmap_step_order"),
        CheckConstraint("step_type IN ('learn','build','apply')", name="chk_roadmap_step_type"),
    )
