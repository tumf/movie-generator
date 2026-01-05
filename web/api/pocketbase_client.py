"""PocketBase client utilities."""

from datetime import datetime, timedelta
from typing import Any

import httpx

from config import settings
from models import JobStatus


class PocketBaseClient:
    """Client for interacting with PocketBase."""

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize PocketBase client."""
        self.base_url = base_url or settings.pocketbase_url
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def create_job(self, url: str, client_ip: str) -> dict[str, Any]:
        """Create a new job in PocketBase.

        Args:
            url: URL to process
            client_ip: Client IP address for rate limiting

        Returns:
            Created job record
        """
        expires_at = datetime.utcnow() + timedelta(hours=settings.job_expiration_hours)

        job_data = {
            "url": url,
            "status": JobStatus.PENDING.value,
            "progress": 0,
            "client_ip": client_ip,
            "expires_at": expires_at.isoformat() + "Z",
        }

        response = await self.client.post(
            "/api/collections/jobs/records",
            json=job_data,
        )
        response.raise_for_status()
        return response.json()

    async def get_job(self, job_id: str) -> dict[str, Any]:
        """Get a job by ID.

        Args:
            job_id: Job ID

        Returns:
            Job record
        """
        response = await self.client.get(f"/api/collections/jobs/records/{job_id}")
        response.raise_for_status()
        return response.json()

    async def update_job(self, job_id: str, update_data: dict[str, Any]) -> dict[str, Any]:
        """Update a job.

        Args:
            job_id: Job ID
            update_data: Fields to update

        Returns:
            Updated job record
        """
        response = await self.client.patch(
            f"/api/collections/jobs/records/{job_id}",
            json=update_data,
        )
        response.raise_for_status()
        return response.json()

    async def count_pending_jobs(self) -> int:
        """Count jobs in pending status.

        Returns:
            Number of pending jobs
        """
        response = await self.client.get(
            "/api/collections/jobs/records",
            params={
                "filter": f"status = '{JobStatus.PENDING.value}'",
                "perPage": 1,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data.get("totalItems", 0)

    async def count_jobs_by_ip_today(self, client_ip: str) -> int:
        """Count jobs created by IP address today.

        Args:
            client_ip: Client IP address

        Returns:
            Number of jobs created today by this IP
        """
        # Get start of today (UTC 00:00:00)
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_start_iso = today_start.isoformat() + "Z"

        # PocketBase filter: client_ip matches AND created >= today start
        filter_query = f"client_ip = '{client_ip}' && created >= '{today_start_iso}'"

        response = await self.client.get(
            "/api/collections/jobs/records",
            params={
                "filter": filter_query,
                "perPage": 1,  # We only need totalItems count
            },
        )
        response.raise_for_status()
        data = response.json()
        return data.get("totalItems", 0)

    async def get_pending_jobs(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get pending jobs for worker processing.

        Args:
            limit: Maximum number of jobs to return

        Returns:
            List of pending job records
        """
        response = await self.client.get(
            "/api/collections/jobs/records",
            params={
                "filter": f"status = '{JobStatus.PENDING.value}'",
                "sort": "created",
                "perPage": limit,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data.get("items", [])

    async def delete_expired_jobs(self) -> int:
        """Delete jobs that have passed their expiration time.

        Returns:
            Number of jobs deleted
        """
        now = datetime.utcnow()

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
            except httpx.HTTPError:
                continue

        return deleted_count
