"""e-SAJ source collector for validation.

This collector does not scrape e-SAJ directly. Instead, it reads a curated
snapshot (manual validation export) that represents practical ground truth.
This keeps compliance and deterministic validation behavior in MVP.
"""

from __future__ import annotations

import json
import os
from pathlib import Path


class ESAJSnapshotCollector:
    """Loads validated e-SAJ process snapshots from local JSON file."""

    def __init__(self) -> None:
        path = os.getenv("ESAJ_SNAPSHOT_PATH", "./esaj_snapshot.json")
        self.snapshot_path = Path(path)

    def find_by_processo(self, processo: str) -> dict | None:
        """Return e-SAJ snapshot for the given CNJ process number."""
        if not self.snapshot_path.exists():
            return None

        with self.snapshot_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        registros = payload.get("processos", []) if isinstance(payload, dict) else []

        for item in registros:
            if item.get("numero") == processo:
                return item

        return None
