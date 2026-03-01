"""I/O helpers for refua-preclinical."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def load_mapping(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    suffix = file_path.suffix.lower()

    if suffix == ".json":
        payload = json.loads(text)
    elif suffix in {".yml", ".yaml"}:
        try:
            import yaml  # type: ignore
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "PyYAML is required for YAML input; install pyyaml or use JSON files."
            ) from exc
        payload = yaml.safe_load(text)
    else:
        raise ValueError("Unsupported config file extension. Use .json, .yml, or .yaml")

    if payload is None:
        return {}
    if not isinstance(payload, dict):
        raise ValueError("Top-level config must be an object")
    return dict(payload)


def load_rows(path: str | Path) -> list[dict[str, Any]]:
    file_path = Path(path)
    suffix = file_path.suffix.lower()
    if suffix == ".json":
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return [dict(item) for item in payload if isinstance(item, dict)]
        if isinstance(payload, dict):
            rows = payload.get("rows")
            if isinstance(rows, list):
                return [dict(item) for item in rows if isinstance(item, dict)]
        raise ValueError(
            'JSON samples file must contain a list of objects or {"rows": [...]} '
        )

    if suffix == ".csv":
        rows: list[dict[str, Any]] = []
        with file_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                rows.append(dict(row))
        return rows

    raise ValueError("Unsupported sample file extension. Use .json or .csv")


def dump_json(path: str | Path, payload: dict[str, Any]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8"
    )
