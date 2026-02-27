"""Storage usage, type, temperature, and wear collectors."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from sysmatrix.models import StorageData
from sysmatrix.utils.commands import run_command


def _to_float(value: str) -> float | None:
    """Convert text to float, returning None on parse failure."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value: str) -> int | None:
    """Convert text to int, returning None on parse failure."""
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _last_number(text: str) -> float | None:
    """Extract the last numeric token from a line of text."""
    matches = re.findall(r"-?\d+(?:\.\d+)?", text)
    if not matches:
        return None
    return _to_float(matches[-1])


def _root_block_device() -> str:
    """Resolve root filesystem backing block device name."""
    source = run_command(["findmnt", "-no", "SOURCE", "/"])
    if not source:
        lines = run_command(["df", "/", "--output=source"]).splitlines()
        source = lines[-1] if lines else ""
    if source.startswith("/dev/mapper/"):
        mapped = run_command(["lsblk", "-no", "pkname", source])
        source = f"/dev/{mapped}" if mapped else source
    if source.startswith("/dev/"):
        source = source[5:]
    if source.startswith("nvme") and "p" in source:
        return source.split("p", 1)[0]
    return source.rstrip("0123456789")


def _device_type(device: str) -> str:
    """Classify device as NVMe SSD, SATA SSD, HDD, or Unknown."""
    if not device:
        return "Unknown"
    if device.startswith("nvme"):
        return "NVMe SSD"
    rotational_file = Path(f"/sys/block/{device}/queue/rotational")
    if rotational_file.exists():
        val = rotational_file.read_text(encoding="utf-8", errors="ignore").strip()
        return "SATA SSD" if val == "0" else "HDD"
    return "Unknown"


def _temperature_from_smart(device: str) -> float | None:
    """Read disk temperature from SMART output or NVMe hwmon fallback."""
    if not device:
        return None
    out = run_command(["smartctl", "-A", f"/dev/{device}"])
    for line in out.splitlines():
        lowered = line.lower()
        if any(
            marker in lowered
            for marker in ("temperature:", "composite temperature", "temperature_celsius", "airflow_temperature_cel")
        ):
            value = _last_number(line)
            if value is not None:
                return value
    if device.startswith("nvme"):
        for hwmon in Path("/sys/class/hwmon").glob("hwmon*"):
            name_file = hwmon / "name"
            temp_file = hwmon / "temp1_input"
            if not name_file.exists() or not temp_file.exists():
                continue
            name = name_file.read_text(encoding="utf-8", errors="ignore").strip().lower()
            if "nvme" not in name:
                continue
            milli = _to_int(temp_file.read_text(encoding="utf-8", errors="ignore").strip())
            if milli is not None:
                return round(milli / 1000.0, 1)
    return None


def _wear_from_smart(device: str) -> int | None:
    """Read disk wear percentage from SMART fields when available."""
    if not device:
        return None
    out = run_command(["smartctl", "-A", f"/dev/{device}"])
    for line in out.splitlines():
        lowered = line.lower()
        number = _last_number(line)
        if "percentage used:" in lowered:
            val = _to_int(str(number)) if number is not None else None
            if val is not None:
                return max(0, min(100, val))
        if "remain" in lowered:
            remain = _to_int(str(number)) if number is not None else None
            if remain is not None:
                return max(0, min(100, 100 - remain))
        if "media_wearout_indicator" in lowered or "wear_leveling_count" in lowered:
            remaining = _to_int(str(number)) if number is not None else None
            if remaining is not None:
                return max(0, min(100, 100 - remaining))
    return None


def collect_storage() -> StorageData:
    """Collect root storage usage and optional health indicators."""
    usage = shutil.disk_usage("/")
    total_gb = round(usage.total / 1024 / 1024 / 1024, 1)
    used_gb = round(usage.used / 1024 / 1024 / 1024, 1)
    usage_percent = round((usage.used / usage.total * 100.0), 1) if usage.total else 0.0

    root_device = _root_block_device()
    return StorageData(
        root_mount="/",
        device_type=_device_type(root_device),
        total_gb=total_gb,
        used_gb=used_gb,
        usage_percent=usage_percent,
        temperature_c=_temperature_from_smart(root_device),
        wear_percent=_wear_from_smart(root_device),
    )
