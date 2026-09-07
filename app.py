"""
AEGIS Safety Intelligence — Root Application Entrypoint
Forwarder for Streamlit deployments pointing to repository root app.py
"""
import os
import sys
from pathlib import Path

# Add dashboard directory and project root to sys.path
_current_dir = Path(__file__).resolve().parent
_dashboard_dir = _current_dir / "dashboard"
for _p in [str(_dashboard_dir), str(_current_dir)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Execute main dashboard app
import runpy
runpy.run_path(str(_dashboard_dir / "app.py"), run_name="__main__")
