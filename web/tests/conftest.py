"""Pytest configuration and fixtures."""

import pytest

# Add fixtures here for testing


@pytest.fixture
def anyio_backend():
    """Use asyncio backend for async tests."""
    return "asyncio"
