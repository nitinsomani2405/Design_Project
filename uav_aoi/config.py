from __future__ import annotations

from typing import Any, Dict
import json
import yaml


def load_config(path: str) -> Dict[str, Any]:
    """Load configuration from YAML or JSON file."""

    if path.lower().endswith(('.yaml', '.yml')):
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    if path.lower().endswith('.json'):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    raise ValueError(f"Unsupported config format: {path}")


