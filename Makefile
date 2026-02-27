.PHONY: test unit integration compile smoke ci

unit:
	python3 -m pytest -q tests/unit

integration:
	python3 -m pytest -q tests/integration

test:
	python3 -m pytest -q tests/unit tests/integration

compile:
	python3 -m compileall src

smoke:
	./scripts/sysmatrix --version
	./scripts/sysmatrix --short --plain
	./scripts/sysmatrix --json >/dev/null

ci: compile test smoke
