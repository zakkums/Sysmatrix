"""Live refresh renderer loop for watch mode."""

from __future__ import annotations

import time

from sysmatrix.config import RuntimeConfig
from sysmatrix.renderers.json_output import render_json
from sysmatrix.renderers.terminal_full import render_full
from sysmatrix.renderers.terminal_short import render_short
from sysmatrix.snapshot import collect_snapshot


def run_watch(config: RuntimeConfig) -> int:
    """Continuously redraw output until interrupted by the user."""
    try:
        while True:
            snapshot = collect_snapshot()
            print("\033[2J\033[H", end="")
            if config.json:
                print(render_json(snapshot, config))
            elif config.short:
                print(render_short(snapshot, config))
            else:
                print(render_full(snapshot, config))
            print(f"\nRefreshing every {config.watch_interval}s. Press Ctrl+C to exit.")
            time.sleep(config.watch_interval)
    except KeyboardInterrupt:
        return 0
