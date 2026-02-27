# sysmatrix Project Overview

## Objective

Build a production-ready, modular system diagnostics CLI with:

- stable terminal and JSON output modes
- resilient collectors with graceful fallback behavior
- repeatable Debian package build support

## Repository Layout

```text
sysmatrix/
├─ src/
│  └─ sysmatrix/
│     ├─ __init__.py
│     ├─ __main__.py                 # python -m sysmatrix entry
│     ├─ cli.py                      # argparse entrypoint and mode routing
│     ├─ config.py                   # runtime defaults
│     ├─ models.py                   # dataclasses for system snapshot
│     ├─ defaults.py                 # fallback values for resilience
│     ├─ snapshot.py                 # collector orchestration with fail-safe fallbacks
│     ├─ collectors/
│     │  ├─ __init__.py
│     │  ├─ base.py                  # optional base collector helpers
│     │  ├─ system.py                # host/os/kernel/desktop/display
│     │  ├─ cpu.py
│     │  ├─ gpu.py
│     │  ├─ memory.py
│     │  ├─ storage.py
│     │  ├─ motherboard.py
│     │  ├─ network.py
│     │  └─ performance.py           # bottleneck/headroom scoring
│     ├─ renderers/
│     │  ├─ __init__.py
│     │  ├─ terminal_full.py
│     │  ├─ terminal_short.py
│     │  ├─ json_output.py
│     │  └─ watch.py
│     └─ utils/
│        ├─ __init__.py
│        ├─ commands.py              # subprocess helpers + command availability
│        └─ formatting.py            # units, colors, redaction
├─ scripts/
│  └─ sysmatrix                      # primary launcher
├─ tests/
│  ├─ unit/
│  │  ├─ test_collectors_parsing.py
│  │  ├─ test_render_json.py
│  │  ├─ test_render_short.py
│  │  └─ test_snapshot_resilience.py
│  ├─ fixtures/collectors/
│  └─ integration/
│     └─ test_cli_modes.py
├─ .github/workflows/
│  └─ ci.yml
├─ debian/
│  ├─ control
│  ├─ rules
│  ├─ changelog
│  ├─ install
│  ├─ copyright
│  └─ source/format
├─ docs/
│  ├─ architecture.md
│  ├─ collector-matrix.md
│  ├─ migration-notes.md
│  └─ release-process.md
├─ pyproject.toml
├─ README.md
├─ CONTRIBUTING.md
├─ LICENSE
├─ Makefile
├─ info.md
└─ progress.md
```

## Module Responsibilities

- `src/sysmatrix/collectors/*`: hardware and platform data collection
- `src/sysmatrix/models.py`: typed snapshot schema
- `src/sysmatrix/snapshot.py`: collector orchestration + fallback handling
- `src/sysmatrix/renderers/*`: full/short/JSON/watch output formatting
- `src/sysmatrix/cli.py`: argument parsing, mode routing, CLI UX
- `src/sysmatrix/utils/*`: command execution and formatting helpers

## Packaging Direction

- Primary command name: `sysmatrix`
- Python entrypoint from `pyproject.toml`
- Debian metadata under top-level `debian/`

## Quality Baseline

- Unit tests for renderer output, parser behavior, and snapshot resilience
- Integration tests for CLI mode paths
- Compile checks (`python3 -m compileall src`)
- CI workflow for automated validation on push and pull request
