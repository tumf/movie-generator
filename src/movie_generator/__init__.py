"""Movie Generator - YouTube slide video generator from blog URLs."""

__version__ = "0.2.19"

# Export custom exceptions for convenience
from .exceptions import (
    AudioGenerationError,
    ConfigurationError,
    ContentFetchError,
    MCPError,
    MovieGeneratorError,
    RenderingError,
    SlideGenerationError,
)

__all__ = [
    "MovieGeneratorError",
    "ConfigurationError",
    "RenderingError",
    "MCPError",
    "ContentFetchError",
    "AudioGenerationError",
    "SlideGenerationError",
]
