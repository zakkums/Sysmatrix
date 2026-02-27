"""CPU collector functions."""

from __future__ import annotations

import time
from pathlib import Path

from sysmatrix.models import CpuData


def _read_cpu_model() -> str:
    """Return CPU model name from /proc/cpuinfo."""
    for line in Path("/proc/cpuinfo").read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith("model name"):
            return line.split(":", 1)[1].strip()
    return "Unknown CPU"


def _read_cpu_usage() -> float:
    """Sample /proc/stat twice to estimate total CPU usage percentage."""
    def sample() -> tuple[int, int]:
        fields = Path("/proc/stat").read_text(encoding="utf-8", errors="ignore").splitlines()[0].split()
        values = [int(x) for x in fields[1:8]]
        idle = values[3]
        total = sum(values)
        return idle, total

    idle1, total1 = sample()
    time.sleep(0.12)
    idle2, total2 = sample()
    idle_delta = idle2 - idle1
    total_delta = total2 - total1
    if total_delta <= 0:
        return 0.0
    return round(100.0 * (1.0 - (idle_delta / total_delta)), 1)


def collect_cpu() -> CpuData:
    """Collect CPU model, core count, and sampled utilization."""
    cores = 0
    for line in Path("/proc/cpuinfo").read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith("processor"):
            cores += 1
    return CpuData(
        model=_read_cpu_model(),
        cores=cores,
        usage_percent=_read_cpu_usage(),
    )
