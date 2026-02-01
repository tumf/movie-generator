"""Worker configuration settings."""

from __future__ import annotations

import os
from pathlib import Path


class WorkerSettings:
    """Worker configuration."""

    pocketbase_url: str = "http://localhost:8090"
    max_concurrent_jobs: int = 2
    worker_poll_interval: int = 5  # seconds
    job_data_dir: Path = Path("/app/data/jobs")
    config_path: Path | None = None
    mcp_config_path: Path | None = None

    def __init__(self) -> None:
        """Initialize configuration from environment variables."""
        self.pocketbase_url = os.getenv("POCKETBASE_URL", self.pocketbase_url)
        self.max_concurrent_jobs = int(
            os.getenv("MAX_CONCURRENT_JOBS", str(self.max_concurrent_jobs))
        )
        self.worker_poll_interval = int(
            os.getenv("WORKER_POLL_INTERVAL", str(self.worker_poll_interval))
        )
        job_data_dir_str = os.getenv("JOB_DATA_DIR", str(self.job_data_dir))
        self.job_data_dir = Path(job_data_dir_str)

        # MCP agent configuration
        config_path_str = os.getenv("CONFIG_PATH")
        if config_path_str:
            self.config_path = Path(config_path_str)

        mcp_config_path_str = os.getenv("MCP_CONFIG_PATH")
        if mcp_config_path_str:
            self.mcp_config_path = Path(mcp_config_path_str)
