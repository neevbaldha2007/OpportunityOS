import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    SmallInteger,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from app.db import Base, GUID, JSONList


def utcnow():
    return datetime.now(timezone.utc)


class Skill(Base):
    __tablename__ = "skills"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(80), unique=True, nullable=False, index=True)
    slug = Column(String(80), unique=True, nullable=False, index=True)
    category = Column(String(40), nullable=True, index=True)
    aliases = Column(JSONList, default=list, nullable=False)
    is_verified = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    user_skills = relationship("UserSkill", back_populates="skill")
    opportunity_skills = relationship("OpportunitySkill", back_populates="skill")
    skill_gaps = relationship("SkillGap", back_populates="skill")


class UserSkill(Base):
    __tablename__ = "user_skills"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(GUID, ForeignKey("skills.id", ondelete="RESTRICT"), nullable=False, index=True)
    proficiency = Column(SmallInteger, default=2, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    user = relationship("User", back_populates="skills")
    skill = relationship("Skill", back_populates="user_skills")

    __table_args__ = (
        UniqueConstraint("user_id", "skill_id", name="uq_user_skills"),
        CheckConstraint("proficiency BETWEEN 1 AND 5", name="chk_user_skill_proficiency"),
    )


class OpportunitySkill(Base):
    __tablename__ = "opportunity_skills"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    opportunity_id = Column(GUID, ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(GUID, ForeignKey("skills.id", ondelete="RESTRICT"), nullable=False, index=True)
    requirement = Column(String(10), default="required", nullable=False)
    extraction_method = Column(String(12), default="dictionary", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    opportunity = relationship("Opportunity", back_populates="skills")
    skill = relationship("Skill", back_populates="opportunity_skills")

    __table_args__ = (
        UniqueConstraint("opportunity_id", "skill_id", name="uq_opportunity_skills"),
        CheckConstraint("requirement IN ('required','preferred')", name="chk_opp_skill_requirement"),
        CheckConstraint("extraction_method IN ('dictionary','llm')", name="chk_opp_skill_extraction_method"),
    )
