# Collector Matrix

| Domain      | Status      | Notes |
|-------------|-------------|-------|
| System      | Implemented | OS, kernel, shell, uptime, host/user |
| CPU         | Implemented | Model, cores, usage sampling |
| Memory      | Implemented | RAM and swap totals/usage |
| GPU         | Implemented | NVIDIA and AMD/Intel fallback paths |
| Storage     | Implemented | Disk usage, SMART and hwmon fallbacks |
| Motherboard | Implemented | DMI board info and VRM temp attempts |
| Network     | Implemented | Interface/IP/throughput + wifi/bluetooth |
| Performance | Implemented | Load average, thermal status, bottleneck hint |
