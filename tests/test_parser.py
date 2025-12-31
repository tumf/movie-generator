"""Tests for content parser."""


from movie_generator.content.parser import parse_html


def test_parse_html_basic():
    """Test basic HTML parsing."""
    html = """
    <html>
        <head>
            <title>Test Title</title>
            <meta name="description" content="Test description">
        </head>
        <body>
            <article>
                <h1>Test Article</h1>
                <p>Test content</p>
            </article>
        </body>
    </html>
    """
    parsed = parse_html(html)
    assert parsed.metadata.title == "Test Title"
    assert parsed.metadata.description == "Test description"
    assert "Test Article" in parsed.content


def test_extract_images_with_meaningful_alt():
    """Test image extraction with meaningful alt text (10+ characters)."""
    html = """
    <html>
        <body>
            <img src="https://example.com/image1.jpg" alt="A meaningful description">
            <img src="https://example.com/image2.jpg" alt="Short">
            <img src="https://example.com/image3.jpg">
        </body>
    </html>
    """
    parsed = parse_html(html, base_url="https://example.com")
    assert parsed.images is not None
    assert len(parsed.images) == 1
    assert parsed.images[0].src == "https://example.com/image1.jpg"
    assert parsed.images[0].alt == "A meaningful description"


def test_extract_images_with_title():
    """Test image extraction with title attribute."""
    html = """
    <html>
        <body>
            <img src="image1.jpg" title="Image Title">
            <img src="image2.jpg" alt="Short">
        </body>
    </html>
    """
    parsed = parse_html(html, base_url="https://example.com/blog/")
    assert parsed.images is not None
    assert len(parsed.images) == 1
    assert parsed.images[0].src == "https://example.com/blog/image1.jpg"
    assert parsed.images[0].title == "Image Title"


def test_extract_images_with_aria_describedby():
    """Test image extraction with aria-describedby reference."""
    html = """
    <html>
        <body>
            <img src="diagram.png" aria-describedby="desc1">
            <p id="desc1">This is a detailed diagram description</p>
            <img src="chart.png" aria-describedby="nonexistent">
        </body>
    </html>
    """
    parsed = parse_html(html, base_url="https://example.com")
    assert parsed.images is not None
    assert len(parsed.images) == 1
    assert parsed.images[0].src == "https://example.com/diagram.png"
    assert parsed.images[0].aria_describedby == "This is a detailed diagram description"


def test_extract_images_relative_url_resolution():
    """Test relative URL resolution for images."""
    html = """
    <html>
        <body>
            <img src="/images/test.jpg" alt="Absolute path image">
            <img src="relative/test.jpg" alt="Relative path image">
            <img src="../parent/test.jpg" alt="Parent relative image">
        </body>
    </html>
    """
    parsed = parse_html(html, base_url="https://example.com/blog/post/")
    assert parsed.images is not None
    assert len(parsed.images) == 3
    assert parsed.images[0].src == "https://example.com/images/test.jpg"
    assert parsed.images[1].src == "https://example.com/blog/post/relative/test.jpg"
    assert parsed.images[2].src == "https://example.com/blog/parent/test.jpg"


def test_extract_images_with_dimensions():
    """Test extraction of width and height attributes."""
    html = """
    <html>
        <body>
            <img src="test.jpg" alt="Test image with dimensions" width="800" height="600">
            <img src="test2.jpg" alt="Test image without dimensions">
        </body>
    </html>
    """
    parsed = parse_html(html, base_url="https://example.com")
    assert parsed.images is not None
    assert len(parsed.images) == 2
    assert parsed.images[0].width == 800
    assert parsed.images[0].height == 600
    assert parsed.images[1].width is None
    assert parsed.images[1].height is None


def test_extract_images_no_meaningful_description():
    """Test that images without meaningful description are excluded."""
    html = """
    <html>
        <body>
            <img src="test1.jpg">
            <img src="test2.jpg" alt="">
            <img src="test3.jpg" alt="Short">
            <img src="test4.jpg" alt="This is a meaningful description">
        </body>
    </html>
    """
    parsed = parse_html(html, base_url="https://example.com")
    assert parsed.images is not None
    assert len(parsed.images) == 1
    assert parsed.images[0].src == "https://example.com/test4.jpg"


def test_extract_images_without_base_url():
    """Test image extraction without base URL (absolute URLs only)."""
    html = """
    <html>
        <body>
            <img src="https://example.com/absolute.jpg" alt="Absolute URL image">
            <img src="relative.jpg" alt="Relative URL image">
        </body>
    </html>
    """
    parsed = parse_html(html)
    assert parsed.images is not None
    # Both images should be extracted, but relative URL won't be resolved
    assert len(parsed.images) == 2
    assert parsed.images[0].src == "https://example.com/absolute.jpg"
    assert parsed.images[1].src == "relative.jpg"


def test_extract_images_empty_html():
    """Test image extraction from empty HTML."""
    html = "<html><body></body></html>"
    parsed = parse_html(html)
    assert parsed.images is not None
    assert len(parsed.images) == 0
