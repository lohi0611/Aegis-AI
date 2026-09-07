"""
AEGIS Incident Explorer Forwarder
"""
import sys
from pathlib import Path
import runpy

_root = Path(__file__).resolve().parent.parent
_dash = _root / "dashboard"
for _p in [str(_dash), str(_root)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

runpy.run_path(str(_dash / "pages" / "2_incidentExplorer.py"), run_name="__main__")
