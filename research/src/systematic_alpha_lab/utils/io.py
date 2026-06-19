"""Filesystem helpers: project paths, config loading, JSON/Parquet IO."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

# research/  (three levels up from this file: utils -> systematic_alpha_lab -> src -> research)
RESEARCH_ROOT = Path(__file__).resolve().parents[3]
CONFIG_DIR = RESEARCH_ROOT / "config"
OUTPUT_DIR = RESEARCH_ROOT / "outputs"
DATA_DIR = RESEARCH_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
WEB_DATA_DIR = RESEARCH_ROOT.parent / "web" / "public" / "research-data"

_OUTPUT_SUBDIRS = {
    "data_audit": OUTPUT_DIR / "data_audit",
    "signals": OUTPUT_DIR / "signals",
    "backtests": OUTPUT_DIR / "backtests",
    "validation": OUTPUT_DIR / "validation",
    "website_json": OUTPUT_DIR / "website_json",
    "reports": OUTPUT_DIR / "reports",
}


def ensure_dirs() -> None:
    """Create every output and data directory if missing."""
    for path in (*_OUTPUT_SUBDIRS.values(), RAW_DIR, WEB_DATA_DIR):
        path.mkdir(parents=True, exist_ok=True)


def out_path(subdir: str, filename: str) -> Path:
    return _OUTPUT_SUBDIRS[subdir] / filename


def load_config(name: str) -> dict[str, Any]:
    """Load a YAML config by base name (without extension)."""
    with open(CONFIG_DIR / f"{name}.yaml", "r") as fh:
        return yaml.safe_load(fh)


def _clean(obj: Any) -> Any:
    """Recursively convert numpy/pandas scalars and NaN/inf into JSON-safe values."""
    if isinstance(obj, dict):
        return {str(k): _clean(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_clean(v) for v in obj]
    if isinstance(obj, float):
        return None if (math.isnan(obj) or math.isinf(obj)) else round(obj, 6)
    # numpy scalar types
    if hasattr(obj, "item") and not isinstance(obj, (str, bytes)):
        try:
            val = obj.item()
            return _clean(val) if isinstance(val, float) else val
        except (ValueError, AttributeError):
            return obj
    if isinstance(obj, (pd.Timestamp,)):
        return obj.strftime("%Y-%m-%d")
    return obj


def write_json(subdir: str, filename: str, payload: Any) -> Path:
    path = out_path(subdir, filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as fh:
        json.dump(_clean(payload), fh, indent=2)
    return path


def write_web_json(filename: str, payload: Any) -> Path:
    """Write a website-facing JSON file into web/public/research-data/."""
    WEB_DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = WEB_DATA_DIR / filename
    with open(path, "w") as fh:
        json.dump(_clean(payload), fh, indent=2)
    return path


def read_json(subdir: str, filename: str) -> Any:
    with open(out_path(subdir, filename), "r") as fh:
        return json.load(fh)


def write_parquet(subdir: str, filename: str, df: pd.DataFrame) -> Path:
    path = out_path(subdir, filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path)
    return path


def read_parquet(subdir: str, filename: str) -> pd.DataFrame:
    return pd.read_parquet(out_path(subdir, filename))
