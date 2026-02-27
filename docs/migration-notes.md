# Migration Notes

## Completed

- Replaced the monolithic shell implementation with a modular Python package.
- Added collector coverage for system, CPU, memory, GPU, storage, motherboard, network, and performance.
- Added renderers for full, short, JSON, and watch modes.
- Added Debian packaging metadata and CI-friendly validation checks.
- Hardened multi-GPU parsing/selection, fallback diagnostics, and network/storage parser edge cases.
- Added fixture-driven parser coverage for NVIDIA/SMART/network command variants.
- Rebranded CLI/package output from `sysinfo-cli` to `sysmatrix`.
- Validated Debian package build after dependency and metadata hardening.

## Current Focus

- Publish first tagged release using the documented process in `docs/release-process.md`.
