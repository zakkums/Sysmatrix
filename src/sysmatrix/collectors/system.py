"""System identity and environment metadata collectors."""

from __future__ import annotations

import getpass
import os
import platform
import socket
from pathlib import Path

from sysmatrix.models import SystemData
from sysmatrix.utils.commands import run_command


def _read_os_name() -> str:
    """Read a friendly OS name, preferring /etc/os-release."""
    os_release = Path("/etc/os-release")
    if os_release.exists():
        for line in os_release.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.startswith("PRETTY_NAME="):
                return line.split("=", 1)[1].strip().strip('"')
    return platform.platform()


def _read_uptime() -> str:
    """Read human-readable uptime from the host."""
    data = run_command(["uptime", "-p"])
    return data.replace("up ", "", 1) if data else "unknown"


def collect_system() -> SystemData:
    """Collect baseline system metadata for display and JSON output."""
    return SystemData(
        user=getpass.getuser(),
        hostname=socket.gethostname(),
        os=_read_os_name(),
        kernel=platform.release(),
        arch=platform.machine(),
        uptime=_read_uptime(),
        shell=os.path.basename(os.environ.get("SHELL", "unknown")),
    )
