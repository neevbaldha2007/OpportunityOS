import re
from typing import Dict, Any, List, Optional
from app.search.dedupe import dedupe_hash


def infer_opportunity_type(title: str, schedule_type: Optional[str] = None) -> str:
    """
    Infers standard opportunity category from title and schedule metadata.
    Returns: 'internship' | 'full_time' | 'part_time' | 'contract' | 'program' | 'fellowship' | 'career_page'
    """
    combined = f"{title or ''} {schedule_type or ''}".lower()
    if "intern" in combined or "trainee" in combined or "apprentice" in combined:
        return "internship"
    if "part-time" in combined or "part time" in combined:
        return "part_time"
    if "contract" in combined or "freelance" in combined or "temporary" in combined:
        return "contract"
    if "fellowship" in combined:
        return "fellowship"
    if "program" in combined or "bootcamp" in combined:
        return "program"
    if "career" in combined or "hiring" in combined:
        return "career_page"
    if "full-time" in combined or "full time" in combined:
        return "full_time"
    return "internship" if "intern" in (title or "").lower() else "full_time"


def is_job_remote(title: str, location: str, detected_ext: Optional[Dict[str, Any]] = None) -> bool:
    """
    Determines whether a role offers remote / work-from-home options.
    """
    if detected_ext and (detected_ext.get("work_from_home") or detected_ext.get("remote")):
        return True
    combined = f"{title or ''} {location or ''}".lower()
    patterns = [r"\bremote\b", r"\bwork from home\b", r"\bwfh\b", r"\banywhere\b", r"\btelecommute\b"]
    return any(re.search(p, combined) for p in patterns)


def normalize_google_job(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Normalizes a single Google Jobs result item into canonical opportunity dictionary.
    """
    title = (item.get("title") or "").strip()
    if not title:
        return None

    company = (item.get("company_name") or "").strip()
    location = (item.get("location") or "").strip()
    detected_ext = item.get("detected_extensions") or {}

    remote = is_job_remote(title, location, detected_ext)
    schedule_type = detected_ext.get("schedule_type")
    posted_at_text = detected_ext.get("posted_at")
    salary_text = detected_ext.get("salary") or item.get("salary")
    source_via = item.get("via") or ""
    description = (item.get("description") or "")[:8000]
    highlights = item.get("job_highlights") or []

    # URL extraction hierarchy: apply_options[0].link -> share_link -> related_links
    apply_url = None
    apply_options = item.get("apply_options")
    if apply_options and isinstance(apply_options, list) and len(apply_options) > 0:
        apply_url = apply_options[0].get("link")
    if not apply_url:
        apply_url = item.get("share_link")
    if not apply_url and item.get("related_links"):
        apply_url = item["related_links"][0].get("link")

    opp_type = infer_opportunity_type(title, schedule_type)
    hash_val = dedupe_hash(title, company, location)

    return {
        "dedupe_hash": hash_val,
        "source_engine": "google_jobs",
        "external_id": item.get("job_id"),
        "title": title,
        "company_name": company or None,
        "location": location or None,
        "is_remote": remote,
        "opportunity_type": opp_type,
        "schedule_type": schedule_type,
        "description": description,
        "highlights": highlights,
        "salary_text": salary_text,
        "source_via": source_via or None,
        "apply_url": apply_url,
        "posted_at_text": posted_at_text,
        "raw": item,
    }


def normalize_google_organic(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Normalizes a Google Search organic result (programs, fellowships, career portals).
    """
    title = (item.get("title") or "").strip()
    link = item.get("link")
    if not title or not link:
        return None

    snippet = (item.get("snippet") or "")[:8000]
    source_via = item.get("source") or item.get("displayed_link") or ""

    # Infer company from separators: ' - ', ' | ', ' • ', ' · '
    company = None
    for sep in [" - ", " | ", " • ", " · "]:
        if sep in title:
            parts = title.split(sep)
            company = parts[-1].strip()
            break

    opp_type = infer_opportunity_type(title)
    if opp_type == "full_time" and ("program" in title.lower() or "fellowship" in title.lower()):
        opp_type = "program"
    elif opp_type == "full_time":
        opp_type = "career_page"

    hash_val = dedupe_hash(title, company or "", "")

    return {
        "dedupe_hash": hash_val,
        "source_engine": "google",
        "external_id": link,
        "title": title,
        "company_name": company,
        "location": "India",
        "is_remote": "remote" in (title + " " + snippet).lower(),
        "opportunity_type": opp_type,
        "schedule_type": None,
        "description": snippet,
        "highlights": [],
        "salary_text": None,
        "source_via": source_via or None,
        "apply_url": link,
        "posted_at_text": None,
        "raw": item,
    }


def normalize_google_news(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes a Google News article item for industry hiring trends.
    """
    source = item.get("source")
    source_name = source.get("name") if isinstance(source, dict) else str(source or "News")
    return {
        "title": item.get("title", ""),
        "link": item.get("link", ""),
        "source": source_name,
        "date": item.get("date", ""),
        "snippet": item.get("snippet", ""),
        "thumbnail": item.get("thumbnail"),
    }


def normalize_youtube(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes a YouTube video search result for skill learning roadmaps.
    """
    return {
        "title": item.get("title", ""),
        "link": item.get("link", ""),
        "channel": item.get("channel", {}).get("name") if isinstance(item.get("channel"), dict) else str(item.get("channel", "")),
        "duration": item.get("duration", ""),
        "thumbnail": item.get("thumbnail"),
    }


def normalize_search_results(engine: str, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Unified entrypoint to normalize search results from any supported SerpApi engine.
    """
    results: List[Dict[str, Any]] = []

    if engine == "google_jobs":
        jobs = raw_data.get("jobs_results", [])
        for job in jobs:
            norm = normalize_google_job(job)
            if norm:
                results.append(norm)

    elif engine == "google":
        organics = raw_data.get("organic_results", [])
        for org in organics:
            norm = normalize_google_organic(org)
            if norm:
                results.append(norm)

    elif engine == "google_news":
        news = raw_data.get("news_results", [])
        for n in news:
            norm = normalize_google_news(n)
            if norm:
                results.append(norm)

    elif engine == "youtube":
        videos = raw_data.get("video_results", [])
        for v in videos:
            norm = normalize_youtube(v)
            if norm:
                results.append(norm)

    return results
