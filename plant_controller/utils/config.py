from __future__ import annotations

import pathlib
from typing import Any, Dict

import yaml


def load_config(path: str | pathlib.Path) -> Dict[str, Any]:
    cfg_path = pathlib.Path(path)
    if not cfg_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {cfg_path}")
    with cfg_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return data

