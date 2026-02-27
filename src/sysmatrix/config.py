"""Runtime configuration model derived from CLI arguments."""

from dataclasses import dataclass


@dataclass
class RuntimeConfig:
    """Flags and runtime options used across collectors and renderers."""
    short: bool = False
    plain: bool = False
    opsec: bool = False
    json: bool = False
    watch: bool = False
    watch_interval: int = 1
    logo: str = "debian"
