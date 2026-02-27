from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _run_sysmatrix(args: list[str]) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    return subprocess.run(
        [str(ROOT / "scripts" / "sysmatrix"), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )


def test_cli_short_mode() -> None:
    proc = _run_sysmatrix(["--short", "--plain"])
    assert proc.returncode == 0
    assert "CPU " in proc.stdout
    assert "RAM " in proc.stdout


def test_cli_json_mode() -> None:
    proc = _run_sysmatrix(["--json"])
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert "system" in payload
    assert "performance" in payload


def test_cli_opsec_redacts_user_and_ip() -> None:
    proc = _run_sysmatrix(["--json", "--opsec"])
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload["system"]["user"] == "[REDACTED]"
    assert payload["network"]["ip"] == "[REDACTED]"


def test_cli_version() -> None:
    proc = _run_sysmatrix(["--version"])
    assert proc.returncode == 0
    assert proc.stdout.startswith("sysmatrix ")


def test_cli_rejects_invalid_watch_interval() -> None:
    proc = _run_sysmatrix(["--watch", "0"])
    assert proc.returncode != 0
    assert "watch interval must be >= 1 second" in proc.stderr
