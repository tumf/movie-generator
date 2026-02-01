"""Job time utilities for parsing and calculating elapsed time."""

from datetime import UTC, datetime, timedelta
from typing import Any


def parse_datetime(value: str | datetime | None) -> datetime | None:
    """Parse a datetime value from PocketBase.

    PocketBase returns datetime fields as ISO strings like "2026-01-21 16:43:53.380Z".

    Args:
        value: Datetime string, datetime object, or None

    Returns:
        Parsed datetime object with UTC timezone, or None
    """
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value
    try:
        # PocketBase format: "2026-01-21 16:43:53.380Z"
        # Replace space with T for ISO format
        iso_str = value.replace(" ", "T")
        if iso_str.endswith("Z"):
            iso_str = iso_str[:-1] + "+00:00"
        dt = datetime.fromisoformat(iso_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt
    except (ValueError, AttributeError):
        return None


def calculate_elapsed_time(job: dict[str, Any]) -> str | None:
    """Calculate and format elapsed time for a job.

    Args:
        job: Job dictionary from PocketBase

    Returns:
        Formatted elapsed time string (e.g., "2分30秒"), or None if not applicable
    """
    now = datetime.now(UTC)
    delta: timedelta | None = None

    if job.get("status") == "completed":
        started = parse_datetime(job.get("started_at"))
        completed = parse_datetime(job.get("completed_at"))
        if started and completed:
            delta = completed - started
        elif completed:
            created = parse_datetime(job.get("created"))
            if created:
                delta = completed - created
        else:
            return None
    elif job.get("status") == "failed":
        # Use completed_at (set when job failed) to stop the timer
        started = parse_datetime(job.get("started_at"))
        completed = parse_datetime(job.get("completed_at"))
        if started and completed:
            delta = completed - started
        elif started:
            # Fallback if completed_at not set
            delta = now - started
        else:
            return None
    elif job.get("status") == "processing":
        started = parse_datetime(job.get("started_at"))
        if started:
            delta = now - started
        else:
            created = parse_datetime(job.get("created"))
            if created:
                delta = now - created
    elif job.get("status") == "pending":
        created = parse_datetime(job.get("created"))
        if created:
            delta = now - created
        else:
            return None
    else:
        return None

    if delta is None:
        return None

    total_seconds = int(delta.total_seconds())
    if total_seconds < 60:
        return f"{total_seconds}秒"
    elif total_seconds < 3600:
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}分{seconds}秒" if seconds else f"{minutes}分"
    else:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}時間{minutes}分" if minutes else f"{hours}時間"
