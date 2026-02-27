"""GPU collector with NVIDIA, AMD, and Intel best-effort support."""

from __future__ import annotations

import csv
from pathlib import Path

from sysmatrix.models import GpuData
from sysmatrix.utils.commands import command_exists, run_command


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


def _vendor_from_lspci() -> tuple[str, str]:
    """Detect primary GPU vendor/model from lspci output."""
    output = run_command(["lspci"])
    for line in output.splitlines():
        line_lower = line.lower()
        if not any(token in line_lower for token in ("vga", "3d", "display")):
            continue
        if "nvidia" in line_lower:
            return "nvidia", line.split(":", 2)[-1].strip()
        if any(token in line_lower for token in ("amd", "ati", "radeon")):
            return "amd", line.split(":", 2)[-1].strip()
        if "intel" in line_lower:
            return "intel", line.split(":", 2)[-1].strip()
        return "unknown", line.split(":", 2)[-1].strip()
    return "unknown", "Unknown GPU"


def _amd_temp_from_sensors() -> float | None:
    """Read AMD edge/junction temperature from sensors output."""
    sensors = run_command(["sensors"])
    for line in sensors.splitlines():
        stripped = line.strip().lower()
        if stripped.startswith("edge:") or stripped.startswith("junction:"):
            token = stripped.split()[1].replace("+", "").replace("°c", "")
            return _to_float(token)
    return None


def _detect_card_path(vendor_hex: str) -> Path | None:
    """Find DRM device path matching a vendor PCI ID."""
    matches: list[Path] = []
    for card in sorted(Path("/sys/class/drm").glob("card*/device")):
        vendor_file = card / "vendor"
        if vendor_file.exists():
            vendor = vendor_file.read_text(encoding="utf-8", errors="ignore").strip().lower()
            if vendor == vendor_hex:
                matches.append(card)
    if not matches:
        return None

    # Prefer the active boot VGA device when multiple cards are present.
    for card in matches:
        boot_vga = _read_int_file(card / "boot_vga")
        if boot_vga == 1:
            return card
    return matches[0]


def _read_int_file(path: Path) -> int | None:
    """Read an integer from a sysfs-style file path."""
    try:
        return int(path.read_text(encoding="utf-8", errors="ignore").strip())
    except (OSError, ValueError):
        return None


def _read_amd_stats(card_path: Path) -> tuple[float | None, int | None, int | None, float | None, int | None]:
    """Read utilization, VRAM, power, and fan values for AMD GPUs."""
    util = vram_used = vram_total = power = fan = None
    busy = _read_int_file(card_path / "gpu_busy_percent")
    if busy is not None:
        util = float(busy)

    used_bytes = _read_int_file(card_path / "mem_info_vram_used")
    total_bytes = _read_int_file(card_path / "mem_info_vram_total")
    if used_bytes is not None:
        vram_used = int(used_bytes / 1024 / 1024)
    if total_bytes is not None:
        vram_total = int(total_bytes / 1024 / 1024)

    hwmons = sorted((card_path / "hwmon").glob("hwmon*"))
    if hwmons:
        hwmon = hwmons[0]
        power_uw = _read_int_file(hwmon / "power1_average")
        if power_uw is not None:
            power = round(power_uw / 1_000_000.0, 1)
        fan_val = _read_int_file(hwmon / "fan1_input")
        if fan_val is not None:
            fan = fan_val

    return util, vram_used, vram_total, power, fan


def _read_intel_stats(card_path: Path) -> tuple[float | None, float | None]:
    """Read available utilization and temperature values for Intel GPUs."""
    util = None
    temp = None
    busy = _read_int_file(card_path / "gpu_busy_percent")
    if busy is not None:
        util = float(busy)

    hwmons = sorted((card_path / "hwmon").glob("hwmon*"))
    if hwmons:
        t_milli = _read_int_file(hwmons[0] / "temp1_input")
        if t_milli is not None:
            temp = round(t_milli / 1000.0, 1)
    return util, temp


def _parse_nvidia_smi_rows(output: str) -> list[list[str]]:
    """Parse nvidia-smi CSV output into normalized row columns."""
    rows = []
    for raw_row in csv.reader(output.splitlines()):
        row = [part.strip() for part in raw_row]
        if row:
            rows.append(row)
    return rows


def _normalized(text: str) -> str:
    """Normalize text for tolerant model matching."""
    return "".join(ch.lower() for ch in text if ch.isalnum())


def _pick_nvidia_row(rows: list[list[str]], detected_model: str) -> list[str] | None:
    """Select the best NVIDIA row for hosts with multiple GPUs."""
    valid_rows = [row for row in rows if len(row) >= 7]
    if not valid_rows:
        return None

    model_key = _normalized(detected_model)
    if model_key and "unknowngpu" not in model_key:
        for row in valid_rows:
            if model_key in _normalized(row[0]) or _normalized(row[0]) in model_key:
                return row

    # Fallback: prefer the row with highest VRAM total, then highest utilization.
    def score(row: list[str]) -> tuple[int, float]:
        return (_to_int(row[4]) or -1, _to_float(row[1]) or -1.0)

    return max(valid_rows, key=score)


def collect_gpu() -> GpuData:
    """Collect GPU model and telemetry with vendor-specific paths."""
    vendor, model = _vendor_from_lspci()
    util = temp = power = None
    vram_used = vram_total = fan = None

    if vendor == "nvidia" and command_exists("nvidia-smi"):
        query = run_command(
            [
                "nvidia-smi",
                "--query-gpu=name,utilization.gpu,temperature.gpu,memory.used,memory.total,power.draw,fan.speed",
                "--format=csv,noheader,nounits",
            ]
        )
        if query:
            selected = _pick_nvidia_row(_parse_nvidia_smi_rows(query), model)
            if selected is not None:
                model = selected[0] or model
                util = _to_float(selected[1])
                temp = _to_float(selected[2])
                vram_used = _to_int(selected[3])
                vram_total = _to_int(selected[4])
                power = _to_float(selected[5])
                fan = _to_int(selected[6])
    elif vendor == "amd":
        temp = _amd_temp_from_sensors()
        card_path = _detect_card_path("0x1002")
        if card_path is not None:
            util, vram_used, vram_total, power, fan = _read_amd_stats(card_path)
    elif vendor == "intel":
        card_path = _detect_card_path("0x8086")
        if card_path is not None:
            util, temp = _read_intel_stats(card_path)

    return GpuData(
        vendor=vendor,
        model=model,
        utilization_percent=util,
        temperature_c=temp,
        vram_used_mb=vram_used,
        vram_total_mb=vram_total,
        power_watts=power,
        fan_rpm=None if fan == 0 else fan,
    )
