"""Pydantic models for API."""

from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, HttpUrl


class JobStatus(str, Enum):
    """Job status enum."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobCreate(BaseModel):
    """Request model for creating a job."""

    url: Annotated[HttpUrl, Field(description="URL of the blog post to convert")]


class JobResponse(BaseModel):
    """Response model for job information."""

    id: str
    url: str
    status: JobStatus
    progress: Annotated[int, Field(ge=0, le=100)]
    progress_message: str | None = None
    current_step: str | None = None
    video_path: str | None = None
    video_size: int | None = None
    error_message: str | None = None
    created: datetime
    updated: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    expires_at: datetime


class JobStatusResponse(BaseModel):
    """Response model for job status polling."""

    status: JobStatus
    progress: Annotated[int, Field(ge=0, le=100)]
    progress_message: str | None = None
    current_step: str | None = None
    error_message: str | None = None
    completed: bool
    video_available: bool


class ErrorResponse(BaseModel):
    """Response model for errors."""

    detail: str
