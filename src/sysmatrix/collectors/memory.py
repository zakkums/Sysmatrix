"""Memory and swap collector functions."""

from __future__ import annotations

from pathlib import Path

from sysmatrix.models import MemoryData


def _parse_meminfo() -> dict[str, int]:
    """Parse /proc/meminfo into a key->value(kB) mapping."""
    out: dict[str, int] = {}
    for line in Path("/proc/meminfo").read_text(encoding="utf-8", errors="ignore").splitlines():
        if ":" not in line:
            continue
        key, rest = line.split(":", 1)
        value_kb = rest.strip().split()[0]
        out[key] = int(value_kb)
    return out


def _kb_to_gb(value: int) -> float:
    """Convert a kB value to GiB with one decimal place."""
    return round(value / 1024 / 1024, 1)


def collect_memory() -> MemoryData:
    """Collect RAM and swap usage derived from /proc/meminfo."""
    mem = _parse_meminfo()
    total = mem.get("MemTotal", 0)
    available = mem.get("MemAvailable", 0)
    used = max(total - available, 0)
    swap_total = mem.get("SwapTotal", 0)
    swap_free = mem.get("SwapFree", 0)
    swap_used = max(swap_total - swap_free, 0)
    usage = (used / total * 100.0) if total else 0.0
    return MemoryData(
        total_gb=_kb_to_gb(total),
        used_gb=_kb_to_gb(used),
        usage_percent=round(usage, 1),
        swap_total_gb=_kb_to_gb(swap_total),
        swap_used_gb=_kb_to_gb(swap_used),
    )
