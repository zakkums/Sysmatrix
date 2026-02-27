"""Motherboard vendor/model and VRM temperature collectors."""

from __future__ import annotations

from pathlib import Path

from sysmatrix.models import MotherboardData
from sysmatrix.utils.commands import run_command


def _read_dmi_value(path: Path, fallback_cmd: list[str]) -> str:
    """Read a DMI value from sysfs, with a command fallback."""
    if path.exists():
        value = path.read_text(encoding="utf-8", errors="ignore").strip()
        if value:
            return value
    output = run_command(fallback_cmd)
    return output if output else "Unknown"


def _parse_vrm_temp() -> float | None:
    """Best-effort parse of VRM/MOS temperature from sensors output."""
    sensors = run_command(["sensors"])
    for line in sensors.splitlines():
        if not any(token in line.lower() for token in ("vrm", "mos")):
            continue
        for token in line.split():
            cleaned = token.replace("+", "").replace("°C", "").replace("C", "")
            try:
                value = float(cleaned)
            except ValueError:
                continue
            if 20 <= value <= 130:
                return value
    return None


def collect_motherboard() -> MotherboardData:
    """Collect motherboard identity and optional VRM temperature."""
    vendor = _read_dmi_value(
        Path("/sys/class/dmi/id/board_vendor"),
        ["dmidecode", "-s", "baseboard-manufacturer"],
    )
    model = _read_dmi_value(
        Path("/sys/class/dmi/id/board_name"),
        ["dmidecode", "-s", "baseboard-product-name"],
    )
    return MotherboardData(vendor=vendor, model=model, vrm_temp_c=_parse_vrm_temp())
