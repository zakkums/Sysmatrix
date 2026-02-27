# sysmatrix

`sysmatrix` is a modular system diagnostics tool for Linux, with a focus on
clear terminal output, script-friendly JSON output, and Debian package support.

## Features

- Multi-domain system snapshot (system, CPU, GPU, memory, storage, network, performance)
- Output modes: `--short`, full view, `--json`, and `--watch`
- Privacy mode: `--opsec` redacts user/host/IP fields
- Fault-tolerant collection: partial failures degrade gracefully instead of crashing

## Quick Start

Run directly from the repository:

```bash
./scripts/sysmatrix --help
./scripts/sysmatrix --short
```

Run from source during development without installation:

```bash
PYTHONPATH=src ./scripts/sysmatrix --json
```

Install locally in editable mode:

```bash
pip install -e .
sysmatrix --version
```

## Development Checks

```bash
python3 -m compileall src
python3 -m pytest -q tests/unit tests/integration
./scripts/sysmatrix --version
./scripts/sysmatrix --json >/dev/null
```

## Debian Build

Install required build dependencies:

```bash
sudo apt-get update
sudo apt-get install -y debhelper dh-python pybuild-plugin-pyproject python3-all python3-setuptools
```

Build package:

```bash
dpkg-buildpackage -us -uc -b
```

See `docs/release-process.md` for full release steps and checklist.
