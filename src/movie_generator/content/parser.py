"""Content parser for extracting structured data from HTML.

Parses HTML content and extracts metadata and main content.
"""

from datetime import datetime
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag
from markdownify import markdownify
from pydantic import BaseModel


class ContentMetadata(BaseModel):
    """Metadata extracted from content."""

    title: str | None = None
    author: str | None = None
    published_date: datetime | None = None
    description: str | None = None


class ImageInfo(BaseModel):
    """Image information extracted from blog content."""

    src: str
    alt: str | None = None
    title: str | None = None
    aria_describedby: str | None = None
    width: int | None = None
    height: int | None = None


class ParsedContent(BaseModel):
    """Parsed content with metadata."""

    metadata: ContentMetadata
    content: str
    markdown: str
    images: list[ImageInfo] | None = None


def parse_html(html: str, base_url: str | None = None) -> ParsedContent:
    """Parse HTML content and extract metadata.

    Args:
        html: Raw HTML content.
        base_url: Base URL for resolving relative image URLs.

    Returns:
        Parsed content with metadata.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Extract metadata
    metadata = ContentMetadata()

    # Title
    if title_tag := soup.find("title"):
        metadata.title = title_tag.get_text().strip()  # type: ignore[union-attr]
    elif og_title := soup.find("meta", property="og:title"):
        metadata.title = og_title.get("content", "").strip()  # type: ignore[union-attr]

    # Author
    if author_meta := soup.find("meta", attrs={"name": "author"}):
        metadata.author = author_meta.get("content", "").strip()  # type: ignore[union-attr]

    # Description
    if desc_meta := soup.find("meta", attrs={"name": "description"}):
        metadata.description = desc_meta.get("content", "").strip()  # type: ignore[union-attr]
    elif og_desc := soup.find("meta", property="og:description"):
        metadata.description = og_desc.get("content", "").strip()  # type: ignore[union-attr]

    # Extract main content (try common article selectors)
    content_element = (
        soup.find("article") or soup.find("main") or soup.find("div", class_="content") or soup.body
    )

    if content_element:
        # Remove script and style elements
        for script in content_element(["script", "style"]):  # type: ignore[operator]
            script.decompose()

        content_html = str(content_element)
        content_text = content_element.get_text(separator="\n", strip=True)  # type: ignore[union-attr]
        markdown_content = markdownify(content_html, heading_style="ATX")
    else:
        content_text = ""
        markdown_content = ""

    # Extract images from the content
    images = _extract_images(soup, base_url)

    return ParsedContent(
        metadata=metadata, content=content_text, markdown=markdown_content, images=images
    )


def _extract_image_attributes(img_tag: Tag) -> dict[str, Any]:
    """Extract basic attributes from an img tag.

    Args:
        img_tag: BeautifulSoup img element.

    Returns:
        Dictionary with src, alt, title, aria_describedby_id, width, and height.
    """
    src = img_tag.get("src")
    alt = img_tag.get("alt")
    title = img_tag.get("title")
    aria_describedby_id = img_tag.get("aria-describedby")

    # Extract width and height if available
    width: int | None = None
    height: int | None = None
    try:
        if width_attr := img_tag.get("width"):
            width = int(width_attr)  # type: ignore[arg-type]
        if height_attr := img_tag.get("height"):
            height = int(height_attr)  # type: ignore[arg-type]
    except (ValueError, TypeError):
        pass

    return {
        "src": src,
        "alt": alt,
        "title": title,
        "aria_describedby_id": aria_describedby_id,
        "width": width,
        "height": height,
    }


def _resolve_url(src: str, base_url: str | None) -> str:
    """Resolve relative URL to absolute URL.

    Args:
        src: Image source URL (may be relative).
        base_url: Base URL for resolution.

    Returns:
        Absolute URL.
    """
    if base_url:
        return urljoin(base_url, src)
    return src


def _resolve_aria_describedby(aria_describedby_id: str | None, soup: BeautifulSoup) -> str | None:
    """Resolve aria-describedby ID to referenced element's text content.

    Args:
        aria_describedby_id: ID of the element referenced by aria-describedby.
        soup: BeautifulSoup object of the HTML content.

    Returns:
        Text content of the referenced element, or None if not found.
    """
    if not aria_describedby_id:
        return None

    described_element = soup.find(id=aria_describedby_id)
    if described_element:
        return described_element.get_text(strip=True)
    return None


def _has_meaningful_description(
    alt: str | None, title: str | None, aria_describedby: str | None
) -> bool:
    """Check if an image has meaningful description.

    Meaningful description is defined as:
    - alt text with 10+ characters, OR
    - non-empty title attribute, OR
    - non-empty aria-describedby text

    Args:
        alt: Alt text attribute.
        title: Title attribute.
        aria_describedby: Resolved aria-describedby text.

    Returns:
        True if image has meaningful description.
    """
    has_meaningful_alt = bool(alt and len(alt.strip()) >= 10)
    has_title = bool(title and len(title.strip()) > 0)
    has_aria_description = bool(aria_describedby and len(aria_describedby.strip()) > 0)

    return has_meaningful_alt or has_title or has_aria_description


def _extract_images(soup: BeautifulSoup, base_url: str | None = None) -> list[ImageInfo]:
    """Extract image information from HTML content.

    Args:
        soup: BeautifulSoup object of the HTML content.
        base_url: Base URL for resolving relative URLs.

    Returns:
        List of extracted image information.
    """
    images = []

    for img_tag in soup.find_all("img"):
        # Step 1: Extract attributes
        attrs = _extract_image_attributes(img_tag)  # type: ignore[arg-type]
        src = attrs["src"]
        if not src or not isinstance(src, str):
            continue

        # Step 2: Resolve relative URL to absolute URL
        src = _resolve_url(src, base_url)

        # Step 3: Resolve aria-describedby reference
        aria_describedby = _resolve_aria_describedby(attrs["aria_describedby_id"], soup)

        # Step 4: Filter by meaningful description
        if _has_meaningful_description(attrs["alt"], attrs["title"], aria_describedby):
            images.append(
                ImageInfo(
                    src=src,
                    alt=attrs["alt"],
                    title=attrs["title"],
                    aria_describedby=aria_describedby,
                    width=attrs["width"],
                    height=attrs["height"],
                )
            )

    return images
