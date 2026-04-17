import os
import sys
import importlib
from nicegui import ui

# Ensure app directory is on path
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from db.database import init_db
from db.seed import run as seed_run

# Initialize Database
db_path = os.path.join(APP_DIR, "quality.db")
init_db()

# Improved Seeding logic: Check if database is actually empty
def needs_seeding():
    from db.database import get_defects
    try:
        defects = get_defects(limit=1)
        return len(defects) == 0
    except Exception:
        return True

if needs_seeding():
    print("Database empty or missing. Running seed logic...")
    seed_run()

# Layout components
from components.layout import frame
from nicegui import app

# Add static files for assets and user uploads
UPLOAD_DIR = os.path.join(APP_DIR, 'uploads')
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
