import os
import sqlite3

def purge_location(db_path, upload_dir, label):
    if not os.path.exists(db_path):
        print(f"Skipping {label}: DB not found at {db_path}")
        return
    
    print(f"Purging {label} at {db_path}...")
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        tables = ['defects', 'measurements', 'capa', 'fmea', 'audit_logs']
        total_purged = 0
        for table in tables:
            try:
                # Check if table exists
                cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if not cur.fetchone():
                    continue
                    
                count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                cur.execute(f"DELETE FROM {table}")
                cur.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
                print(f"  - {table}: Removed {count} records.")
                total_purged += count
            except Exception as e:
                print(f"  - {table}: Error ({e})")
                
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"FAILED to open database at {db_path}: {e}")
    
    if os.path.exists(upload_dir):
        files = os.listdir(upload_dir)
        print(f"Cleaning upload directory: {upload_dir}")
        for file in files:
            file_path = os.path.join(upload_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"  - Removed file: {file}")
    
    print(f"Done purging {label}.\n")

def run_purge():
    print("QualityPulse — Global Production Purge Initiated")
    print("=" * 50)
    
    # 1. Project Local
    local_db = os.path.join(os.getcwd(), 'app', 'quality.db')
    local_upload = os.path.join(os.getcwd(), 'app', 'uploads')
    purge_location(local_db, local_upload, "DEVELOPMENT STATE")
    
    # 2. APPDATA (Production State)
    appdata_base = os.path.join(os.environ.get("APPDATA", ""), "QualityPulse")
    appdata_db = os.path.join(appdata_base, "quality.db")
    appdata_upload = os.path.join(appdata_base, "uploads")
    purge_location(appdata_db, appdata_upload, "PRODUCTION/APPDATA STATE")
    
    print("=" * 50)
    print("SUCCESS: All system records and sample files have been wiped.")

if __name__ == "__main__":
    run_purge()
