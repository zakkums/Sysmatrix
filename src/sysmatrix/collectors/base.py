"""Shared collector exceptions and base primitives."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CollectorError(Exception):
    """Domain-specific collector exception type."""
    message: str

    def __str__(self) -> str:
        return self.message
