"""JSON renderer for machine-readable snapshot export."""

from __future__ import annotations

import json

from sysmatrix.config import RuntimeConfig
from sysmatrix.models import Snapshot
from sysmatrix.utils.formatting import maybe_redact


def render_json(snapshot: Snapshot, config: RuntimeConfig) -> str:
    """Render snapshot data as formatted JSON with optional redaction."""
    data = snapshot.to_dict()
    data["system"]["user"] = maybe_redact(data["system"]["user"], config.opsec)
    data["system"]["hostname"] = maybe_redact(data["system"]["hostname"], config.opsec)
    data["network"]["ip"] = maybe_redact(data["network"]["ip"], config.opsec)
    return json.dumps(data, indent=2, sort_keys=True)
