from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class QueryLogItem(BaseModel):
    engine: str
    query: str
    location: Optional[str] = None
    purpose: Optional[str] = "jobs"
    result_count: int = 0
    cached: bool = False
    latency_ms: Optional[int] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SearchHistorySessionItem(BaseModel):
    session_id: str
    status: str
    created_at: datetime
    target_role: Optional[str] = None
    opportunity_count: int = 0
    best_score: int = 0
    queries: List[QueryLogItem] = []

    model_config = ConfigDict(from_attributes=True)


class SearchHistoryResponse(BaseModel):
    items: List[SearchHistorySessionItem]
    page: int = 1
    page_size: int = 20
    total: int = 0


class CacheStatsResponse(BaseModel):
    total_entries: int = 0
    active_entries: int = 0
    expired_entries: int = 0
    engines: Dict[str, int] = {}
    daily_budget: int = 80
    daily_calls_used: int = 0
    cache_ttl_hours: int = 24


class CachePurgeResponse(BaseModel):
    purged_count: int
    message: str
