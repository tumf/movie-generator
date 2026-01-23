"""Firecrawl API client for content quality checking."""

import httpx
from typing import Dict, Any

from config import settings


class FirecrawlError(Exception):
    """Base exception for Firecrawl-related errors."""

    pass


class FirecrawlClient:
    """Client for Firecrawl API."""

    BASE_URL = "https://api.firecrawl.dev/v1"

    def __init__(self, api_key: str | None = None):
        """Initialize Firecrawl client.

        Args:
            api_key: Firecrawl API key (optional, defaults to settings)
        """
        self.api_key = api_key or settings.firecrawl_api_key
        if not self.api_key:
            raise FirecrawlError("Firecrawl API key is not configured")

    async def get_summary(self, url: str, timeout: int = 30) -> str:
        """Fetch summary of a URL using Firecrawl.

        Args:
            url: URL to fetch summary for
            timeout: Request timeout in seconds

        Returns:
            Summary text (stripped of whitespace)

        Raises:
            FirecrawlError: If API call fails or returns an error
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "url": url,
            "formats": ["extract"],
            "extract": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": "A comprehensive summary of the main content",
                        }
                    },
                    "required": ["summary"],
                }
            },
        }

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{self.BASE_URL}/scrape",
                    json=payload,
                    headers=headers,
                )

                if response.status_code == 401:
                    raise FirecrawlError("Firecrawl API authentication failed")
                elif response.status_code == 429:
                    raise FirecrawlError("Firecrawl API rate limit exceeded")
                elif response.status_code >= 400:
                    raise FirecrawlError(f"Firecrawl API error: HTTP {response.status_code}")

                data = response.json()

                # Extract summary from the response
                if "data" in data and "extract" in data["data"]:
                    summary = data["data"]["extract"].get("summary", "")
                    return summary.strip()
                else:
                    raise FirecrawlError("Unexpected response format from Firecrawl")

        except httpx.TimeoutException:
            raise FirecrawlError("Firecrawl API request timed out")
        except httpx.RequestError as e:
            raise FirecrawlError(f"Firecrawl API request failed: {str(e)}")
        except Exception as e:
            if isinstance(e, FirecrawlError):
                raise
            raise FirecrawlError(f"Unexpected error: {str(e)}")


async def check_content_quality(url: str) -> None:
    """Check if URL content meets minimum quality standards.

    Args:
        url: URL to check

    Raises:
        FirecrawlError: If quality check fails or cannot be performed
    """
    client = FirecrawlClient()
    summary = await client.get_summary(url)

    if len(summary) < settings.firecrawl_summary_min_length:
        raise FirecrawlError(
            f"Content quality check failed: summary too short "
            f"({len(summary)} chars, minimum {settings.firecrawl_summary_min_length})"
        )
