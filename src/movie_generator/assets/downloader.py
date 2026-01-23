"""Download logo assets from URLs."""

import asyncio
import re
from pathlib import Path

import httpx

from ..constants import TimeoutConstants
from ..utils.filesystem import skip_if_exists  # type: ignore[import]


def sanitize_filename(name: str) -> str:
    """Sanitize a product/company name to create a safe filename.

    Args:
        name: Product or company name.

    Returns:
        Sanitized filename (alphanumeric + hyphens only).
    """
    # Convert to lowercase and replace spaces/underscores with hyphens
    sanitized = name.lower().replace(" ", "-").replace("_", "-")
    # Keep only alphanumeric and hyphens
    sanitized = re.sub(r"[^a-z0-9-]", "", sanitized)
    # Remove consecutive hyphens
    sanitized = re.sub(r"-+", "-", sanitized)
    # Strip leading/trailing hyphens
    return sanitized.strip("-")


async def download_logo(
    *,
    url: str,
    output_path: Path,
    max_retries: int = 3,
    retry_delay: float = 2.0,
) -> Path:
    """Download a logo from URL with retry logic.

    Args:
        url: URL of the logo to download.
        output_path: Path to save the downloaded file.
        max_retries: Maximum number of retry attempts on failure.
        retry_delay: Initial delay between retries (exponential backoff).

    Returns:
        Path to the downloaded file.

    Raises:
        httpx.HTTPError: If download fails after all retries.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Skip if already exists
    if skip_if_exists(output_path, "logo"):
        return output_path

    print(f"  ↓ Downloading logo: {url}")

    last_error = None
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=TimeoutConstants.ASSET_DOWNLOAD) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()

                # Save the file
                output_path.write_bytes(response.content)
                print(f"  ✓ Downloaded: {output_path.name} ({len(response.content)} bytes)")
                return output_path

        except httpx.HTTPStatusError as e:
            last_error = e
            print(f"⚠ HTTP error on attempt {attempt + 1}/{max_retries}: {e.response.status_code}")
        except httpx.HTTPError as e:
            last_error = e
            print(f"⚠ HTTP error on attempt {attempt + 1}/{max_retries}: {e}")
        except Exception as e:
            last_error = e
            print(f"⚠ Error on attempt {attempt + 1}/{max_retries}: {e}")

        # Retry with exponential backoff
        if attempt < max_retries - 1:
            delay = retry_delay * (2**attempt)
            print(f"  ⟳ Retrying in {delay:.1f}s...")
            await asyncio.sleep(delay)

    # All retries exhausted
    print(f"✗ Failed to download logo after {max_retries} attempts: {url}")
    if last_error:
        raise last_error
    raise RuntimeError(f"Failed to download logo from {url}")
