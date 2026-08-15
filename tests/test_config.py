"""
AEGIS — Unit Tests for Configuration Loader
Tests YAML loading, environment variable overrides, and path resolution.
"""
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from src.config.loader import load_config, get_default_config_path


class TestConfigLoader:
    def test_default_config_loads(self):
        """Default config.yaml should load without error."""
        cfg = load_config()
        assert isinstance(cfg, dict)
        assert "model" in cfg
        assert "compliance" in cfg
        assert "database" in cfg

    def test_model_path_resolved_to_absolute(self):
        """Model path should be resolved to an absolute path."""
        cfg = load_config()
        assert os.path.isabs(cfg["model"]["path"])

    def test_env_override_device(self, monkeypatch):
        """AEGIS_DEVICE env var should override device config."""
        monkeypatch.setenv("AEGIS_DEVICE", "cuda:0")
        cfg = load_config()
        assert cfg["model"]["device"] == "cuda:0"

    def test_env_override_conf_threshold(self, monkeypatch):
        """AEGIS_CONF_THRESH env var should override conf threshold."""
        monkeypatch.setenv("AEGIS_CONF_THRESH", "0.6")
        cfg = load_config()
        assert cfg["model"]["conf_threshold"] == pytest.approx(0.6)

    def test_config_required_keys_present(self):
        """All critical keys must be present in config."""
        cfg = load_config()
        required_keys = ["model", "compliance", "database", "video", "alerts", "evaluation"]
        for key in required_keys:
            assert key in cfg, f"Missing required config key: {key}"

    def test_compliance_required_ppe_structure(self):
        """Compliance section must define required_ppe."""
        cfg = load_config()
        comp = cfg.get("compliance", {})
        required_ppe = comp.get("required_ppe", {})
        assert "hardhat" in required_ppe
        assert "safety_vest" in required_ppe
