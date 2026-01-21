"""Tests for API endpoints."""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

# Add API directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

from main import app


@pytest.fixture
def mock_pb_client():
    """Mock PocketBase client."""
    client = AsyncMock()
    return client


@pytest.fixture
def test_video_file():
    """Create a temporary test video file."""
    # Create a temporary file with some content
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".mp4", delete=False) as f:
        # Write some test data (1MB)
        test_data = b"TEST_VIDEO_DATA" * 70000  # ~1MB
        f.write(test_data)
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


class TestVideoStreamingEndpoint:
    """Tests for video streaming endpoint."""

    @pytest.mark.asyncio
    async def test_stream_video_full_file(self, mock_pb_client, test_video_file):
        """Test streaming entire video file without Range header."""
        # Setup mock
        mock_pb_client.get_job.return_value = {
            "id": "test_job_123",
            "status": "completed",
            "video_path": test_video_file,
        }

        app.state.pb_client = mock_pb_client

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/jobs/test_job_123/video")

            assert response.status_code == 200
            assert response.headers["content-type"] == "video/mp4"
            assert "accept-ranges" in response.headers
            assert response.headers["accept-ranges"] == "bytes"
            assert "content-length" in response.headers
            assert int(response.headers["content-length"]) == os.path.getsize(test_video_file)

            # Verify content
            content = response.content
            assert len(content) == os.path.getsize(test_video_file)
            assert content.startswith(b"TEST_VIDEO_DATA")

    @pytest.mark.asyncio
    async def test_stream_video_with_range(self, mock_pb_client, test_video_file):
        """Test streaming video with Range header (partial content)."""
        # Setup mock
        mock_pb_client.get_job.return_value = {
            "id": "test_job_123",
            "status": "completed",
            "video_path": test_video_file,
        }

        app.state.pb_client = mock_pb_client

        file_size = os.path.getsize(test_video_file)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Request bytes 0-1023 (first 1KB)
            response = await client.get(
                "/api/jobs/test_job_123/video", headers={"Range": "bytes=0-1023"}
            )

            assert response.status_code == 206  # Partial Content
            assert response.headers["content-type"] == "video/mp4"
            assert "content-range" in response.headers
            assert response.headers["content-range"] == f"bytes 0-1023/{file_size}"
            assert "accept-ranges" in response.headers
            assert int(response.headers["content-length"]) == 1024

            # Verify content
            content = response.content
            assert len(content) == 1024
            assert content.startswith(b"TEST_VIDEO_DATA")

    @pytest.mark.asyncio
    async def test_stream_video_with_open_ended_range(self, mock_pb_client, test_video_file):
        """Test streaming video with open-ended Range header (bytes=1000-)."""
        # Setup mock
        mock_pb_client.get_job.return_value = {
            "id": "test_job_123",
            "status": "completed",
            "video_path": test_video_file,
        }

        app.state.pb_client = mock_pb_client

        file_size = os.path.getsize(test_video_file)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Request bytes from 1000 to end
            response = await client.get(
                "/api/jobs/test_job_123/video", headers={"Range": "bytes=1000-"}
            )

            assert response.status_code == 206
            assert response.headers["content-type"] == "video/mp4"
            assert "content-range" in response.headers
            assert response.headers["content-range"] == f"bytes 1000-{file_size - 1}/{file_size}"
            assert int(response.headers["content-length"]) == file_size - 1000

            # Verify content length
            content = response.content
            assert len(content) == file_size - 1000

    @pytest.mark.asyncio
    async def test_stream_video_invalid_range(self, mock_pb_client, test_video_file):
        """Test streaming video with invalid Range header (out of bounds)."""
        # Setup mock
        mock_pb_client.get_job.return_value = {
            "id": "test_job_123",
            "status": "completed",
            "video_path": test_video_file,
        }

        app.state.pb_client = mock_pb_client

        file_size = os.path.getsize(test_video_file)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Request range beyond file size
            response = await client.get(
                "/api/jobs/test_job_123/video",
                headers={"Range": f"bytes={file_size}-{file_size + 1000}"},
            )

            assert response.status_code == 416  # Range Not Satisfiable

    @pytest.mark.asyncio
    async def test_stream_video_job_not_completed(self, mock_pb_client, test_video_file):
        """Test streaming video when job is not completed."""
        # Setup mock
        mock_pb_client.get_job.return_value = {
            "id": "test_job_123",
            "status": "processing",
            "video_path": test_video_file,
        }

        app.state.pb_client = mock_pb_client

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/jobs/test_job_123/video")

            assert response.status_code == 400
            assert "まだ生成されていません" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_stream_video_no_video_path(self, mock_pb_client):
        """Test streaming video when video_path is missing."""
        # Setup mock
        mock_pb_client.get_job.return_value = {
            "id": "test_job_123",
            "status": "completed",
            "video_path": None,
        }

        app.state.pb_client = mock_pb_client

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/jobs/test_job_123/video")

            assert response.status_code == 404
            # Response may be JSON or HTML depending on error handler
            if "application/json" in response.headers.get("content-type", ""):
                assert "見つかりません" in response.json()["detail"]
            else:
                # HTML error page
                assert "見つかりません" in response.text or response.status_code == 404

    @pytest.mark.asyncio
    async def test_stream_video_file_not_exists(self, mock_pb_client):
        """Test streaming video when video file doesn't exist."""
        # Setup mock with non-existent path
        mock_pb_client.get_job.return_value = {
            "id": "test_job_123",
            "status": "completed",
            "video_path": "/nonexistent/path/video.mp4",
        }

        app.state.pb_client = mock_pb_client

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/jobs/test_job_123/video")

            assert response.status_code == 404
            # Response may be JSON or HTML depending on error handler
            if "application/json" in response.headers.get("content-type", ""):
                assert "見つかりません" in response.json()["detail"]
            else:
                # HTML error page
                assert "見つかりません" in response.text or response.status_code == 404

    @pytest.mark.asyncio
    async def test_stream_video_job_not_found(self, mock_pb_client):
        """Test streaming video when job doesn't exist."""
        # Setup mock to raise exception
        mock_pb_client.get_job.side_effect = Exception("Job not found")

        app.state.pb_client = mock_pb_client

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/jobs/nonexistent_job/video")

            assert response.status_code == 500
            assert "ストリーミングに失敗しました" in response.json()["detail"]
