"""Unit tests for retry utility."""

import asyncio

import pytest

from movie_generator.constants import RetryConfig
from movie_generator.utils.retry import retry_with_backoff


class TestRetryWithBackoff:
    """Test retry_with_backoff utility."""

    @pytest.mark.asyncio
    async def test_successful_on_first_attempt(self):
        """Test that successful operations don't retry."""
        call_count = 0

        async def succeed_immediately() -> str:
            nonlocal call_count
            call_count += 1
            return "success"

        result = await retry_with_backoff(succeed_immediately)
        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_on_failure(self):
        """Test that failures trigger retries."""
        call_count = 0

        async def fail_twice_then_succeed() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError(f"Attempt {call_count} failed")
            return "success"

        result = await retry_with_backoff(
            fail_twice_then_succeed,
            max_retries=3,
            initial_delay=0.01,  # Use small delay for testing
            backoff_factor=2.0,
        )
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_exhausted_retries(self):
        """Test that errors are raised when retries are exhausted."""
        call_count = 0

        async def always_fail() -> str:
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")

        with pytest.raises(ValueError, match="Always fails"):
            await retry_with_backoff(
                always_fail,
                max_retries=3,
                initial_delay=0.01,
                backoff_factor=2.0,
            )
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_uses_retry_config_constants(self):
        """Test that RetryConfig constants are used correctly."""
        call_count = 0

        async def fail_then_succeed() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("First attempt fails")
            return "success"

        result = await retry_with_backoff(
            fail_then_succeed,
            max_retries=RetryConfig.MAX_RETRIES,
            initial_delay=0.01,  # Override for testing speed
            backoff_factor=RetryConfig.BACKOFF_FACTOR,
        )
        assert result == "success"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_exponential_backoff_timing(self):
        """Test that exponential backoff delays are applied correctly."""
        call_times = []

        async def fail_twice() -> str:
            call_times.append(asyncio.get_event_loop().time())
            if len(call_times) < 3:
                raise ValueError("Not yet")
            return "success"

        await retry_with_backoff(
            fail_twice,
            max_retries=3,
            initial_delay=0.1,
            backoff_factor=2.0,
        )

        assert len(call_times) == 3
        # Check delays between attempts (with some tolerance for timing precision)
        delay_1 = call_times[1] - call_times[0]
        delay_2 = call_times[2] - call_times[1]

        # First delay should be ~0.1s (initial_delay)
        assert 0.08 < delay_1 < 0.15
        # Second delay should be ~0.2s (initial_delay * backoff_factor)
        assert 0.18 < delay_2 < 0.25

    @pytest.mark.asyncio
    async def test_should_retry_callback(self):
        """Test that should_retry callback controls retry behavior."""
        call_count = 0

        async def fail_with_value_error() -> str:
            nonlocal call_count
            call_count += 1
            raise ValueError("Non-retryable error")

        def should_retry(error: Exception) -> bool:
            # Don't retry ValueError
            return not isinstance(error, ValueError)

        with pytest.raises(ValueError, match="Non-retryable error"):
            await retry_with_backoff(
                fail_with_value_error,
                max_retries=3,
                initial_delay=0.01,
                should_retry=should_retry,
            )
        # Should fail immediately without retry
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_should_retry_allows_specific_errors(self):
        """Test that should_retry allows retrying specific errors."""
        call_count = 0

        async def fail_with_runtime_error() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise RuntimeError("Retryable error")
            return "success"

        def should_retry(error: Exception) -> bool:
            # Only retry RuntimeError
            return isinstance(error, RuntimeError)

        result = await retry_with_backoff(
            fail_with_runtime_error,
            max_retries=3,
            initial_delay=0.01,
            should_retry=should_retry,
        )
        assert result == "success"
        assert call_count == 2
