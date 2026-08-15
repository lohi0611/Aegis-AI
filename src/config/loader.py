"""
AEGIS — Configuration Loader Module
Provides typed dictionary configuration loading from YAML with environment variable overrides.
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def get_default_config_path() -> Path:
    """Return default configuration YAML path."""
    return REPO_ROOT / "configs" / "config.yaml"


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load YAML configuration file with environment variable overrides.
    Resolves relative file paths against REPO_ROOT.
    """
    p = Path(config_path) if config_path else get_default_config_path()
    if not p.is_absolute():
        p = REPO_ROOT / p

    if not p.exists():
        # Fallback to empty default structure if file missing
        cfg: Dict[str, Any] = {}
    else:
        with open(p, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}

    # Apply environment variable overrides if present
    if "AEGIS_DEVICE" in os.environ:
        cfg.setdefault("model", {})["device"] = os.environ["AEGIS_DEVICE"]
    if "AEGIS_CONF_THRESH" in os.environ:
        cfg.setdefault("model", {})["conf_threshold"] = float(os.environ["AEGIS_CONF_THRESH"])
    if "DATABASE_URL" in os.environ:
        cfg.setdefault("database", {})["url"] = os.environ["DATABASE_URL"]
    if "AEGIS_MODEL_PATH" in os.environ:
        cfg.setdefault("model", {})["path"] = os.environ["AEGIS_MODEL_PATH"]

    # Resolve relative paths
    if "model" in cfg and "path" in cfg["model"]:
        mpath = Path(cfg["model"]["path"])
        if not mpath.is_absolute():
            cfg["model"]["path"] = str(REPO_ROOT / mpath)

    if "evaluation" in cfg and "dataset_yaml" in cfg["evaluation"]:
        dpath = Path(cfg["evaluation"]["dataset_yaml"])
        if not dpath.is_absolute():
            cfg["evaluation"]["dataset_yaml"] = str(REPO_ROOT / dpath)

    return cfg
