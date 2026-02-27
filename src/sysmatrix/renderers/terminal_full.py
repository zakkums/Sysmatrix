"""Full terminal renderer for human-readable diagnostics output."""

from __future__ import annotations

from sysmatrix.config import RuntimeConfig
from sysmatrix.models import Snapshot
from sysmatrix.utils.formatting import color_usage, maybe_redact


def render_full(snapshot: Snapshot, config: RuntimeConfig) -> str:
    """Render the complete multi-section terminal report."""
    system = snapshot.system
    cpu = snapshot.cpu
    gpu = snapshot.gpu
    mem = snapshot.memory
    storage = snapshot.storage
    motherboard = snapshot.motherboard
    network = snapshot.network
    perf = snapshot.performance

    user = maybe_redact(system.user, config.opsec)
    host = maybe_redact(system.hostname, config.opsec)

    lines = [
        "SYSTEM INFORMATION",
        f"Host: {host} | User: {user}",
        f"OS: {system.os}",
        f"Kernel: {system.kernel} | Arch: {system.arch}",
        f"Uptime: {system.uptime} | Shell: {system.shell}",
        f"Motherboard: {motherboard.vendor} {motherboard.model}",
        (
            "VRM Temp: "
            + ("N/A" if motherboard.vrm_temp_c is None else f"{motherboard.vrm_temp_c:.1f} C")
        ),
        "",
        "RESOURCES",
        f"CPU: {cpu.model}",
        f"Cores: {cpu.cores} | Usage: {color_usage(cpu.usage_percent, config.plain)}",
        (
            f"GPU: {gpu.model} ({gpu.vendor}) | Usage: "
            + ("N/A" if gpu.utilization_percent is None else color_usage(gpu.utilization_percent, config.plain))
        ),
        (
            "GPU Temp: "
            + ("N/A" if gpu.temperature_c is None else f"{gpu.temperature_c:.1f} C")
            + " | VRAM: "
            + (
                "N/A"
                if gpu.vram_used_mb is None or gpu.vram_total_mb is None
                else f"{gpu.vram_used_mb}/{gpu.vram_total_mb} MB"
            )
        ),
        (
            f"RAM: {mem.used_gb:.1f}/{mem.total_gb:.1f} GiB "
            f"({color_usage(mem.usage_percent, config.plain)})"
        ),
        f"Swap: {mem.swap_used_gb:.1f}/{mem.swap_total_gb:.1f} GiB",
        "",
        "STORAGE",
        (
            f"Root: {storage.root_mount} | Type: {storage.device_type} | Used: "
            f"{storage.used_gb:.1f}/{storage.total_gb:.1f} GiB "
            f"({color_usage(storage.usage_percent, config.plain)})"
        ),
        (
            "Disk Temp: "
            + ("N/A" if storage.temperature_c is None else f"{storage.temperature_c:.1f} C")
            + " | Wear: "
            + ("N/A" if storage.wear_percent is None else f"{storage.wear_percent}%")
        ),
        "",
        "NETWORK",
        f"IP: {maybe_redact(network.ip, config.opsec)} | Interface: {network.interface}",
        f"Throughput: {network.throughput}",
        f"Wi-Fi: {network.wifi_chipset} | Bluetooth: {network.bluetooth_chipset}",
        "",
        "PERFORMANCE",
        f"Load Average: {perf.load_average}",
        "CPU Perf: "
        + ("N/A" if perf.cpu_perf_score is None else f"{perf.cpu_perf_score:.1f}%")
        + " | Thermal: "
        + (
            "N/A"
            if perf.thermal_headroom_c is None
            else f"{perf.thermal_headroom_c:.1f} C headroom ({perf.thermal_status})"
        ),
        f"Bottleneck: {perf.bottleneck}",
    ]
    return "\n".join(lines)
