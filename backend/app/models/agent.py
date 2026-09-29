import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    SmallInteger,
    Integer,
    JSON,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from app.db import Base, GUID


def utcnow():
    return datetime.now(timezone.utc)


class AgentSession(Base):
    __tablename__ = "agent_sessions"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    career_goal_id = Column(GUID, ForeignKey("career_goals.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(12), default="queued", nullable=False, index=True)
    input_snapshot = Column(JSON, nullable=False)
    stages = Column(JSON, default=list, nullable=False)
    warnings = Column(JSON, default=list, nullable=False)
    result_summary = Column(JSON, nullable=True)
    error_code = Column(String(40), nullable=True)
    serp_calls_live = Column(SmallInteger, default=0, nullable=False)
    serp_calls_cached = Column(SmallInteger, default=0, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)

    user = relationship("User", back_populates="agent_sessions")
    career_goal = relationship("CareerGoal", back_populates="agent_sessions")
    matches = relationship("OpportunityMatch", back_populates="agent_session", cascade="all, delete-orphan")
    search_history = relationship("SearchHistory", back_populates="agent_session", cascade="all, delete-orphan")
    skill_gaps = relationship("SkillGap", back_populates="agent_session", cascade="all, delete-orphan")
    roadmap = relationship("Roadmap", back_populates="agent_session", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(
            "status IN ('queued','running','completed','partial','failed')",
            name="chk_session_status",
        ),
    )


class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_session_id = Column(GUID, ForeignKey("agent_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    engine = Column(String(20), nullable=False)
    query = Column(String(200), nullable=False)
    location = Column(String(120), nullable=True)
    purpose = Column(String(15), nullable=False)
    result_count = Column(Integer, default=0, nullable=False)
    cached = Column(Boolean, default=False, nullable=False)
    latency_ms = Column(Integer, nullable=True)
    error_code = Column(String(40), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)

    user = relationship("User")
    agent_session = relationship("AgentSession", back_populates="search_history")

    __table_args__ = (
        CheckConstraint(
            "engine IN ('google_jobs','google','google_news','youtube')",
            name="chk_search_engine",
        ),
        CheckConstraint(
            "purpose IN ('jobs','programs','market_signal','learning')",
            name="chk_search_purpose",
        ),
    )


class SerpCache(Base):
    __tablename__ = "serp_cache"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    cache_key = Column(String(64), unique=True, nullable=False, index=True)
    engine = Column(String(20), nullable=False, index=True)
    params = Column(JSON, nullable=False)
    raw_json = Column(JSON, nullable=False)
    result_count = Column(Integer, default=0, nullable=False)
    fetched_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
