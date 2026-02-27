from __future__ import annotations

from pathlib import Path

import sysmatrix.collectors.gpu as gpu_mod
import sysmatrix.collectors.network as network_mod
import sysmatrix.collectors.storage as storage_mod


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "collectors"


def _fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_gpu_vendor_detects_amd_from_lspci(monkeypatch) -> None:
    monkeypatch.setattr(gpu_mod, "run_command", lambda _args: _fixture("lspci_amd.txt"))
    vendor, model = gpu_mod._vendor_from_lspci()
    assert vendor == "amd"
    assert "Navi 22" in model


def test_gpu_amd_temp_parses_from_sensors(monkeypatch) -> None:
    monkeypatch.setattr(gpu_mod, "run_command", lambda _args: _fixture("sensors_amd.txt"))
    assert gpu_mod._amd_temp_from_sensors() == 52.0


def test_gpu_collect_nvidia_selects_matching_model_row(monkeypatch) -> None:
    lspci = "01:00.0 VGA compatible controller: NVIDIA Corporation GA104 [GeForce RTX 3070]\n"
    smi = "\n".join(
        [
            "NVIDIA GeForce GTX 1650, 20, 45, 1200, 4096, 40.2, 50",
            "NVIDIA GeForce RTX 3070, 75, 65, 4300, 8192, 175.5, 60",
        ]
    )

    def fake_run(args: list[str]) -> str:
        if args[:1] == ["lspci"]:
            return lspci
        if args[:1] == ["nvidia-smi"]:
            return smi
        return ""

    monkeypatch.setattr(gpu_mod, "run_command", fake_run)
    monkeypatch.setattr(gpu_mod, "command_exists", lambda _name: True)

    gpu = gpu_mod.collect_gpu()
    assert gpu.vendor == "nvidia"
    assert gpu.model == "NVIDIA GeForce RTX 3070"
    assert gpu.vram_total_mb == 8192
    assert gpu.utilization_percent == 75.0


def test_gpu_collect_nvidia_fallback_prefers_highest_vram(monkeypatch) -> None:
    lspci = "00:02.0 VGA compatible controller: NVIDIA Corporation Unknown Device\n"
    smi = "\n".join(
        [
            "NVIDIA Tesla T4, 10, 50, 1000, 16384, 45.0, 40",
            "NVIDIA GeForce RTX 3060, 50, 60, 3200, 12288, 120.0, 55",
        ]
    )

    def fake_run(args: list[str]) -> str:
        if args[:1] == ["lspci"]:
            return lspci
        if args[:1] == ["nvidia-smi"]:
            return smi
        return ""

    monkeypatch.setattr(gpu_mod, "run_command", fake_run)
    monkeypatch.setattr(gpu_mod, "command_exists", lambda _name: True)

    gpu = gpu_mod.collect_gpu()
    assert gpu.model == "NVIDIA Tesla T4"
    assert gpu.vram_total_mb == 16384


def test_detect_card_path_prefers_boot_vga(tmp_path, monkeypatch) -> None:
    drm = tmp_path / "drm"
    card0 = drm / "card0" / "device"
    card1 = drm / "card1" / "device"
    card0.mkdir(parents=True)
    card1.mkdir(parents=True)
    (card0 / "vendor").write_text("0x1002", encoding="utf-8")
    (card1 / "vendor").write_text("0x1002", encoding="utf-8")
    (card0 / "boot_vga").write_text("0", encoding="utf-8")
    (card1 / "boot_vga").write_text("1", encoding="utf-8")

    monkeypatch.setattr(gpu_mod, "Path", lambda value: drm if value == "/sys/class/drm" else Path(value))
    selected = gpu_mod._detect_card_path("0x1002")
    assert selected == card1


