"""Retry utility with exponential backoff."""

import asyncio
from collections.abc import Awaitable, Callable


async def retry_with_backoff[T](
    func: Callable[[], Awaitable[T]],
    *,
    max_retries: int = 3,
    initial_delay: float = 2.0,
    backoff_factor: float = 2.0,
    error_message_prefix: str = "Operation",
    should_retry: Callable[[Exception], bool] | None = None,
) -> T:
    """Retry an async function with exponential backoff.

    Args:
        func: Async function to retry.
        max_retries: Maximum number of retry attempts.
        initial_delay: Initial delay between retries in seconds.
        backoff_factor: Multiplier for delay on each retry.
        error_message_prefix: Prefix for error messages.
        should_retry: Optional callable to determine if error should be retried.
                     If None, all errors are retried. If provided, only errors
                     where should_retry(error) returns True are retried.

    Returns:
        Result from successful function call.

    Raises:
        Exception: Last exception if all retries fail or should_retry returns False.
    """
    last_error: Exception | None = None

    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            last_error = e

            # Check if we should retry this error
            if should_retry is not None and not should_retry(e):
                print(f"✗ {error_message_prefix} failed with non-retryable error: {e}")
                raise e

            print(f"⚠ {error_message_prefix} error on attempt {attempt + 1}/{max_retries}: {e}")

            # Retry with exponential backoff
            if attempt < max_retries - 1:
                delay = initial_delay * (backoff_factor**attempt)
                print(f"  ⟳ Retrying in {delay:.1f}s...")
                await asyncio.sleep(delay)

    # All retries exhausted
    print(f"✗ {error_message_prefix} failed after {max_retries} attempts")
    if last_error:
        raise last_error
    raise RuntimeError(f"{error_message_prefix} failed with no error captured")
