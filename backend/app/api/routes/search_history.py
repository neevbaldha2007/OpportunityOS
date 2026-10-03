from typing import List, Optional, Dict
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db import get_db
from app.models.user import User
from app.models.agent import AgentSession, SearchHistory, SerpCache
from app.config import settings
from app.schemas.history import (
    SearchHistoryResponse,
    SearchHistorySessionItem,
    QueryLogItem,
    CacheStatsResponse,
    CachePurgeResponse,
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/search", tags=["Search History & Cache"])


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@router.get("/history", response_model=SearchHistoryResponse)
def get_search_history(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=50, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by session status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve paginated search sessions and query histories for the authenticated user.
    """
    query = (
        db.query(AgentSession)
        .filter(AgentSession.user_id == current_user.id)
    )

    if status:
        query = query.filter(AgentSession.status == status)

    total = query.count()
    offset = (page - 1) * page_size
    sessions = query.order_by(AgentSession.created_at.desc()).offset(offset).limit(page_size).all()

    items: List[SearchHistorySessionItem] = []
    for s in sessions:
        role = s.career_goal.target_role if s.career_goal else (s.input_snapshot or {}).get("target_role")
        opp_count = (s.result_summary or {}).get("opportunity_count", 0)
        best_sc = (s.result_summary or {}).get("best_score", 0)

        query_logs = (
            db.query(SearchHistory)
            .filter(SearchHistory.agent_session_id == s.id)
            .order_by(SearchHistory.created_at.asc())
            .all()
        )
        q_items = [
            QueryLogItem(
                engine=q.engine,
                query=q.query,
                location=q.location,
                purpose=q.purpose,
                result_count=q.result_count,
                cached=q.cached,
                latency_ms=q.latency_ms,
                created_at=q.created_at,
            )
            for q in query_logs
        ]

        items.append(
            SearchHistorySessionItem(
                session_id=str(s.id),
                status=s.status,
                created_at=s.created_at,
                target_role=role,
                opportunity_count=opp_count,
                best_score=best_sc,
                queries=q_items,
            )
        )

    return SearchHistoryResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/history/{session_id}", response_model=SearchHistorySessionItem)
def get_session_search_history(
    session_id: str = Path(..., description="ID of the agent search session"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve query log and execution details for a specific search session.
    """
    session = (
        db.query(AgentSession)
        .filter(AgentSession.id == session_id, AgentSession.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search session not found or access denied",
        )

    role = session.career_goal.target_role if session.career_goal else (session.input_snapshot or {}).get("target_role")
    opp_count = (session.result_summary or {}).get("opportunity_count", 0)
    best_sc = (session.result_summary or {}).get("best_score", 0)

    query_logs = (
        db.query(SearchHistory)
        .filter(SearchHistory.agent_session_id == session.id)
        .order_by(SearchHistory.created_at.asc())
        .all()
    )
    q_items = [
        QueryLogItem(
            engine=q.engine,
            query=q.query,
            location=q.location,
            purpose=q.purpose,
            result_count=q.result_count,
            cached=q.cached,
            latency_ms=q.latency_ms,
            created_at=q.created_at,
        )
        for q in query_logs
    ]

    return SearchHistorySessionItem(
        session_id=str(session.id),
        status=session.status,
        created_at=session.created_at,
        target_role=role,
        opportunity_count=opp_count,
        best_score=best_sc,
        queries=q_items,
    )


@router.get("/cache/stats", response_model=CacheStatsResponse)
def get_cache_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve SerpCache performance statistics, entry counts, and daily API quota usage.
    """
    now = utcnow()
    total_entries = db.query(SerpCache).count()
    active_entries = db.query(SerpCache).filter(SerpCache.expires_at > now).count()
    expired_entries = total_entries - active_entries

    # Group count by engine
    engine_counts = (
        db.query(SerpCache.engine, func.count(SerpCache.id))
        .group_by(SerpCache.engine)
        .all()
    )
    engines_map: Dict[str, int] = {engine: count for engine, count in engine_counts}

    # Daily budget usage
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    daily_sessions = (
        db.query(AgentSession)
        .filter(AgentSession.created_at >= today_start)
        .all()
    )
    calls_used = sum(s.serp_calls_live for s in daily_sessions)

    return CacheStatsResponse(
        total_entries=total_entries,
        active_entries=active_entries,
        expired_entries=expired_entries,
        engines=engines_map,
        daily_budget=settings.SERP_DAILY_BUDGET,
        daily_calls_used=calls_used,
        cache_ttl_hours=getattr(settings, "SERP_CACHE_TTL_HOURS", 24),
    )


@router.delete("/cache/expired", response_model=CachePurgeResponse)
def purge_expired_cache(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Purge stale/expired search cache entries from the database.
    """
    now = utcnow()
    deleted_count = (
        db.query(SerpCache)
        .filter(SerpCache.expires_at <= now)
        .delete(synchronize_session=False)
    )
    db.commit()

    return CachePurgeResponse(
        purged_count=deleted_count,
        message=f"Successfully purged {deleted_count} expired cache records.",
    )
