"""Command-line entrypoints and argument handling for sysmatrix."""

from __future__ import annotations

import argparse
from importlib.metadata import PackageNotFoundError, version

from sysmatrix.config import RuntimeConfig
from sysmatrix import __version__
from sysmatrix.renderers.json_output import render_json
from sysmatrix.renderers.terminal_full import render_full
from sysmatrix.renderers.terminal_short import render_short
from sysmatrix.renderers.watch import run_watch
from sysmatrix.snapshot import collect_snapshot


def build_parser() -> argparse.ArgumentParser:
    """Build and return the top-level argument parser."""
    parser = argparse.ArgumentParser(
        prog="sysmatrix",
        description="Modular system information and diagnostics tool.",
    )
    parser.add_argument("--short", "-s", action="store_true", help="Minimal output")
    parser.add_argument("--plain", "-p", action="store_true", help="Disable colors")
    parser.add_argument("--opsec", "-o", action="store_true", help="Redact sensitive fields")
    parser.add_argument("--json", "-j", action="store_true", help="Output JSON")
    parser.add_argument(
        "--watch",
        "-w",
        nargs="?",
        const=1,
        type=int,
        help="Refresh output every N seconds (default: 1)",
    )
    parser.add_argument(
        "--logo",
        default="debian",
        choices=["debian", "corsair", "minimal", "none"],
        help="Reserved for output compatibility",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_runtime_version()}",
    )
    return parser


def _runtime_version() -> str:
    """Resolve installed package version, with source-tree fallback."""
    try:
        return version("sysmatrix")
    except PackageNotFoundError:
        return __version__


def _config_from_args(args: argparse.Namespace) -> RuntimeConfig:
    """Convert parsed CLI arguments into runtime configuration."""
    interval = args.watch if args.watch is not None else 1
    if interval < 1:
        raise ValueError("watch interval must be >= 1 second")
    return RuntimeConfig(
        short=args.short,
        plain=args.plain or args.json,
        opsec=args.opsec,
        json=args.json,
        watch=args.watch is not None,
        watch_interval=interval,
        logo=args.logo,
    )


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        config = _config_from_args(args)
    except ValueError as exc:
        parser.error(str(exc))
        return 2

    if config.watch:
        return run_watch(config)

    snapshot = collect_snapshot()
    if config.json:
        print(render_json(snapshot, config))
    elif config.short:
        print(render_short(snapshot, config))
    else:
        print(render_full(snapshot, config))
    return 0
