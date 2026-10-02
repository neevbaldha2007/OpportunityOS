from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SkillAutocompleteItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    category: Optional[str] = None
    is_verified: bool = True


class SkillAutocompleteResponse(BaseModel):
    items: List[SkillAutocompleteItem]


class SkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    category: Optional[str] = None
    aliases: List[str] = Field(default_factory=list)
    is_verified: bool = True
    created_at: Optional[datetime] = None


class SkillCategoryItem(BaseModel):
    category: str
    count: int


class SkillCategoriesResponse(BaseModel):
    categories: List[SkillCategoryItem]
    total_skills: int


class SkillLookupResponse(BaseModel):
    found: bool
    matched_by: Optional[str] = None
    query: str
    skill: Optional[SkillResponse] = None


class SkillListResponse(BaseModel):
    items: List[SkillResponse]
    total: int
    limit: int
    offset: int
