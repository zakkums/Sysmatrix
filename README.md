# sysmatrix

`sysmatrix` is a modular system diagnostics tool for Linux, with a focus on
clear terminal output, script-friendly JSON output, and Debian package support.

## Documentation Navigation

- Project docs index: [`docs/README.md`](docs/README.md)
- Contribution guide: [`CONTRIBUTING.md`](CONTRIBUTING.md)
- Architecture notes: [`docs/architecture.md`](docs/architecture.md)
- Collector coverage: [`docs/collector-matrix.md`](docs/collector-matrix.md)
- Release checklist: [`docs/release-process.md`](docs/release-process.md)
- Source package: [`src/sysmatrix/`](src/sysmatrix)
- Tests: [`tests/`](tests)
- Debian packaging metadata: [`debian/`](debian)

## Features

- Multi-domain system snapshot (system, CPU, GPU, memory, storage, network, performance)
- Output modes: full view, `--short`, `--json`, and `--watch`
- Output toggles: `--plain` (disable colors), `--opsec` (redact sensitive values)
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

## CLI Quick Reference

```bash
sysmatrix --help
sysmatrix --short --plain
sysmatrix --json
sysmatrix --watch 2
sysmatrix --opsec
```

- `--short` / `-s`: minimal terminal output
- `--plain` / `-p`: disable color escape codes
- `--json` / `-j`: JSON output for scripting/automation
- `--watch [N]` / `-w [N]`: refresh every `N` seconds (default `1`)
- `--opsec` / `-o`: redact user/host/IP-style fields
- `--logo`: compatibility flag (`debian`, `corsair`, `minimal`, `none`)

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
