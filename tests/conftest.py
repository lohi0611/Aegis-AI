"""
AEGIS tests — pytest configuration and shared fixtures.
"""
import sys
from pathlib import Path

# Ensure project root is on the import path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


import pytest


@pytest.fixture(scope="session")
def project_root_path():
    return project_root


@pytest.fixture(scope="session")
def sample_person_bbox():
    """A representative full-body person bounding box [x1,y1,x2,y2]."""
    return [10, 50, 110, 350]


@pytest.fixture(scope="session")
def sample_hardhat_bbox():
    """A bounding box for a hardhat at the head position of sample_person_bbox."""
    return [20, 55, 100, 120]


@pytest.fixture(scope="session")
def sample_no_hardhat_bbox():
    """A bounding box for NO-Hardhat at the head position."""
    return [20, 55, 100, 120]
