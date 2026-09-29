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
from app.db import Base, GUID


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(120), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    skills = relationship("UserSkill", back_populates="user", cascade="all, delete-orphan")
    career_goals = relationship("CareerGoal", back_populates="user", cascade="all, delete-orphan")
    saved_opportunities = relationship("SavedOpportunity", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    agent_sessions = relationship("AgentSession", back_populates="user", cascade="all, delete-orphan")
    matches = relationship("OpportunityMatch", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    education_level = Column(
        String(30),
        nullable=False,
    )
    degree = Column(String(120), nullable=True)
    field_of_study = Column(String(120), nullable=True)
    graduation_year = Column(SmallInteger, nullable=True)
    institution = Column(String(200), nullable=True)
    experience_level = Column(String(20), default="student", nullable=False)
    location_city = Column(String(100), nullable=True)
    location_state = Column(String(100), nullable=True)
    location_country = Column(String(2), default="IN", nullable=False)
    open_to_remote = Column(Boolean, default=True, nullable=False)
    weekly_learning_hours = Column(SmallInteger, default=10, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    user = relationship("User", back_populates="profile")

    __table_args__ = (
        CheckConstraint(
            "education_level IN ('high_school','diploma','bachelors','masters','phd','other')",
            name="chk_education_level",
        ),
        CheckConstraint(
            "graduation_year IS NULL OR (graduation_year BETWEEN 1990 AND 2040)",
            name="chk_graduation_year",
        ),
        CheckConstraint(
            "experience_level IN ('student','fresher','0_1_years','1_2_years')",
            name="chk_experience_level",
        ),
        CheckConstraint(
            "weekly_learning_hours BETWEEN 1 AND 60",
            name="chk_weekly_learning_hours",
        ),
    )
