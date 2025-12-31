"""Subprocess execution utilities."""

import subprocess
from pathlib import Path


def run_command_safely(
    command: list[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
    capture_output: bool = True,
    text: bool = True,
    error_message: str | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run a command with consistent error handling.

    Args:
        command: Command and arguments as list.
        cwd: Working directory for command execution.
        check: Whether to raise CalledProcessError on non-zero exit.
        capture_output: Whether to capture stdout/stderr.
        text: Whether to decode output as text.
        error_message: Custom error message prefix on failure.

    Returns:
        CompletedProcess instance.

    Raises:
        RuntimeError: If command not found or execution fails with custom message.
        subprocess.CalledProcessError: If check=True and command fails.
    """
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            check=check,
            capture_output=capture_output,
            text=text,
        )
    except FileNotFoundError as e:
        cmd_name = command[0] if command else "command"
        msg = error_message or f"{cmd_name} is not installed or not available in PATH"
        raise RuntimeError(msg) from e
    except subprocess.CalledProcessError as e:
        if error_message:
            # Re-raise with custom message in exception chain
            raise RuntimeError(f"{error_message}\n{e.stderr if e.stderr else ''}") from e
        raise
