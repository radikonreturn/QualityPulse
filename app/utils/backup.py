import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from utils.paths import get_app_storage_dir
from db.database import current_tenant_id
from core.db import get_tenant_db_path

def create_backup(dest_path: str):
    """
    Zip the database and uploads directory into a single backup file.
    """
    storage_dir = get_app_storage_dir()
    db_file = get_tenant_db_path(current_tenant_id())
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
    tenant_db = get_tenant_db_path(current_tenant_id())
    
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        for member in zipf.namelist():
            if member == "quality.db":
                with zipf.open(member) as source, tenant_db.open("wb") as target:
                    shutil.copyfileobj(source, target)
            elif member.startswith("uploads/"):
                zipf.extract(member, storage_dir)
