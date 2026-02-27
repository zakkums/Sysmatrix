"""Snapshot orchestration with per-collector fail-safe fallbacks."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import TypeVar

from sysmatrix.collectors import (
    collect_cpu,
    collect_gpu,
    collect_memory,
    collect_motherboard,
    collect_network,
    collect_performance,
    collect_storage,
    collect_system,
)
from sysmatrix.defaults import (
    default_cpu,
    default_gpu,
    default_memory,
    default_motherboard,
    default_network,
    default_performance,
    default_storage,
    default_system,
)
from sysmatrix.models import Snapshot

T = TypeVar("T")
LOGGER = logging.getLogger(__name__)


def _callable_name(func: Callable[..., object]) -> str:
    """Return a readable callable name for diagnostics."""
    return getattr(func, "__name__", func.__class__.__name__)


def _safe_collect(collector: Callable[[], T], fallback: Callable[[], T]) -> T:
    """Run a collector and return fallback data on any exception."""
    try:
        return collector()
    except Exception:  # pragma: no cover - branch behavior validated via caplog tests
        LOGGER.warning(
            "collector '%s' failed; using fallback '%s'",
            _callable_name(collector),
            _callable_name(fallback),
            exc_info=True,
        )
        return fallback()


def collect_snapshot() -> Snapshot:
    """Collect a full system snapshot across all collector domains."""
    system = _safe_collect(collect_system, default_system)
    cpu = _safe_collect(collect_cpu, default_cpu)
    memory = _safe_collect(collect_memory, default_memory)
    gpu = _safe_collect(collect_gpu, default_gpu)
    storage = _safe_collect(collect_storage, default_storage)
    motherboard = _safe_collect(collect_motherboard, default_motherboard)
    network = _safe_collect(collect_network, default_network)
    performance = _safe_collect(
        lambda: collect_performance(cpu_usage=cpu.usage_percent, gpu_usage=gpu.utilization_percent),
        default_performance,
    )
    return Snapshot(
        system=system,
        cpu=cpu,
        memory=memory,
        gpu=gpu,
        storage=storage,
        motherboard=motherboard,
        network=network,
        performance=performance,
    )
