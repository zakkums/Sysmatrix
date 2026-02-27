# Architecture

`sysmatrix` is structured around one core rule: collection, modeling, and
rendering are separate concerns.

## Navigation

- Docs index: [`README.md`](README.md)
- Package root: [`../src/sysmatrix/`](../src/sysmatrix)
- Tests: [`../tests/`](../tests)

## Layers

- `collectors/`: read data from the system (`/proc`, `/sys`, shell tools)
- `models.py`: typed snapshot objects shared across the app
- `snapshot.py`: orchestration and resilience fallbacks per collector
- `renderers/`: output formatting for full, short, JSON, and watch modes
- `cli.py`: argument parsing and runtime mode selection

## Key Files

- CLI runtime routing: [`../src/sysmatrix/cli.py`](../src/sysmatrix/cli.py)
- Snapshot orchestration: [`../src/sysmatrix/snapshot.py`](../src/sysmatrix/snapshot.py)
- Data models: [`../src/sysmatrix/models.py`](../src/sysmatrix/models.py)
- Collector modules: [`../src/sysmatrix/collectors/`](../src/sysmatrix/collectors)
- Output renderers: [`../src/sysmatrix/renderers/`](../src/sysmatrix/renderers)
- Command/format helpers: [`../src/sysmatrix/utils/`](../src/sysmatrix/utils)

## Design Notes

- Collectors should fail gracefully and return partial data where possible.
- Renderers should avoid embedding collection logic.
- JSON output should remain stable and backwards-friendly for scripts.
