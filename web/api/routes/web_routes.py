"""Web routes for HTML pages."""

import logging

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import HttpUrl, ValidationError

from ..models import JobCreate
from ..pocketbase_client import PocketBaseClient

logger = logging.getLogger(__name__)

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
        return templates.TemplateResponse(
            "job.html",
            {
                "request": request,
                "job": job,
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
        return templates.TemplateResponse(
            "partials/job_status.html",
            {
                "request": request,
                "job": job,
            },
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
