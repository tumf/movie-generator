"""API endpoints for job management."""

import logging
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from models import JobCreate, JobResponse, JobStatus, JobStatusResponse
from pocketbase_client import PocketBaseClient

from config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


def get_client_ip(request: Request) -> str:
    """Get client IP address from request."""
    # Check for X-Forwarded-For header (behind proxy/Traefik)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.post("/jobs", response_model=JobResponse)
async def create_job(job_data: JobCreate, request: Request) -> JobResponse:
    """Create a new video generation job.

    Args:
        job_data: Job creation data
        request: FastAPI request object

    Returns:
        Created job information

    Raises:
        HTTPException: If queue is full or rate limit exceeded
    """
    pb_client: PocketBaseClient = request.app.state.pb_client
    client_ip = get_client_ip(request)

    # Check rate limit
    jobs_today = await pb_client.count_jobs_by_ip_today(client_ip)
    if jobs_today >= settings.rate_limit_per_day:
        raise HTTPException(
            status_code=429,
            detail=(
                f"1日の利用制限に達しました。明日またお試しください。"
                f"（上限: {settings.rate_limit_per_day}回）"
            ),
        )

    # Check queue size
    pending_count = await pb_client.count_pending_jobs()
    if pending_count >= settings.max_queue_size:
        raise HTTPException(
            status_code=503,
            detail=(
                f"現在キューが満杯です。しばらく待ってから再度お試しください。"
                f"（待機中: {pending_count}件）"
            ),
        )

    # Create job
    try:
        job = await pb_client.create_job(str(job_data.url), client_ip)
        logger.info(f"Created job {job['id']} for URL: {job_data.url}")
        return JobResponse(**job)
    except Exception as e:
        logger.error(f"Failed to create job: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="ジョブの作成に失敗しました")


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, request: Request) -> JobResponse:
    """Get job information by ID.

    Args:
        job_id: Job ID
        request: FastAPI request object

    Returns:
        Job information

    Raises:
        HTTPException: If job not found
    """
    pb_client: PocketBaseClient = request.app.state.pb_client

    try:
        job = await pb_client.get_job(job_id)
        return JobResponse(**job)
    except Exception as e:
        logger.error(f"Failed to get job {job_id}: {e}")
        raise HTTPException(status_code=404, detail="ジョブが見つかりません")


@router.get("/jobs/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: str, request: Request) -> JobStatusResponse:
    """Get job status for polling.

    Args:
        job_id: Job ID
        request: FastAPI request object

    Returns:
        Job status information

    Raises:
        HTTPException: If job not found
    """
    pb_client: PocketBaseClient = request.app.state.pb_client

    try:
        job = await pb_client.get_job(job_id)
        status = JobStatus(job["status"])

        return JobStatusResponse(
            status=status,
            progress=job["progress"],
            progress_message=job.get("progress_message"),
            current_step=job.get("current_step"),
            error_message=job.get("error_message"),
            completed=status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED],
            video_available=status == JobStatus.COMPLETED and job.get("video_path") is not None,
        )
    except Exception as e:
        logger.error(f"Failed to get job status {job_id}: {e}")
        raise HTTPException(status_code=404, detail="ジョブが見つかりません")


@router.get("/jobs/{job_id}/download")
async def download_video(job_id: str, request: Request) -> FileResponse:
    """Download the generated video.

    Args:
        job_id: Job ID
        request: FastAPI request object

    Returns:
        Video file

    Raises:
        HTTPException: If job not found or video not ready
    """
    pb_client: PocketBaseClient = request.app.state.pb_client

    try:
        job = await pb_client.get_job(job_id)

        if job["status"] != JobStatus.COMPLETED.value:
            raise HTTPException(status_code=400, detail="動画はまだ生成されていません")

        video_path_str = job.get("video_path")
        if not video_path_str:
            raise HTTPException(status_code=404, detail="動画ファイルが見つかりません")

        video_path = Path(video_path_str)
        if not video_path.exists():
            logger.error(f"Video file not found: {video_path}")
            raise HTTPException(status_code=404, detail="動画ファイルが見つかりません")

        return FileResponse(
            path=str(video_path),
            media_type="video/mp4",
            filename=f"movie_{job_id}.mp4",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download video for job {job_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="動画のダウンロードに失敗しました")


@router.get("/jobs/{job_id}/video")
async def stream_video(job_id: str, request: Request) -> StreamingResponse:
    """Stream the generated video with Range request support.

    Supports HTTP Range requests for video seeking and progressive loading.

    Args:
        job_id: Job ID
        request: FastAPI request object

    Returns:
        Video stream response

    Raises:
        HTTPException: If job not found or video not ready
    """
    pb_client: PocketBaseClient = request.app.state.pb_client

    try:
        job = await pb_client.get_job(job_id)

        if job["status"] != JobStatus.COMPLETED.value:
            raise HTTPException(status_code=400, detail="動画はまだ生成されていません")

        video_path_str = job.get("video_path")
        if not video_path_str:
            raise HTTPException(status_code=404, detail="動画ファイルが見つかりません")

        video_path = Path(video_path_str)
        if not video_path.exists():
            logger.error(f"Video file not found: {video_path}")
            raise HTTPException(status_code=404, detail="動画ファイルが見つかりません")

        # Get file size
        file_size = os.path.getsize(video_path)

        # Parse Range header
        range_header = request.headers.get("range")

        if range_header:
            # Parse range (format: "bytes=start-end")
            range_match = range_header.replace("bytes=", "").split("-")
            start = int(range_match[0]) if range_match[0] else 0
            end = int(range_match[1]) if len(range_match) > 1 and range_match[1] else file_size - 1

            # Validate range
            if start >= file_size or end >= file_size:
                raise HTTPException(status_code=416, detail="Requested range not satisfiable")

            # Read chunk
            chunk_size = end - start + 1

            def iterfile():
                with open(video_path, "rb") as f:
                    f.seek(start)
                    remaining = chunk_size
                    while remaining > 0:
                        read_size = min(8192, remaining)
                        data = f.read(read_size)
                        if not data:
                            break
                        remaining -= len(data)
                        yield data

            headers = {
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(chunk_size),
            }

            return StreamingResponse(
                iterfile(),
                status_code=206,
                headers=headers,
                media_type="video/mp4",
            )
        else:
            # Return entire file
            def iterfile():
                with open(video_path, "rb") as f:
                    while chunk := f.read(8192):
                        yield chunk

            headers = {
                "Accept-Ranges": "bytes",
                "Content-Length": str(file_size),
            }

            return StreamingResponse(
                iterfile(),
                status_code=200,
                headers=headers,
                media_type="video/mp4",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to stream video for job {job_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="動画のストリーミングに失敗しました")
