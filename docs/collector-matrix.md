# Collector Matrix

Navigation: [`docs index`](README.md) | [`collectors directory`](../src/sysmatrix/collectors)

| Domain      | Status      | Notes | Source |
|-------------|-------------|-------|--------|
| System      | Implemented | OS, kernel, shell, uptime, host/user | [`system.py`](../src/sysmatrix/collectors/system.py) |
| CPU         | Implemented | Model, cores, usage sampling | [`cpu.py`](../src/sysmatrix/collectors/cpu.py) |
| Memory      | Implemented | RAM and swap totals/usage | [`memory.py`](../src/sysmatrix/collectors/memory.py) |
| GPU         | Implemented | NVIDIA and AMD/Intel fallback paths | [`gpu.py`](../src/sysmatrix/collectors/gpu.py) |
| Storage     | Implemented | Disk usage, SMART and hwmon fallbacks | [`storage.py`](../src/sysmatrix/collectors/storage.py) |
| Motherboard | Implemented | DMI board info and VRM temp attempts | [`motherboard.py`](../src/sysmatrix/collectors/motherboard.py) |
| Network     | Implemented | Interface/IP/throughput + wifi/bluetooth | [`network.py`](../src/sysmatrix/collectors/network.py) |
| Performance | Implemented | Load average, thermal status, bottleneck hint | [`performance.py`](../src/sysmatrix/collectors/performance.py) |
