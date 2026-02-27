# Sysmatrix Migration Progress

Navigation: [`README.md`](README.md) | [`docs index`](docs/README.md) | [`release checklist`](docs/release-process.md)

## Snapshot
- Date: 2026-02-27
- Scope: Documentation polish and production hardening
- Status: Active development

## Completed
- [x] Modular Python package established under `src/sysmatrix/`
- [x] Public command renamed to `sysmatrix`
- [x] Core collectors implemented: system, cpu, memory, gpu, storage, motherboard, network, performance
- [x] Output modes implemented: full, short, JSON, watch
- [x] Snapshot collection made fault-tolerant with collector fallbacks
- [x] CLI validation added for `--watch` interval and `--version`
- [x] Debian packaging metadata added under top-level `debian/`
- [x] Repository standards added: `.gitignore`, `LICENSE`, `CONTRIBUTING.md`, `Makefile`, CI workflow
- [x] Legacy script and backup artifacts removed
- [x] Test suite expanded with renderer, integration, resilience, and parser fixture coverage
- [x] Collector fallback and command execution diagnostics improved with logging
- [x] Network throughput calculation hardened for counter resets and elapsed-time accuracy
- [x] Additional parser fixtures and tests added for storage/network command variants
- [x] Release process documented under `docs/release-process.md`

## In Progress
- [ ] Publish first package release using documented checklist

## Next Actions (Priority Order)
- [x] Improve multi-GPU host selection and sensor edge-case handling
- [x] Validate Debian package build in an environment with required build dependencies
- [ ] Publish first package release using documented checklist

## Done Definition For Milestone 1
- [x] `sysmatrix` command runs from Python implementation.
- [x] Full/short/JSON/watch modes produce stable output
- [x] Unit and integration tests cover core rendering and CLI paths
- [x] Debian package builds cleanly in a dependency-complete environment

## Notes
- Build dependencies for Debian packaging are environment-specific and may need manual installation.
- Local build checks attempted on 2026-02-27:
  - First failure: missing `debhelper-compat (= 13)`, `python3-all`.
  - After metadata hardening, packaging requires `pybuild-plugin-pyproject` (added to `debian/control`).
- Debian package build now succeeds for `sysmatrix` after installing required build dependencies.

