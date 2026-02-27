from __future__ import annotations

import logging

import sysmatrix.snapshot as snapshot_mod


def test_snapshot_survives_collector_failure(monkeypatch) -> None:
    def _boom():
        raise RuntimeError("collector failed")

    monkeypatch.setattr(snapshot_mod, "collect_cpu", _boom)
    snapshot = snapshot_mod.collect_snapshot()
    assert snapshot.cpu.model == "Unknown CPU"
    assert snapshot.cpu.cores == 0
    assert snapshot.cpu.usage_percent == 0.0


def test_snapshot_logs_collector_failure(monkeypatch, caplog) -> None:
    def _boom():
        raise RuntimeError("collector failed")

    monkeypatch.setattr(snapshot_mod, "collect_memory", _boom)
    with caplog.at_level(logging.WARNING, logger="sysmatrix.snapshot"):
        snapshot = snapshot_mod.collect_snapshot()
    assert snapshot.memory.used_gb == 0.0
    assert "collector '_boom' failed; using fallback 'default_memory'" in caplog.text
