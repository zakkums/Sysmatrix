# Contributing

Thanks for contributing to `sysmatrix`.

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Before Opening a PR

Run the same checks used in CI:

```bash
python3 -m compileall src
python3 -m pytest -q tests/unit tests/integration
./scripts/sysmatrix --version
```

## Coding Guidelines

- Keep collectors defensive: best-effort data is better than a hard failure.
- Add or update tests when parser behavior changes.
- Keep output behavior stable for `--short`, `--json`, `--opsec`, and `--watch`.
- Prefer additive schema changes over breaking JSON field removals/renames.
- Keep comments practical and concise; explain non-obvious logic only.

## Debian Packaging Check

Install required Debian build dependencies first:

```bash
sudo apt-get update
sudo apt-get install -y debhelper dh-python pybuild-plugin-pyproject python3-all python3-setuptools
```

Then run:

```bash
dpkg-buildpackage -us -uc -b
```
