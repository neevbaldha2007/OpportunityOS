"""
Search and normalization package for OpportunityOS.

Provides resilient SerpApi client with 24h caching, multi-engine normalizers,
and deduplication algorithms.
"""

from app.search.serpapi_client import SerpApiClient, compute_cache_key
from app.search.normalizer import (
    normalize_google_job,
    normalize_google_organic,
    normalize_google_news,
    normalize_youtube,
    normalize_search_results,
    infer_opportunity_type,
    is_job_remote,
)
from app.search.dedupe import (
    dedupe_hash,
    normalize_text,
    content_hash,
    is_duplicate,
    deduplicate_records,
)

__all__ = [
    "SerpApiClient",
    "compute_cache_key",
    "normalize_google_job",
    "normalize_google_organic",
    "normalize_google_news",
    "normalize_youtube",
    "normalize_search_results",
    "infer_opportunity_type",
    "is_job_remote",
    "dedupe_hash",
    "normalize_text",
    "content_hash",
    "is_duplicate",
    "deduplicate_records",
]
