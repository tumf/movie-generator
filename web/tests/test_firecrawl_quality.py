"""Tests for Firecrawl content quality checking."""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

# Add API directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

from firecrawl_client import FirecrawlClient, FirecrawlError, check_content_quality
from main import app


@pytest.fixture
def mock_pb_client():
    """Mock PocketBase client."""
    client = AsyncMock()
    client.count_jobs_by_ip_today.return_value = 0
    client.count_pending_jobs.return_value = 0
    client.create_job.return_value = {
        "id": "test_job_123",
        "url": "https://example.com",
        "status": "pending",
        "progress": 0,
        "client_ip": "127.0.0.1",
        "created": "2026-01-23T12:00:00Z",
        "updated": "2026-01-23T12:00:00Z",
        "expires_at": "2026-01-24T12:00:00Z",
    }
    return client


class TestFirecrawlClient:
    """Tests for FirecrawlClient."""

    @pytest.mark.asyncio
    async def test_init_without_api_key(self):
        """Test initialization without API key raises error."""
        with patch("firecrawl_client.settings") as mock_settings:
            mock_settings.firecrawl_api_key = None
            with pytest.raises(FirecrawlError, match="API key is not configured"):
                FirecrawlClient()

    @pytest.mark.asyncio
    async def test_get_summary_success(self):
        """Test successful summary retrieval."""
        with patch("firecrawl_client.settings") as mock_settings:
            mock_settings.firecrawl_api_key = "test_key"

            with patch("httpx.AsyncClient") as mock_client_class:
                mock_response = AsyncMock()
                mock_response.status_code = 200
                # json() should be a regular function, not async
                mock_response.json = lambda: {
                    "data": {
                        "extract": {
                            "summary": "  Test summary content with enough length to pass  "
                        }
                    }
                }

                mock_client = AsyncMock()
                mock_client.post.return_value = mock_response
                mock_client.__aenter__.return_value = mock_client
                mock_client.__aexit__.return_value = None
                mock_client_class.return_value = mock_client

                client = FirecrawlClient()
                summary = await client.get_summary("https://example.com")

                assert summary == "Test summary content with enough length to pass"
                mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_summary_auth_error(self):
        """Test summary retrieval with authentication error."""
        with patch("firecrawl_client.settings") as mock_settings:
            mock_settings.firecrawl_api_key = "invalid_key"

            with patch("httpx.AsyncClient") as mock_client_class:
                mock_response = AsyncMock()
                mock_response.status_code = 401

                mock_client = AsyncMock()
                mock_client.post.return_value = mock_response
                mock_client.__aenter__.return_value = mock_client
                mock_client.__aexit__.return_value = None
                mock_client_class.return_value = mock_client

                client = FirecrawlClient()
                with pytest.raises(FirecrawlError, match="authentication failed"):
                    await client.get_summary("https://example.com")

    @pytest.mark.asyncio
    async def test_get_summary_rate_limit(self):
        """Test summary retrieval with rate limit error."""
        with patch("firecrawl_client.settings") as mock_settings:
            mock_settings.firecrawl_api_key = "test_key"

            with patch("httpx.AsyncClient") as mock_client_class:
                mock_response = AsyncMock()
                mock_response.status_code = 429

                mock_client = AsyncMock()
                mock_client.post.return_value = mock_response
                mock_client.__aenter__.return_value = mock_client
                mock_client.__aexit__.return_value = None
                mock_client_class.return_value = mock_client

                client = FirecrawlClient()
                with pytest.raises(FirecrawlError, match="rate limit exceeded"):
                    await client.get_summary("https://example.com")

    @pytest.mark.asyncio
    async def test_get_summary_timeout(self):
        """Test summary retrieval with timeout."""
        import httpx

        with patch("firecrawl_client.settings") as mock_settings:
            mock_settings.firecrawl_api_key = "test_key"

            with patch("httpx.AsyncClient") as mock_client_class:
                mock_client = AsyncMock()
                mock_client.post.side_effect = httpx.TimeoutException("Timeout")
                mock_client.__aenter__.return_value = mock_client
                mock_client.__aexit__.return_value = None
                mock_client_class.return_value = mock_client

                client = FirecrawlClient()
                with pytest.raises(FirecrawlError, match="timed out"):
                    await client.get_summary("https://example.com")


