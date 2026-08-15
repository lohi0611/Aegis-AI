"""
AEGIS-AI Evaluation Utilities
Helpers for configuration loading, metrics calculation, hardware telemetry, and serialization.
"""
import os
import sys
import json
import time
import platform
import psutil
import yaml
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

# Root directory of the repository
REPO_ROOT = Path(__file__).resolve().parent.parent

def load_eval_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load and resolve evaluation configuration YAML."""
    if config_path is None:
        config_path = str(REPO_ROOT / "evaluation" / "configs" / "evaluation.yaml")
    
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    
    # Resolve relative paths against REPO_ROOT
    if "model" in cfg and "path" in cfg["model"]:
        cfg["model"]["path"] = str(REPO_ROOT / cfg["model"]["path"])
    if "dataset" in cfg and "yaml_path" in cfg["dataset"]:
        cfg["dataset"]["yaml_path"] = str(REPO_ROOT / cfg["dataset"]["yaml_path"])
        
    return cfg


def ensure_dir(dir_path: Union[str, Path]) -> Path:
    """Ensure a directory exists and return Path object."""
    p = Path(dir_path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_hardware_info() -> Dict[str, Any]:
    """Gather hardware and runtime environment telemetry."""
    info = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "os": f"{platform.system()} {platform.release()} ({platform.version()})",
        "python_version": sys.version.split()[0],
        "processor": platform.processor(),
        "cpu_count_physical": psutil.cpu_count(logical=False),
        "cpu_count_logical": psutil.cpu_count(logical=True),
        "total_ram_gb": round(psutil.virtual_memory().total / (1024 ** 3), 2),
        "available_ram_gb": round(psutil.virtual_memory().available / (1024 ** 3), 2),
    }
    
    try:
        import torch
        info["torch_version"] = torch.__version__
        info["cuda_available"] = torch.cuda.is_available()
        if torch.cuda.is_available():
            info["gpu_name"] = torch.cuda.get_device_name(0)
            info["gpu_count"] = torch.cuda.device_count()
            info["gpu_vram_gb"] = round(torch.cuda.get_device_properties(0).total_memory / (1024 ** 3), 2)
        else:
            info["gpu_name"] = "None (CPU Execution)"
    except ImportError:
        info["torch_version"] = "Not Installed"
        info["cuda_available"] = False
        
    return info


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for NumPy / PyTorch types."""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        elif hasattr(obj, "item"):
            return obj.item()
        return super().default(obj)


def save_json_report(data: Dict[str, Any], filepath: Union[str, Path]) -> None:
    """Save dictionary report as pretty-printed JSON."""
    filepath = Path(filepath)
    ensure_dir(filepath.parent)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, cls=NumpyEncoder)
    print(f"[AEGIS-EVAL] Saved JSON report to: {filepath}")


def save_csv_report(data: Union[pd.DataFrame, List[Dict[str, Any]]], filepath: Union[str, Path]) -> None:
    """Save metrics DataFrame or records list as CSV."""
    filepath = Path(filepath)
    ensure_dir(filepath.parent)
    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = data
    df.to_csv(filepath, index=False)
    print(f"[AEGIS-EVAL] Saved CSV report to: {filepath}")
