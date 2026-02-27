"""Network interface, IP, throughput, and radio chipset collectors."""

from __future__ import annotations

import ipaddress
import time
from pathlib import Path

from sysmatrix.models import NetworkData
from sysmatrix.utils.commands import run_command


def _preferred_ip(text: str) -> str | None:
    """Pick a non-loopback IP, preferring IPv4 addresses."""
    ipv4_candidates: list[str] = []
    ipv6_candidates: list[str] = []
    for token in text.split():
        try:
            ip = ipaddress.ip_address(token)
        except ValueError:
            continue
        if ip.is_loopback or ip.is_link_local or ip.is_unspecified:
            continue
        if ip.version == 4:
            ipv4_candidates.append(token)
        else:
            ipv6_candidates.append(token)
    if ipv4_candidates:
        return ipv4_candidates[0]
    if ipv6_candidates:
        return ipv6_candidates[0]
    return None


def _active_interface() -> str:
    """Return the first active non-loopback interface, if any."""
    net_dir = Path("/sys/class/net")
    if not net_dir.exists():
        return "N/A"
    for iface in sorted(net_dir.iterdir()):
        if iface.name == "lo":
            continue
        state = iface / "operstate"
        if state.exists() and state.read_text(encoding="utf-8", errors="ignore").strip() == "up":
            return iface.name
    return "N/A"


def _ip_address() -> str:
    """Resolve primary host IP using hostname/ip route fallbacks."""
    output = run_command(["hostname", "-I"])
    preferred = _preferred_ip(output)
    if preferred:
        return preferred
    output = run_command(["ip", "route", "get", "1"])
    parts = output.split()
    if "src" in parts:
        idx = parts.index("src")
        if idx + 1 < len(parts):
            preferred = _preferred_ip(parts[idx + 1])
            if preferred:
                return preferred
    return "N/A"


def _throughput(interface: str) -> str:
    """Estimate RX/TX throughput from sysfs byte counters."""
    if interface == "N/A":
        return "N/A"
    rx_file = Path(f"/sys/class/net/{interface}/statistics/rx_bytes")
    tx_file = Path(f"/sys/class/net/{interface}/statistics/tx_bytes")
    if not rx_file.exists() or not tx_file.exists():
        return "N/A"
    try:
        rx1 = int(rx_file.read_text(encoding="utf-8", errors="ignore").strip())
        tx1 = int(tx_file.read_text(encoding="utf-8", errors="ignore").strip())
    except (OSError, ValueError):
        return "N/A"
    started = time.perf_counter()
    time.sleep(0.25)
    try:
        rx2 = int(rx_file.read_text(encoding="utf-8", errors="ignore").strip())
        tx2 = int(tx_file.read_text(encoding="utf-8", errors="ignore").strip())
    except (OSError, ValueError):
        return "N/A"
    elapsed = max(time.perf_counter() - started, 1e-6)
    rx_delta = max(rx2 - rx1, 0)
    tx_delta = max(tx2 - tx1, 0)
    rx_rate_mb = rx_delta / elapsed / 1024 / 1024
    tx_rate_mb = tx_delta / elapsed / 1024 / 1024
    return f"down {rx_rate_mb:.2f} MB/s | up {tx_rate_mb:.2f} MB/s ({interface})"


def _wifi_chipset() -> str:
    """Best-effort lookup of Wi-Fi chipset from PCI/USB inventory."""
    net_dir = Path("/sys/class/net")
    if not net_dir.exists():
        return "N/A"
    for iface in net_dir.iterdir():
        if (iface / "wireless").exists():
            line = run_command(["lspci"])
            for row in line.splitlines():
                lowered = row.lower()
                if any(tok in lowered for tok in ("network", "wireless", "wifi")):
                    return row.split(":", 2)[-1].strip()
            usb = run_command(["lsusb"])
            for row in usb.splitlines():
                lowered = row.lower()
                if any(tok in lowered for tok in ("wireless", "wifi", "wlan")):
                    return row.split(":", 2)[-1].strip()
    return "N/A"


def _bluetooth_chipset() -> str:
    """Best-effort lookup of Bluetooth controller from PCI/USB inventory."""
    bt_dir = Path("/sys/class/bluetooth")
    if not bt_dir.exists():
        return "N/A"
    pci = run_command(["lspci"])
    for row in pci.splitlines():
        if "bluetooth" in row.lower():
            return row.split(":", 2)[-1].strip()
    usb = run_command(["lsusb"])
    for row in usb.splitlines():
        if "bluetooth" in row.lower():
            return row.split(":", 2)[-1].strip()
    return "N/A"


def collect_network() -> NetworkData:
    """Collect network summary used by text and JSON renderers."""
    interface = _active_interface()
    return NetworkData(
        ip=_ip_address(),
        interface=interface,
        throughput=_throughput(interface),
        wifi_chipset=_wifi_chipset(),
        bluetooth_chipset=_bluetooth_chipset(),
    )
