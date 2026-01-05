"""Main FastAPI application."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from .config import settings
from .pocketbase_client import PocketBaseClient
from .routes import api_routes, web_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# PocketBase client (will be initialized in lifespan)
pb_client: PocketBaseClient | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager for startup and shutdown."""
    global pb_client

    # Startup
    logger.info("Starting FastAPI application...")
    pb_client = PocketBaseClient()
    app.state.pb_client = pb_client
    logger.info("PocketBase client initialized")

    yield

    # Shutdown
    logger.info("Shutting down FastAPI application...")
    if pb_client:
        await pb_client.close()
    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Movie Generator Web Service",
    description="Generate YouTube slide videos from blog URLs",
    version="0.1.0",
    lifespan=lifespan,
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Mount static files
static_path = Path(__file__).parent / "static"
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Setup templates
templates_path = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))
app.state.templates = templates

# Include routers
app.include_router(web_routes.router, tags=["web"])
app.include_router(api_routes.router, prefix="/api", tags=["api"])


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception) -> HTMLResponse:
    """Custom 404 handler."""
    templates = request.app.state.templates
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "error_message": "ページが見つかりません", "status_code": 404},
        status_code=404,
    )


@app.exception_handler(500)
async def server_error_handler(request: Request, exc: Exception) -> HTMLResponse:
    """Custom 500 handler."""
    logger.error(f"Server error: {exc}", exc_info=True)
    templates = request.app.state.templates
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "error_message": "サーバーエラーが発生しました",
            "status_code": 500,
        },
        status_code=500,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
