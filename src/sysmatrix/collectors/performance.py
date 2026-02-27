"""Derived performance metrics built from collected hardware data."""

from __future__ import annotations

from pathlib import Path

from sysmatrix.models import PerformanceData
from sysmatrix.utils.commands import run_command


def _load_average() -> str:
    """Return 1/5/15-minute load average values."""
    try:
        values = Path("/proc/loadavg").read_text(encoding="utf-8", errors="ignore").split()
        return ", ".join(values[:3])
    except OSError:
        return "N/A"


def _read_cpu_freq_pair() -> tuple[float | None, float | None]:
    """Read current and max CPU frequency values from sysfs."""
    cur_path = Path("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq")
    max_path = Path("/sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq")
    try:
        cur = float(cur_path.read_text(encoding="utf-8", errors="ignore").strip())
        maxf = float(max_path.read_text(encoding="utf-8", errors="ignore").strip())
        if maxf > 0:
            return cur, maxf
    except OSError:
        pass
    return None, None


def _cpu_temp_from_sensors() -> float | None:
    """Best-effort CPU package temperature from sensors output."""
    data = run_command(["sensors"])
    keys = ("tctl", "tdie", "package id 0", "core 0")
    for line in data.splitlines():
        lowered = line.strip().lower()
        if not any(lowered.startswith(k + ":") for k in keys):
            continue
        token = lowered.split()[1].replace("+", "").replace("°c", "")
        try:
            return float(token)
        except ValueError:
            continue
    return None


def collect_performance(cpu_usage: float, gpu_usage: float | None) -> PerformanceData:
    """Compute performance summary fields for rendering and JSON export."""
    cur, maxf = _read_cpu_freq_pair()
    cpu_perf = round((cur / maxf) * 100.0, 1) if cur is not None and maxf else None

    cpu_temp = _cpu_temp_from_sensors()
    thermal_headroom = None
    thermal_status = "N/A"
    if cpu_temp is not None:
        thermal_headroom = round(95.0 - cpu_temp, 1)
        if thermal_headroom < 0:
            thermal_status = "THROTTLING"
        elif thermal_headroom < 10:
            thermal_status = "Critical"
        elif thermal_headroom < 20:
            thermal_status = "Warm"
        else:
            thermal_status = "OK"

    bottleneck = "None detected"
    if gpu_usage is not None:
        if cpu_usage > 85 and gpu_usage < 50:
            bottleneck = f"CPU Limited (CPU: {cpu_usage:.0f}%, GPU: {gpu_usage:.0f}%)"
        elif gpu_usage > 95 and cpu_usage < 50:
            bottleneck = f"GPU Limited (GPU: {gpu_usage:.0f}%, CPU: {cpu_usage:.0f}%)"
        elif cpu_usage > 90 and gpu_usage > 90:
            bottleneck = "Balanced (both maxed)"

    return PerformanceData(
        load_average=_load_average(),
        cpu_perf_score=cpu_perf,
        thermal_headroom_c=thermal_headroom,
        thermal_status=thermal_status,
        bottleneck=bottleneck,
    )