def test_network_throughput_uses_elapsed_and_clamps_negative(tmp_path, monkeypatch) -> None:
    stats_dir = tmp_path / "sys" / "class" / "net" / "eth0" / "statistics"
    stats_dir.mkdir(parents=True)
    rx = stats_dir / "rx_bytes"
    tx = stats_dir / "tx_bytes"
    rx.write_text("2000", encoding="utf-8")
    tx.write_text("3000", encoding="utf-8")

    monkeypatch.setattr(network_mod, "Path", lambda value: tmp_path / value.lstrip("/"))
    perf = iter([10.0, 10.5])
    monkeypatch.setattr(network_mod.time, "perf_counter", lambda: next(perf))

    def _sleep(_seconds: float) -> None:
        rx.write_text("1000", encoding="utf-8")
        tx.write_text("1200", encoding="utf-8")

    monkeypatch.setattr(network_mod.time, "sleep", _sleep)
    assert network_mod._throughput("eth0") == "down 0.00 MB/s | up 0.00 MB/s (eth0)"


def test_network_throughput_calculates_rate_from_elapsed(tmp_path, monkeypatch) -> None:
    stats_dir = tmp_path / "sys" / "class" / "net" / "wlan0" / "statistics"
    stats_dir.mkdir(parents=True)
    rx = stats_dir / "rx_bytes"
    tx = stats_dir / "tx_bytes"
    rx.write_text("0", encoding="utf-8")
    tx.write_text("0", encoding="utf-8")

    monkeypatch.setattr(network_mod, "Path", lambda value: tmp_path / value.lstrip("/"))
    perf = iter([20.0, 20.5])
    monkeypatch.setattr(network_mod.time, "perf_counter", lambda: next(perf))

    def _sleep(_seconds: float) -> None:
        rx.write_text(str(1_048_576), encoding="utf-8")
        tx.write_text(str(524_288), encoding="utf-8")

    monkeypatch.setattr(network_mod.time, "sleep", _sleep)
    assert network_mod._throughput("wlan0") == "down 2.00 MB/s | up 1.00 MB/s (wlan0)"


def test_network_ip_prefers_non_loopback_hostname_address(monkeypatch) -> None:
    hostname_output = _fixture("hostname_I_multiple.txt")
    monkeypatch.setattr(network_mod, "run_command", lambda _args: hostname_output)
    assert network_mod._ip_address() == "10.42.0.23"


def test_network_ip_falls_back_to_ip_route_src(monkeypatch) -> None:
    route_output = _fixture("ip_route_get_1_src.txt")

    def fake_run(args: list[str]) -> str:
        if args[:2] == ["hostname", "-I"]:
            return ""
        if args[:4] == ["ip", "route", "get", "1"]:
            return route_output
        return ""

    monkeypatch.setattr(network_mod, "run_command", fake_run)
    assert network_mod._ip_address() == "10.42.0.23"


def test_network_ip_returns_na_when_no_hostname_or_route_src(monkeypatch) -> None:
    route_output = _fixture("ip_route_get_1_no_src.txt")

    def fake_run(args: list[str]) -> str:
        if args[:2] == ["hostname", "-I"]:
            return ""
        if args[:4] == ["ip", "route", "get", "1"]:
            return route_output
        return ""

    monkeypatch.setattr(network_mod, "run_command", fake_run)
    assert network_mod._ip_address() == "N/A"


def test_storage_temperature_and_wear_percentage_used(monkeypatch) -> None:
    fixture = _fixture("smartctl_nvme_percentage_used.txt")
    monkeypatch.setattr(storage_mod, "run_command", lambda _args: fixture)
    assert storage_mod._temperature_from_smart("nvme0n1") == 35.0
    assert storage_mod._wear_from_smart("nvme0n1") == 6


def test_storage_wear_remaining_life_fallback(monkeypatch) -> None:
    fixture = _fixture("smartctl_nvme_remaining_life.txt")
    monkeypatch.setattr(storage_mod, "run_command", lambda _args: fixture)
    assert storage_mod._wear_from_smart("nvme0n1") == 8


def test_storage_temperature_parses_sata_attribute_line(monkeypatch) -> None:
    fixture = _fixture("smartctl_sata_temperature_celsius.txt")
    monkeypatch.setattr(storage_mod, "run_command", lambda _args: fixture)
    assert storage_mod._temperature_from_smart("sda") == 35.0


def test_storage_wear_parses_media_wearout_indicator(monkeypatch) -> None:
    fixture = _fixture("smartctl_sata_media_wearout.txt")
    monkeypatch.setattr(storage_mod, "run_command", lambda _args: fixture)
    assert storage_mod._wear_from_smart("sda") == 6
