"""Content parser for extracting structured data from HTML.

Parses HTML content and extracts metadata and main content.
"""

from dataclasses import dataclass
from datetime import datetime

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
    """Information about an image found in the content."""

    src: str
    alt: str | None = None
    title: str | None = None
    width: int | None = None
    height: int | None = None


@dataclass
class ParsedContent:
    """Parsed content with metadata."""

    metadata: ContentMetadata
    content: str
    markdown: str
    images: list[ImageInfo]  # List of images found in content

    def __init__(
        self,
        metadata: ContentMetadata,
        content: str,
        markdown: str,
        images: list[ImageInfo] | None = None,
    ):
        self.metadata = metadata
        self.content = content
        self.markdown = markdown
        self.images = images or []


def parse_html(html: str) -> ParsedContent:
    """Parse HTML content and extract metadata.

    Args:
        html: Raw HTML content.

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

    # Extract images before removing elements
    images: list[ImageInfo] = []
    if content_element:
        for img_tag in content_element.find_all("img"):
            src = img_tag.get("src")
            if src:  # Only include images with src attribute
                # Parse width/height if present
                width_str = img_tag.get("width")
                height_str = img_tag.get("height")

                width = None
                if width_str:
                    try:
                        width = int(str(width_str))
                    except (ValueError, TypeError):
                        width = None

                height = None
                if height_str:
                    try:
                        height = int(str(height_str))
                    except (ValueError, TypeError):
                        height = None

                alt_val = img_tag.get("alt")
                title_val = img_tag.get("title")

                images.append(
                    ImageInfo(
                        src=str(src),
                        alt=str(alt_val) if alt_val else None,
                        title=str(title_val) if title_val else None,
                        width=width,
                        height=height,
                    )
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

    return ParsedContent(
        metadata=metadata, content=content_text, markdown=markdown_content, images=images
    )
