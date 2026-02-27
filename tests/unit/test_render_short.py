from sysmatrix.config import RuntimeConfig
from sysmatrix.models import (
    CpuData,
    GpuData,
    MemoryData,
    MotherboardData,
    NetworkData,
    PerformanceData,
    Snapshot,
    StorageData,
    SystemData,
)
from sysmatrix.renderers.terminal_short import render_short


def test_short_output_includes_gpu() -> None:
    snapshot = Snapshot(
        system=SystemData(
            user="alice",
            hostname="devbox",
            os="Debian",
            kernel="6.x",
            arch="x86_64",
            uptime="1 hour",
            shell="bash",
        ),
        cpu=CpuData(model="cpu", cores=8, usage_percent=10.0),
        memory=MemoryData(
            total_gb=16.0,
            used_gb=4.0,
            usage_percent=25.0,
            swap_total_gb=2.0,
            swap_used_gb=0.0,
        ),
        gpu=GpuData(
            vendor="amd",
            model="gpu",
            utilization_percent=42.0,
            temperature_c=55.0,
            vram_used_mb=1024,
            vram_total_mb=8192,
            power_watts=100.0,
            fan_rpm=1200,
        ),
        storage=StorageData(
            root_mount="/",
            device_type="NVMe SSD",
            total_gb=1000.0,
            used_gb=200.0,
            usage_percent=20.0,
            temperature_c=34.0,
            wear_percent=4,
        ),
        motherboard=MotherboardData(vendor="ASUS", model="B550", vrm_temp_c=41.0),
        network=NetworkData(
            ip="192.168.1.10",
            interface="enp0s31f6",
            throughput="down 0.01 MB/s | up 0.01 MB/s (enp0s31f6)",
            wifi_chipset="N/A",
            bluetooth_chipset="N/A",
        ),
        performance=PerformanceData(
            load_average="0.01, 0.05, 0.10",
            cpu_perf_score=75.0,
            thermal_headroom_c=35.0,
            thermal_status="OK",
            bottleneck="None detected",
        ),
    )
    out = render_short(snapshot, RuntimeConfig(plain=True, short=True))
    assert "CPU " in out
    assert "GPU " in out
    assert "RAM " in out
