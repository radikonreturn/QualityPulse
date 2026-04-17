import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from utils.paths import get_app_storage_dir

def create_backup(dest_path: str):
    """
    Zip the database and uploads directory into a single backup file.
    """
    storage_dir = get_app_storage_dir()
    db_file = storage_dir / "quality.db"
    upload_dir = storage_dir / "uploads"
    
    with zipfile.ZipFile(dest_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add database
        if db_file.exists():
            zipf.write(db_file, "quality.db")
        
        # Add uploads
        if upload_dir.exists():
            for root, dirs, files in os.walk(upload_dir):
                for file in files:
                    full_path = Path(root) / file
                    arcname = Path("uploads") / full_path.relative_to(upload_dir)
                    zipf.write(full_path, arcname)

def restore_backup(zip_path: str):
    """
    Extract a backup ZIP file and restore the database and uploads.
    """
    storage_dir = get_app_storage_dir()
    
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        # Before extracting, we should probably close DB connections if possible,
        # but in a simple nicegui app, we just overwrite and restart.
        zipf.extractall(storage_dir)
