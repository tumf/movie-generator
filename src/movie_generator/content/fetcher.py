"""Content fetcher for retrieving content from URLs.

Fetches HTML/Markdown content from web URLs.
"""

from typing import Any

import httpx


async def fetch_url(url: str, timeout: float = 30.0) -> str:
    """Fetch content from a URL.

    Args:
        url: URL to fetch content from.
        timeout: Request timeout in seconds.

    Returns:
        Raw content as string.

    Raises:
        httpx.HTTPError: If request fails.
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text


def fetch_url_sync(url: str, timeout: float = 30.0) -> str:
    """Fetch content from a URL (synchronous version).

    Args:
        url: URL to fetch content from.
        timeout: Request timeout in seconds.

    Returns:
        Raw content as string.

    Raises:
        httpx.HTTPError: If request fails.
    """
    with httpx.Client(timeout=timeout) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.text
