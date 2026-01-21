"""Web routes for HTML pages."""

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from models import JobCreate
from pocketbase_client import PocketBaseClient
from pydantic import HttpUrl, ValidationError

logger = logging.getLogger(__name__)


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
        started = parse_datetime(job.get("started_at"))
        if started:
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


router = APIRouter()


def get_client_ip(request: Request) -> str:
    """Get client IP address from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """Render the top page with URL input form."""
    templates = request.app.state.templates
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/jobs/create")
async def create_job_form(
    request: Request,
    url: str = Form(...),
) -> RedirectResponse:
    """Handle job creation from HTML form.

    Args:
        request: FastAPI request
        url: URL from form

    Returns:
        Redirect to job detail page

    Raises:
        HTTPException: If validation fails or job creation fails
    """
    from .api_routes import create_job as api_create_job

    # Validate URL
    try:
        job_data = JobCreate(url=HttpUrl(url))
    except ValidationError:
        templates = request.app.state.templates
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": "有効なURLを入力してください",
                "url": url,
            },
            status_code=400,
        )

    # Create job via API
    try:
        job = await api_create_job(job_data, request)
        return RedirectResponse(url=f"/jobs/{job.id}", status_code=303)
    except HTTPException as e:
        templates = request.app.state.templates
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": e.detail,
                "url": url,
            },
            status_code=e.status_code,
        )


@router.get("/jobs/{job_id}", response_class=HTMLResponse)
async def job_detail(request: Request, job_id: str) -> HTMLResponse:
    """Render job detail page with progress and download.

    Args:
        request: FastAPI request
        job_id: Job ID

    Returns:
        Job detail HTML page

    Raises:
        HTTPException: If job not found
    """
    pb_client: PocketBaseClient = request.app.state.pb_client
    templates = request.app.state.templates

    try:
        job = await pb_client.get_job(job_id)
        elapsed_time = calculate_elapsed_time(job)

        # Get queue position for pending jobs
        queue_position = None
        queue_total = None
        if job.get("status") == "pending" and job.get("created"):
            queue_position, queue_total = await pb_client.get_queue_position(job_id, job["created"])

        return templates.TemplateResponse(
            "job.html",
            {
                "request": request,
                "job": job,
                "elapsed_time": elapsed_time,
                "queue_position": queue_position,
                "queue_total": queue_total,
            },
        )
    except Exception as e:
        logger.error(f"Failed to get job {job_id}: {e}")
        raise HTTPException(status_code=404, detail="ジョブが見つかりません")


@router.get("/jobs/{job_id}/status-html", response_class=HTMLResponse)
async def job_status_html(request: Request, job_id: str) -> HTMLResponse:
    """Render job status fragment for htmx polling.

    Args:
        request: FastAPI request
        job_id: Job ID

    Returns:
        Job status HTML fragment

    Raises:
        HTTPException: If job not found
    """

    pb_client: PocketBaseClient = request.app.state.pb_client
    templates = request.app.state.templates

    try:
        job = await pb_client.get_job(job_id)
        elapsed_time = calculate_elapsed_time(job)

        # Get queue position for pending jobs
        queue_position = None
        queue_total = None
        if job.get("status") == "pending" and job.get("created"):
            queue_position, queue_total = await pb_client.get_queue_position(job_id, job["created"])

        # Stop polling when job is completed
        headers = {}
        if job.get("status") in ["completed", "failed", "cancelled"]:
            headers["HX-Stop-Polling"] = "true"

        return templates.TemplateResponse(
            "partials/job_status.html",
            {
                "request": request,
                "job": job,
                "elapsed_time": elapsed_time,
                "queue_position": queue_position,
                "queue_total": queue_total,
            },
            headers=headers,
        )
    except Exception as e:
        logger.error(f"Failed to get job status {job_id}: {e}")
        return templates.TemplateResponse(
            "partials/job_status.html",
            {
                "request": request,
                "error": "ジョブ情報の取得に失敗しました",
            },
            status_code=500,
        )
