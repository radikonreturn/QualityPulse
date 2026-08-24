import os
import sys
from pathlib import Path

def get_app_storage_dir() -> Path:
    """
    Returns the persistent storage directory for the application.
    - Custom / Docker: Configured via QP_DATA_DIR environment variable
    - Production (Frozen .exe): %APPDATA%/QualityPulse
    - Development: The project root directory
    """
    if "QP_DATA_DIR" in os.environ:
        base_dir = Path(os.environ["QP_DATA_DIR"])
    elif getattr(sys, 'frozen', False):
        # Running as a bundled executable
        base_dir = Path(os.environ.get("APPDATA", os.path.expanduser("~"))) / "QualityPulse"
    else:
        # Running in a development environment
        # We assume this script is in app/utils/paths.py, so parent.parent is 'app/'
        base_dir = Path(__file__).parent.parent
    
    # Ensure the directory exists
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir
