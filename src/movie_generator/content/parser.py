"""Content parser for extracting structured data from HTML.

Parses HTML content and extracts metadata and main content.
"""

from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from markdownify import markdownify


@dataclass
class ContentMetadata:
    """Metadata extracted from content."""

    title: str | None = None
    author: str | None = None
    published_date: datetime | None = None
    description: str | None = None


@dataclass
class ImageInfo:
    """Image information extracted from blog content."""

    src: str
    alt: str | None = None
    title: str | None = None
    aria_describedby: str | None = None
    width: int | None = None
    height: int | None = None


@dataclass
class ParsedContent:
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
        metadata.title = title_tag.get_text().strip()
    elif og_title := soup.find("meta", property="og:title"):
        metadata.title = og_title.get("content", "").strip()

    # Author
    if author_meta := soup.find("meta", attrs={"name": "author"}):
        metadata.author = author_meta.get("content", "").strip()

    # Description
    if desc_meta := soup.find("meta", attrs={"name": "description"}):
        metadata.description = desc_meta.get("content", "").strip()
    elif og_desc := soup.find("meta", property="og:description"):
        metadata.description = og_desc.get("content", "").strip()

    # Extract main content (try common article selectors)
    content_element = (
        soup.find("article") or soup.find("main") or soup.find("div", class_="content") or soup.body
    )

    if content_element:
        # Remove script and style elements
        for script in content_element(["script", "style"]):
            script.decompose()

        content_html = str(content_element)
        content_text = content_element.get_text(separator="\n", strip=True)
        markdown_content = markdownify(content_html, heading_style="ATX")
    else:
        content_text = ""
        markdown_content = ""

    # Extract images from the content
    images = _extract_images(soup, base_url)

    return ParsedContent(
        metadata=metadata, content=content_text, markdown=markdown_content, images=images
    )


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
        src = img_tag.get("src")
        if not src:
            continue

        # Resolve relative URLs to absolute URLs
        if base_url:
            src = urljoin(base_url, src)

        # Extract alt and title attributes
        alt = img_tag.get("alt")
        title = img_tag.get("title")

        # Extract aria-describedby if present
        aria_describedby = None
        aria_describedby_id = img_tag.get("aria-describedby")
        if aria_describedby_id:
            described_element = soup.find(id=aria_describedby_id)
            if described_element:
                aria_describedby = described_element.get_text(strip=True)

        # Extract width and height if available
        width = None
        height = None
        try:
            if width_attr := img_tag.get("width"):
                width = int(width_attr)
            if height_attr := img_tag.get("height"):
                height = int(height_attr)
        except (ValueError, TypeError):
            pass

        # Filter images by meaningful description (as per spec)
        # Meaningful: alt text (10+ chars) OR title OR aria-describedby
        has_meaningful_alt = alt and len(alt.strip()) >= 10
        has_title = title and len(title.strip()) > 0
        has_aria_description = aria_describedby and len(aria_describedby.strip()) > 0

        if has_meaningful_alt or has_title or has_aria_description:
            images.append(
                ImageInfo(
                    src=src,
                    alt=alt,
                    title=title,
                    aria_describedby=aria_describedby,
                    width=width,
                    height=height,
                )
            )

    return images
