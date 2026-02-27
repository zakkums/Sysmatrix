"""Default model factories used when collectors fail gracefully."""

from __future__ import annotations

from sysmatrix.models import (
    CpuData,
    GpuData,
    MemoryData,
    MotherboardData,
    NetworkData,
    PerformanceData,
    StorageData,
    SystemData,
)


def default_system() -> SystemData:
    """Return conservative default values for system identity fields."""
    return SystemData(
        user="unknown",
        hostname="unknown",
        os="Unknown",
        kernel="unknown",
        arch="unknown",
        uptime="unknown",
        shell="unknown",
    )


def default_cpu() -> CpuData:
    """Return a safe fallback CPU snapshot."""
    return CpuData(model="Unknown CPU", cores=0, usage_percent=0.0)


def default_memory() -> MemoryData:
    """Return a safe fallback memory snapshot."""
    return MemoryData(
        total_gb=0.0,
        used_gb=0.0,
        usage_percent=0.0,
        swap_total_gb=0.0,
        swap_used_gb=0.0,
    )


def default_gpu() -> GpuData:
    """Return a safe fallback GPU snapshot."""
    return GpuData(
        vendor="unknown",
        model="Unknown GPU",
        utilization_percent=None,
        temperature_c=None,
        vram_used_mb=None,
        vram_total_mb=None,
        power_watts=None,
        fan_rpm=None,
    )


def default_storage() -> StorageData:
    """Return a safe fallback storage snapshot."""
    return StorageData(
        root_mount="/",
        device_type="Unknown",
        total_gb=0.0,
        used_gb=0.0,
        usage_percent=0.0,
        temperature_c=None,
        wear_percent=None,
    )


def default_motherboard() -> MotherboardData:
    """Return a safe fallback motherboard snapshot."""
    return MotherboardData(vendor="Unknown", model="Unknown", vrm_temp_c=None)


def default_network() -> NetworkData:
    """Return a safe fallback network snapshot."""
    return NetworkData(
        ip="N/A",
        interface="N/A",
        throughput="N/A",
        wifi_chipset="N/A",
        bluetooth_chipset="N/A",
    )


def default_performance() -> PerformanceData:
    """Return a safe fallback performance summary."""
    return PerformanceData(
        load_average="N/A",
        cpu_perf_score=None,
        thermal_headroom_c=None,
        thermal_status="N/A",
        bottleneck="None detected",
    )
