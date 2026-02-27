"""Collector exports for snapshot assembly."""

from sysmatrix.collectors.cpu import collect_cpu
from sysmatrix.collectors.gpu import collect_gpu
from sysmatrix.collectors.memory import collect_memory
from sysmatrix.collectors.motherboard import collect_motherboard
from sysmatrix.collectors.network import collect_network
from sysmatrix.collectors.performance import collect_performance
from sysmatrix.collectors.storage import collect_storage
from sysmatrix.collectors.system import collect_system

__all__ = [
    "collect_system",
    "collect_cpu",
    "collect_memory",
    "collect_gpu",
    "collect_storage",
    "collect_motherboard",
    "collect_network",
    "collect_performance",
]
