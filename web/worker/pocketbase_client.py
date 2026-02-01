"""PocketBase client for job management."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class PocketBaseClient:
    """Client for interacting with PocketBase."""

    def __init__(self, base_url: str) -> None:
        """Initialize PocketBase client."""
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def get_pending_jobs(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get pending jobs."""
        response = await self.client.get(
            "/api/collections/jobs/records",
            params={
                "filter": "status = 'pending'",
                "sort": "created",
                "perPage": limit,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data.get("items", [])

    async def update_job(self, job_id: str, update_data: dict[str, Any]) -> dict[str, Any]:
        """Update a job."""
        response = await self.client.patch(
            f"/api/collections/jobs/records/{job_id}",
            json=update_data,
        )
        response.raise_for_status()
        return response.json()

    async def delete_expired_jobs(self) -> int:
        """Delete jobs that have passed their expiration time."""
        now = datetime.now(UTC)

        response = await self.client.get(
            "/api/collections/jobs/records",
            params={
                "filter": f"expires_at < '{now.isoformat()}Z'",
                "perPage": 100,
            },
        )
        response.raise_for_status()
        data = response.json()
        jobs = data.get("items", [])

        deleted_count = 0
        for job in jobs:
            try:
                await self.client.delete(f"/api/collections/jobs/records/{job['id']}")
                deleted_count += 1
                logger.info(f"Deleted expired job {job['id']}")
            except httpx.HTTPError:
                continue

        return deleted_count
