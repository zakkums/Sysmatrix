"""Compact terminal renderer for quick status checks."""

from __future__ import annotations

from sysmatrix.config import RuntimeConfig
from sysmatrix.models import Snapshot
from sysmatrix.utils.formatting import color_usage


def render_short(snapshot: Snapshot, config: RuntimeConfig) -> str:
    """Render a one-line CPU/GPU/RAM summary."""
    cpu = snapshot.cpu
    gpu = snapshot.gpu
    mem = snapshot.memory
    gpu_use = "N/A" if gpu.utilization_percent is None else color_usage(gpu.utilization_percent, config.plain)
    return (
        f"CPU {color_usage(cpu.usage_percent, config.plain)} "
        f"| GPU {gpu_use} "
        f"| RAM {mem.used_gb:.1f}/{mem.total_gb:.1f} GiB "
        f"({color_usage(mem.usage_percent, config.plain)})"
    )
