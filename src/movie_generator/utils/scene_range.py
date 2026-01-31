"""Scene range parsing utilities for CLI commands."""


def parse_scene_range(scenes_arg: str) -> tuple[int | None, int | None]:
    """Parse scene range argument.

    Args:
        scenes_arg: Scene range string (e.g., "1-3", "6-" for 6 onwards, "-3" for up to 3, or "2").

    Returns:
        Tuple of (start_index, end_index) (0-based, inclusive).
        start_index can be None to indicate "from the beginning".
        end_index can be None to indicate "to the end".

    Raises:
        ValueError: If the format is invalid or range is invalid.
    """
    # Single scene number (no dash)
    if "-" not in scenes_arg:
        return _parse_single_scene(scenes_arg)

    # Range format (contains dash)
    return _parse_range_scene(scenes_arg)


def _parse_single_scene(scenes_arg: str) -> tuple[int, int]:
    """Parse single scene number.

    Args:
        scenes_arg: Scene number string (e.g., "2").

    Returns:
        Tuple of (scene_num-1, scene_num-1) (0-based, inclusive).

    Raises:
        ValueError: If the format is invalid.
    """
    try:
        scene_num = int(scenes_arg)
    except ValueError:
        raise ValueError(f"Invalid scene number: '{scenes_arg}'. Must be an integer.")

    if scene_num < 1:
        raise ValueError(f"Scene number must be >= 1, got: {scene_num}")

    # Convert to 0-based indexing
    return (scene_num - 1, scene_num - 1)


def _parse_range_scene(scenes_arg: str) -> tuple[int | None, int | None]:
    """Parse scene range with dash.

    Args:
        scenes_arg: Scene range string (e.g., "1-3", "6-", "-3").

    Returns:
        Tuple of (start_index, end_index) (0-based, inclusive).
        start_index can be None to indicate "from the beginning".
        end_index can be None to indicate "to the end".

    Raises:
        ValueError: If the format is invalid or range is invalid.
    """
    parts = scenes_arg.split("-")

    # Guard: Invalid format (too many parts)
    if len(parts) != 2:
        raise ValueError(
            f"Invalid scene range format: '{scenes_arg}'. "
            "Expected format: '1-3', '6-', '-3', or '2'"
        )

    start_part, end_part = parts

    # Guard: Both parts empty ("-")
    if not start_part and not end_part:
        raise ValueError(f"Invalid scene range format: '{scenes_arg}'. Cannot use '-' alone.")

    # Format: "-N" (from beginning to scene N)
    if not start_part:
        return _parse_end_only_range(end_part)

    # Format: "N-" (from scene N to the end)
    if not end_part:
        return _parse_start_only_range(start_part)

    # Format: "N-M" (from scene N to scene M)
    return _parse_full_range(start_part, end_part, scenes_arg)


def _parse_end_only_range(end_part: str) -> tuple[None, int]:
    """Parse "-N" format (from beginning to scene N).

    Args:
        end_part: End scene number string.

    Returns:
        Tuple of (None, end-1) (0-based, inclusive).

    Raises:
        ValueError: If the format is invalid.
    """
    try:
        end = int(end_part)
    except ValueError:
        raise ValueError(f"Invalid end scene number: '{end_part}'. Must be an integer.")

    if end < 1:
        raise ValueError(f"Scene number must be >= 1, got: {end}")

    # "-3" format - from beginning to scene 3 (0-based: None, 2)
    return (None, end - 1)


def _parse_start_only_range(start_part: str) -> tuple[int, None]:
    """Parse "N-" format (from scene N to the end).

    Args:
        start_part: Start scene number string.

    Returns:
        Tuple of (start-1, None) (0-based, inclusive).

    Raises:
        ValueError: If the format is invalid.
    """
    try:
        start = int(start_part)
    except ValueError:
        raise ValueError(f"Invalid start scene number: '{start_part}'. Must be an integer.")

    if start < 1:
        raise ValueError(f"Scene number must be >= 1, got: {start}")

    # "6-" format - from scene 6 to the end (0-based: 5, None)
    return (start - 1, None)


def _parse_full_range(start_part: str, end_part: str, scenes_arg: str) -> tuple[int, int]:
    """Parse "N-M" format (from scene N to scene M).

    Args:
        start_part: Start scene number string.
        end_part: End scene number string.
        scenes_arg: Original full argument for error messages.

    Returns:
        Tuple of (start-1, end-1) (0-based, inclusive).

    Raises:
        ValueError: If the format is invalid or range is invalid.
    """
    try:
        start = int(start_part)
    except ValueError:
        raise ValueError(f"Invalid start scene number: '{start_part}'. Must be an integer.")

    if start < 1:
        raise ValueError(f"Scene number must be >= 1, got: {start}")

    try:
        end = int(end_part)
    except ValueError:
        raise ValueError(f"Invalid end scene number: '{end_part}'. Must be an integer.")

    if end < 1:
        raise ValueError(f"Scene numbers must be >= 1, got: {scenes_arg}")

    if start > end:
        raise ValueError(
            f"Invalid scene range: {scenes_arg}. Start must be <= end. "
            f"Example: '1-3' for scenes 1 through 3."
        )

    # Convert to 0-based indexing
    return (start - 1, end - 1)
