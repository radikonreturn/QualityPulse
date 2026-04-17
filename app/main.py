import os
import sys
import importlib
from nicegui import ui
from fastapi.responses import RedirectResponse

# Ensure app directory is on path
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from db.database import init_db
from db.seed import run as seed_run
from utils.paths import get_app_storage_dir

# Initialize Database
init_db()

# Layout components
from components.layout import frame
from nicegui import app

# Add static files for assets and user uploads
STORAGE_DIR = get_app_storage_dir()
UPLOAD_DIR = os.path.join(STORAGE_DIR, 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.add_static_files('/assets', os.path.join(APP_DIR, 'assets'))
app.add_static_files('/uploads', UPLOAD_DIR)

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
    # Global Security Middleware
    unrestricted_pages = ['/login', '/static', '/_nicegui']
    
    @app.middleware
    async def auth_middleware(request, call_next):
        if not app.storage.user.get('authenticated', False):
            if not any(request.url.path.startswith(p) for p in unrestricted_pages):
                return RedirectResponse('/login')
        return await call_next(request)

    # Run the application
    native_mode = os.getenv('QP_WEB_MODE', '0') != '1'
    
    ui.run(
        title="QualityPulse — Intelligent Quality Management System",
        favicon=os.path.join(APP_DIR, 'assets', 'icon.png'),
        native=native_mode,
        window_size=(1440, 900),
        storage_secret="qp_secret_key_2026",
        reload=False
    )
