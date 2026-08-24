import os
import sys
import importlib
from nicegui import ui

# Ensure app directory is on path
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from core.auth import ensure_default_admin
from utils.paths import get_app_storage_dir

# Initialize master auth database and bootstrap tenant
ensure_default_admin()

# Layout components
from components.layout import frame
from nicegui import app

# Add static files for assets and user uploads
STORAGE_DIR = get_app_storage_dir()
UPLOAD_DIR = os.path.join(STORAGE_DIR, 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.add_static_files('/assets', os.path.join(APP_DIR, 'assets'))
app.add_static_files('/uploads', UPLOAD_DIR)

# Minimal Health Check Endpoint for Docker / Coolify / Reverse Proxy
@app.get('/health')
def health_check():
    return {"status": "healthy", "service": "QualityPulse"}

# Import pages to register routes
page_modules = [
    "pages.dashboard",
    "pages.pareto",
    "pages.spc",
    "pages.capa",
    "pages.fmea",
    "pages.data_entry",
    "pages.data_export",
    "pages.login",
]

for mod in page_modules:
    try:
        importlib.import_module(mod)
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to load page module {mod}. The application may be partially functional.")
        print(f"Details: {e}")

# Global Exception Handler for Stability
def handle_exception(e: Exception):
    print(f"UNHANDLED EXCEPTION: {e}")
    ui.notify(f"An unexpected error occurred: {str(e)[:100]}...", type='negative', position='top')

app.on_exception(handle_exception)

if __name__ in {"__main__", "__mp_main__"}:
    port = int(os.environ.get("PORT", "8888"))
    storage_secret = os.environ.get("STORAGE_SECRET", os.environ.get("SECRET_KEY", "qp_secret_key_2026"))
    ui.run(
        title="QualityPulse — Intelligent Quality Management System",
        favicon=os.path.join(APP_DIR, 'assets', 'icon.svg'),
        host="0.0.0.0",
        port=port,
        storage_secret=storage_secret,
        reload=False,
        show=False,
        forwarded_allow_ips="*"
    )