class TestContentQualityCheck:
    """Tests for content quality checking."""

    @pytest.mark.asyncio
    async def test_check_content_quality_pass(self):
        """Test quality check passes with long enough summary."""
        with patch("firecrawl_client.settings") as mock_settings:
            mock_settings.firecrawl_api_key = "test_key"
            mock_settings.firecrawl_summary_min_length = 200

            with patch("httpx.AsyncClient") as mock_client_class:
                # Create a summary with exactly 200 characters
                long_summary = "a" * 200

                mock_response = AsyncMock()
                mock_response.status_code = 200
                mock_response.json = lambda: {"data": {"extract": {"summary": long_summary}}}

                mock_client = AsyncMock()
                mock_client.post.return_value = mock_response
                mock_client.__aenter__.return_value = mock_client
                mock_client.__aexit__.return_value = None
                mock_client_class.return_value = mock_client

                # Should not raise
                await check_content_quality("https://example.com")

    @pytest.mark.asyncio
    async def test_check_content_quality_fail_short(self):
        """Test quality check fails with short summary."""
        with patch("firecrawl_client.settings") as mock_settings:
            mock_settings.firecrawl_api_key = "test_key"
            mock_settings.firecrawl_summary_min_length = 200

            with patch("httpx.AsyncClient") as mock_client_class:
                # Create a summary shorter than 200 characters
                short_summary = "Short summary"

                mock_response = AsyncMock()
                mock_response.status_code = 200
                mock_response.json = lambda: {"data": {"extract": {"summary": short_summary}}}

                mock_client = AsyncMock()
                mock_client.post.return_value = mock_response
                mock_client.__aenter__.return_value = mock_client
                mock_client.__aexit__.return_value = None
                mock_client_class.return_value = mock_client

                with pytest.raises(FirecrawlError, match="summary too short"):
                    await check_content_quality("https://example.com")

    @pytest.mark.asyncio
    async def test_check_content_quality_api_error(self):
        """Test quality check fails when Firecrawl API fails."""
        with patch("firecrawl_client.settings") as mock_settings:
            mock_settings.firecrawl_api_key = "test_key"

            with patch("httpx.AsyncClient") as mock_client_class:
                mock_response = AsyncMock()
                mock_response.status_code = 500

                mock_client = AsyncMock()
                mock_client.post.return_value = mock_response
                mock_client.__aenter__.return_value = mock_client
                mock_client.__aexit__.return_value = None
                mock_client_class.return_value = mock_client

                with pytest.raises(FirecrawlError, match="API error"):
                    await check_content_quality("https://example.com")


class TestJobCreationWithQualityCheck:
    """Tests for job creation with quality check integration."""

    @pytest.mark.asyncio
    async def test_create_job_success_with_quality_check(self, mock_pb_client):
        """Test successful job creation with passing quality check."""
        app.state.pb_client = mock_pb_client

        # Mock the async check_content_quality function
        async def mock_check(url):
            return None

        with patch("firecrawl_client.check_content_quality", side_effect=mock_check):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post("/api/jobs", json={"url": "https://example.com"})

                assert response.status_code == 200
                mock_pb_client.create_job.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_job_fail_quality_check_short_summary(self, mock_pb_client):
        """Test job creation fails when summary is too short."""
        app.state.pb_client = mock_pb_client

        # Mock the async check_content_quality function to raise error
        async def mock_check(url):
            raise FirecrawlError(
                "Content quality check failed: summary too short (50 chars, minimum 200)"
            )

        with patch("firecrawl_client.check_content_quality", side_effect=mock_check):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post("/api/jobs", json={"url": "https://example.com"})

                assert response.status_code == 400
                assert "コンテンツの品質チェックに失敗しました" in response.json()["detail"]
                mock_pb_client.create_job.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_job_fail_quality_check_no_api_key(self, mock_pb_client):
        """Test job creation fails when Firecrawl API key is not configured."""
        app.state.pb_client = mock_pb_client

        async def mock_check(url):
            raise FirecrawlError("Firecrawl API key is not configured")

        with patch("firecrawl_client.check_content_quality", side_effect=mock_check):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post("/api/jobs", json={"url": "https://example.com"})

                assert response.status_code == 400
                assert "コンテンツの品質チェックに失敗しました" in response.json()["detail"]
                mock_pb_client.create_job.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_job_fail_quality_check_timeout(self, mock_pb_client):
        """Test job creation fails when Firecrawl request times out."""
        app.state.pb_client = mock_pb_client

        async def mock_check(url):
            raise FirecrawlError("Firecrawl API request timed out")

        with patch("firecrawl_client.check_content_quality", side_effect=mock_check):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post("/api/jobs", json={"url": "https://example.com"})

                assert response.status_code == 400
                assert "コンテンツの品質チェックに失敗しました" in response.json()["detail"]
                mock_pb_client.create_job.assert_not_called()
