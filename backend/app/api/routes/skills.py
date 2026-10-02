import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, Header
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, String

from app.db import get_db
from app.models.skill import Skill
from app.models.user import User
from app.schemas.skill import (
    SkillAutocompleteResponse,
    SkillAutocompleteItem,
    SkillResponse,
    SkillCategoriesResponse,
    SkillCategoryItem,
    SkillLookupResponse,
)
from app.api.deps import security
from app.core.security import decode_access_token
from app.core.errors import AppError

router = APIRouter(tags=["Skills"])


def get_optional_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Optional user dependency: allows both authenticated and unauthenticated queries."""
    token = None
    if auth and auth.credentials:
        token = auth.credentials
    elif authorization:
        parts = authorization.strip().split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
        elif len(parts) == 1:
            token = parts[0]

    if not token:
        return None

    try:
        payload = decode_access_token(token)
        user_id_str = payload.get("sub")
        if not user_id_str:
            return None
        user_uuid = uuid.UUID(user_id_str)
        return db.query(User).filter(User.id == user_uuid).first()
    except Exception:
        return None


@router.get("/skills", response_model=SkillAutocompleteResponse)
def get_skills_autocomplete(
    q: Optional[str] = Query(None, description="Search query for skill name, slug, or alias"),
    category: Optional[str] = Query(None, description="Filter skills by category"),
    limit: int = Query(20, ge=1, le=500, description="Maximum number of skills to return"),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """Autocomplete and filter canonical skills by name, slug, alias, and category.

    Results are intelligently ranked: exact matches first, then prefix matches,
    then alias/substring matches.
    """
    query = db.query(Skill)

    if category:
        query = query.filter(Skill.category == category)

    if not q or not q.strip():
        results = query.order_by(Skill.name).limit(limit).all()
        items = [
            SkillAutocompleteItem(
                id=str(s.id),
                name=s.name,
                category=s.category,
                is_verified=s.is_verified,
            )
            for s in results
        ]
        return SkillAutocompleteResponse(items=items)

    clean_q = q.strip().lower()
    search_pattern = f"%{clean_q}%"

    # Search in name, slug, or JSON-stringified aliases
    candidates = (
        query.filter(
            or_(
                Skill.name.ilike(search_pattern),
                Skill.slug.ilike(search_pattern),
                Skill.aliases.cast(String).ilike(search_pattern),
            )
        )
        .order_by(Skill.name)
        .limit(max(limit * 3, 60))
        .all()
    )

    def ranking_key(skill: Skill) -> tuple:
        s_name = (skill.name or "").lower()
        s_slug = (skill.slug or "").lower()
        s_aliases = [a.lower() for a in (skill.aliases or [])]

        if s_name == clean_q:
            priority = 0
        elif s_slug == clean_q:
            priority = 1
        elif clean_q in s_aliases:
            priority = 2
        elif s_name.startswith(clean_q):
            priority = 3
        elif any(a.startswith(clean_q) for a in s_aliases):
            priority = 4
        elif clean_q in s_name:
            priority = 5
        else:
            priority = 6

        return (priority, s_name)

    ranked = sorted(candidates, key=ranking_key)[:limit]

    items = [
        SkillAutocompleteItem(
            id=str(s.id),
            name=s.name,
            category=s.category,
            is_verified=s.is_verified,
        )
        for s in ranked
    ]
    return SkillAutocompleteResponse(items=items)


@router.get("/skills/categories", response_model=SkillCategoriesResponse)
def get_skill_categories(
    db: Session = Depends(get_db),
):
    """Retrieve distinct skill categories with skill counts across the canonical catalog."""
    rows = (
        db.query(Skill.category, func.count(Skill.id).label("count"))
        .filter(Skill.category.isnot(None))
        .group_by(Skill.category)
        .order_by(func.count(Skill.id).desc())
        .all()
    )

    total = db.query(Skill).count()
    categories = [
        SkillCategoryItem(category=cat or "uncategorized", count=cnt)
        for cat, cnt in rows
    ]
    return SkillCategoriesResponse(categories=categories, total_skills=total)


@router.get("/skills/lookup", response_model=SkillLookupResponse)
def lookup_skill_by_term(
    term: str = Query(..., min_length=1, description="Skill name, slug, or alias to look up"),
    db: Session = Depends(get_db),
):
    """Deterministic lookup for a canonical skill by its exact name, slug, or alias.

    Enables reverse resolution of aliases (e.g., 'reactjs' -> React, 'k8s' -> Kubernetes).
    """
    clean_term = term.strip().lower()

    # 1. Exact name match (case-insensitive)
    skill = db.query(Skill).filter(func.lower(Skill.name) == clean_term).first()
    if skill:
        return SkillLookupResponse(
            found=True,
            matched_by="exact_name",
            query=term,
            skill=SkillResponse(
                id=str(skill.id),
                name=skill.name,
                slug=skill.slug,
                category=skill.category,
                aliases=skill.aliases or [],
                is_verified=skill.is_verified,
                created_at=skill.created_at,
            ),
        )

    # 2. Exact slug match
    skill = db.query(Skill).filter(Skill.slug == clean_term).first()
    if skill:
        return SkillLookupResponse(
            found=True,
            matched_by="slug",
            query=term,
            skill=SkillResponse(
                id=str(skill.id),
                name=skill.name,
                slug=skill.slug,
                category=skill.category,
                aliases=skill.aliases or [],
                is_verified=skill.is_verified,
                created_at=skill.created_at,
            ),
        )

    # 3. Alias match across catalog
    all_skills = db.query(Skill).all()
    for s in all_skills:
        aliases = [a.strip().lower() for a in (s.aliases or [])]
        if clean_term in aliases:
            return SkillLookupResponse(
                found=True,
                matched_by="alias",
                query=term,
                skill=SkillResponse(
                    id=str(s.id),
                    name=s.name,
                    slug=s.slug,
                    category=s.category,
                    aliases=s.aliases or [],
                    is_verified=s.is_verified,
                    created_at=s.created_at,
                ),
            )

    return SkillLookupResponse(
        found=False,
        matched_by=None,
        query=term,
        skill=None,
    )


@router.get("/skills/slug/{slug}", response_model=SkillResponse)
def get_skill_by_slug(
    slug: str,
    db: Session = Depends(get_db),
):
    """Retrieve full details for a canonical skill by slug."""
    skill = db.query(Skill).filter(Skill.slug == slug.strip().lower()).first()
    if not skill:
        raise AppError("NOT_FOUND", f"Skill with slug '{slug}' not found", 404)

    return SkillResponse(
        id=str(skill.id),
        name=skill.name,
        slug=skill.slug,
        category=skill.category,
        aliases=skill.aliases or [],
        is_verified=skill.is_verified,
        created_at=skill.created_at,
    )


@router.get("/skills/{skill_id}", response_model=SkillResponse)
def get_skill_by_id(
    skill_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve full details for a canonical skill by its UUID."""
    try:
        uuid_obj = uuid.UUID(skill_id)
    except ValueError:
        raise AppError("BAD_REQUEST", f"Invalid UUID format for skill_id: '{skill_id}'", 400)

    skill = db.query(Skill).filter(Skill.id == uuid_obj).first()
    if not skill:
        raise AppError("NOT_FOUND", f"Skill with id '{skill_id}' not found", 404)

    return SkillResponse(
        id=str(skill.id),
        name=skill.name,
        slug=skill.slug,
        category=skill.category,
        aliases=skill.aliases or [],
        is_verified=skill.is_verified,
        created_at=skill.created_at,
    )
