# Architecture

`sysmatrix` is structured around one core rule: collection, modeling, and
rendering are separate concerns.

## Layers

- `collectors/`: read data from the system (`/proc`, `/sys`, shell tools)
- `models.py`: typed snapshot objects shared across the app
- `snapshot.py`: orchestration and resilience fallbacks per collector
- `renderers/`: output formatting for full, short, JSON, and watch modes
- `cli.py`: argument parsing and runtime mode selection

## Design Notes

- Collectors should fail gracefully and return partial data where possible.
- Renderers should avoid embedding collection logic.
- JSON output should remain stable and backwards-friendly for scripts.
