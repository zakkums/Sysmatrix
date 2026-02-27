# Release Process

This document defines the minimum steps to cut a new `sysmatrix` release and verify Debian packaging output.

Navigation: [`docs index`](README.md) | [`project README`](../README.md) | [`debian metadata`](../debian)

## Prerequisites

Install release/build dependencies:

```bash
sudo apt-get update
sudo apt-get install -y debhelper dh-python pybuild-plugin-pyproject python3-all python3-setuptools devscripts
```

Ensure a clean working tree and passing local checks:

```bash
python3 -m compileall src
python3 -m pytest -q tests/unit tests/integration
./scripts/sysmatrix --version
./scripts/sysmatrix --short --plain
./scripts/sysmatrix --json >/dev/null
```

## Version Update

1. Update `version` in `pyproject.toml`.
2. Add a new top entry in `debian/changelog` with the Debian package version.
3. Document key user-facing changes in `README.md` as needed.

## Debian Package Validation

Run package build:

```bash
dpkg-buildpackage -us -uc -b
```

Expected result:
- A successful build exits with status `0`.
- Package artifacts (`.deb`, `.changes`, `.buildinfo`) are generated one directory above the repository root.

If build dependencies are missing, `dpkg-checkbuilddeps` reports which packages must be installed.

## Final Release Checklist

- [ ] Tests and compile checks pass.
- [ ] `pyproject.toml` and `debian/changelog` versions are updated.
- [ ] `dpkg-buildpackage -us -uc -b` succeeds in a dependency-complete environment.
- [ ] Release notes/docs updated for any behavior or CLI changes.
