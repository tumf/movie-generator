"""Custom exception classes for Movie Generator.

This module defines a hierarchy of custom exceptions to provide
better error handling and clearer error messages throughout the application.
"""


class MovieGeneratorError(Exception):
    """Base exception for all Movie Generator errors.

    All custom exceptions in this application should inherit from this class.
    This allows catching all application-specific errors with a single except clause.
    """

    pass


class ConfigurationError(MovieGeneratorError):
    """Configuration-related errors.

    Raised when there are issues with:
    - Configuration file parsing
    - Invalid configuration values
    - Missing required configuration
    - Environment variable problems
    """

    pass


class RenderingError(MovieGeneratorError):
    """Video rendering errors.

    Raised when there are issues with:
    - Video composition generation
    - Remotion rendering process
    - FFmpeg execution
    - Output file generation
    """

    pass


class MCPError(MovieGeneratorError):
    """MCP (Model Context Protocol) communication errors.

    Raised when there are issues with:
    - MCP server connection
    - MCP request/response handling
    - MCP tool execution
    """

    pass


class ContentFetchError(MovieGeneratorError):
    """Content fetching errors.

    Raised when there are issues with:
    - URL fetching
    - HTML parsing
    - Content extraction
    - Network connectivity
    """

    pass


class AudioGenerationError(MovieGeneratorError):
    """Audio synthesis errors.

    Raised when there are issues with:
    - VOICEVOX synthesis
    - Audio file generation
    - Voice configuration
    """

    pass


class SlideGenerationError(MovieGeneratorError):
    """Slide image generation errors.

    Raised when there are issues with:
    - Slide image generation via LLM
    - Image file download/save
    - Slide prompt processing
    """

    pass
