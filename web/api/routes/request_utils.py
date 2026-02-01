"""Request utilities for extracting client information."""

from fastapi import Request


def get_client_ip(request: Request) -> str:
    """Get client IP address from request.

    Checks X-Forwarded-For header first (for proxy/Traefik scenarios),
    then falls back to direct client IP.

    Args:
        request: FastAPI request object

    Returns:
        Client IP address string, or "unknown" if unavailable
    """
    # Check for X-Forwarded-For header (behind proxy/Traefik)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
