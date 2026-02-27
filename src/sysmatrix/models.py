"""Typed data models shared across collectors and renderers."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class SystemData:
    """Basic host and runtime identity data."""
    user: str
    hostname: str
    os: str
    kernel: str
    arch: str
    uptime: str
    shell: str


@dataclass
class CpuData:
    """CPU model and utilization fields."""
    model: str
    cores: int
    usage_percent: float


@dataclass
class MemoryData:
    """Memory and swap capacity/usage fields."""
    total_gb: float
    used_gb: float
    usage_percent: float
    swap_total_gb: float
    swap_used_gb: float


@dataclass
class GpuData:
    """GPU identity and telemetry fields."""
    vendor: str
    model: str
    utilization_percent: float | None
    temperature_c: float | None
    vram_used_mb: int | None
    vram_total_mb: int | None
    power_watts: float | None
    fan_rpm: int | None


@dataclass
class StorageData:
    """Storage capacity and health fields."""
    root_mount: str
    device_type: str
    total_gb: float
    used_gb: float
    usage_percent: float
    temperature_c: float | None
    wear_percent: int | None


@dataclass
class MotherboardData:
    """Motherboard identity and VRM telemetry."""
    vendor: str
    model: str
    vrm_temp_c: float | None


@dataclass
class NetworkData:
    """Network state and adapter metadata."""
    ip: str
    interface: str
    throughput: str
    wifi_chipset: str
    bluetooth_chipset: str


@dataclass
class PerformanceData:
    """Derived performance metrics and heuristics."""
    load_average: str
    cpu_perf_score: float | None
    thermal_headroom_c: float | None
    thermal_status: str
    bottleneck: str


@dataclass
class Snapshot:
    """Top-level aggregate snapshot of all domains."""
    system: SystemData
    cpu: CpuData
    memory: MemoryData
    gpu: GpuData
    storage: StorageData
    motherboard: MotherboardData
    network: NetworkData
    performance: PerformanceData

    def to_dict(self) -> dict:
        """Serialize snapshot dataclasses to nested dictionaries."""
        return asdict(self)
