"""Formatting and redaction helpers for renderers."""

from __future__ import annotations


class Color:
    """ANSI color constants used by terminal renderers."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    CYAN = "\033[36m"


def color_usage(value: float, plain: bool) -> str:
    """Format utilization percentage with severity color when enabled."""
    if plain:
        return f"{value:.1f}%"
    if value < 30:
        color = Color.GREEN
    elif value < 70:
        color = Color.YELLOW
    else:
        color = Color.RED
    return f"{color}{value:.1f}%{Color.RESET}"


def maybe_redact(value: str, opsec: bool) -> str:
    """Redact potentially sensitive values when OPSEC mode is enabled."""
    return "[REDACTED]" if opsec else value
