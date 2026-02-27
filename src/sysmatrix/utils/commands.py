"""Subprocess helpers used by collectors."""

from __future__ import annotations

import logging
import shutil
import subprocess

LOGGER = logging.getLogger(__name__)


def command_exists(name: str) -> bool:
    """Return True when an executable is available on PATH."""
    return shutil.which(name) is not None


def run_command(args: list[str], timeout_s: float = 2.0) -> str:
    """Run a command and return stdout, or an empty string on failure."""
    try:
        result = subprocess.run(
            args,
            check=False,
            text=True,
            capture_output=True,
            timeout=timeout_s,
        )
    except (OSError, subprocess.TimeoutExpired):
        LOGGER.debug("command failed to start or timed out: %s", args, exc_info=True)
        return ""
    if result.returncode != 0:
        LOGGER.debug(
            "command returned non-zero exit (%s): %s",
            result.returncode,
            args,
        )
    return (result.stdout or "").strip()
