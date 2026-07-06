from nicegui import ui
import pandas as pd
import os
from datetime import datetime
from db.database import get_audit_logs, get_connection
from components.layout import frame
from core.auth import auth_guard
from utils.export import format_excel_sheet
from utils.calculations import calculate_scrap_rate, count_overdue_capa
from nicegui import app

def get_db_connection():
    return get_connection()

def create_excel_export() -> str:
    """Create a multi-sheet Excel report and return the persistent file path."""
    conn = get_db_connection()
    
    # Ensure a persistent 'exports' directory exists in the app root
    export_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exports')
    os.makedirs(export_dir, exist_ok=True)
    
    filename = f"QualityPulse_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    target_path = os.path.join(export_dir, filename)
    
    try:
        with pd.ExcelWriter(target_path, engine='openpyxl') as writer:
            # Safely read tables
            tables = {
                "Defect Records": "defects",
                "Measurement Logs": "measurements",
                "CAPA Tracker": "capa",
                "FMEA Register": "fmea"
            }
            
            dataframes = {}
            for sheet_name, table_name in tables.items():
                try:
                    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
                    dataframes[table_name] = df
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    format_excel_sheet(writer.sheets[sheet_name])
                except Exception:
                    pd.DataFrame([{"Note": "No data found"}]).to_excel(writer, sheet_name=sheet_name, index=False)

            # Executive Summary / KPI Sheet
            summary_rows = [
                {"Metric": "Report Generation Time", "Value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                {"Metric": "Total Defect Entries", "Value": len(dataframes.get("defects", []))},
            ]
            
            if "defects" in dataframes and not dataframes["defects"].empty:
                scrap = calculate_scrap_rate(dataframes["defects"].to_dict('records'))
                summary_rows.append({"Metric": "Global Scrap Rate", "Value": f"{scrap}%"})
            
            if "capa" in dataframes and not dataframes["capa"].empty:
                overdue = count_overdue_capa(dataframes["capa"].to_dict('records'))
                summary_rows.append({"Metric": "Overdue CAPA Count", "Value": overdue})

            df_summary = pd.DataFrame(summary_rows)
            df_summary.to_excel(writer, sheet_name="Executive Summary", index=False)
            format_excel_sheet(writer.sheets["Executive Summary"])

            # Corporate Branding / Cover Page
            cfg = app.storage.user.get('config', {})
            cover_rows = [
                {"Field": "Enterprise Name", "Data": cfg.get("company", {}).get("name", "N/A")},
                {"Field": "Facility / Plant", "Data": cfg.get("company", {}).get("facility", "N/A")},
                {"Field": "Quality Lead", "Data": cfg.get("company", {}).get("qe", "N/A")},
                {"Field": "Plant City", "Data": cfg.get("company", {}).get("city", "N/A")},
                {"Field": "Total Headcount", "Data": cfg.get("company", {}).get("employees", 0)},
                {"Field": "Status", "Data": "CERTIFIED AUDIT REPORT"}
            ]
            df_cover = pd.DataFrame(cover_rows)
            df_cover.to_excel(writer, sheet_name="Company Overview", index=False)
            format_excel_sheet(writer.sheets["Company Overview"])

            # System Audit Logs Sheet
            audit_data = get_audit_logs(limit=500)
            if audit_data:
                df_audit = pd.DataFrame(audit_data)
                df_audit.to_excel(writer, sheet_name="Audit Journal", index=False)
                format_excel_sheet(writer.sheets["Audit Journal"])

        return target_path
    finally:
        conn.close()

@ui.page('/data_export')
def data_export_page():
    if not auth_guard():
        return
    with frame('Data Export Center'):
        content()

def content():
    with ui.card().classes('max-w-2xl mx-auto p-12 shadow-xl border border-slate-200 rounded-3xl mt-12'):
        with ui.column().classes('items-center text-center w-full'):
            ui.avatar('file_download', color='blue-600', text_color='white', size='4rem').classes('mb-6 shadow-lg shadow-blue-100')
            ui.label('Comprehensive Excel Export').classes('text-2xl font-black text-slate-800 mb-2 tracking-tighter')
            ui.label('Generate a professional multi-sheet report including all database records, KPI summaries, and formatted audit logs.').classes('text-sm text-slate-500 mb-10 leading-relaxed')
        
        async def trigger_export():
            n = ui.notification('Generating audit-ready report...', type='ongoing', spinner=True)
            try:
                path = create_excel_export()
                filename = f"QualityPulse_Audit_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
                
                if os.path.exists(path):
                    ui.download(path, filename)
                    n.message = 'Report Ready! Download starting...'
                    n.icon = 'check_circle'
                    n.spinner = False
                    n.type = 'positive'
                    n.timeout = 5
                else:
                    raise Exception("File creation failed.")
                    
            except Exception as e:
                n.message = f'Export Error: {str(e)}'
                n.type = 'negative'
                n.spinner = False

        ui.button('GENERATE AUDIT REPORT', icon='auto_awesome', on_click=trigger_export) \
            .props('elevated no-caps').classes('w-full bg-slate-900 text-white h-16 rounded-2xl font-bold shadow-xl shadow-slate-200')
        
        with ui.row().classes('w-full justify-center mt-6 items-center gap-2 opacity-40'):
            ui.icon('security', size='14px')
            ui.label('Standardized XLSX Format (ISO Compliant)').classes('text-[10px] font-black uppercase tracking-widest')
