import streamlit as st
import pandas as pd
import sqlite3
import io
from datetime import datetime
from db.database import DB_PATH
from components.styles import inject_css, page_header, section_header
from components.icons import get_svg, DASHBOARD

# Provide a suitable SVG icon for DOWNLOAD (we can reuse an existing one or construct a minimalist one)
DOWNLOAD_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>"""
FILE_EXCEL = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="8" y1="13" x2="16" y2="13"/><line x1="8" y1="17" x2="16" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>"""

def get_db_connection():
    return sqlite3.connect(str(DB_PATH))

def create_excel_export() -> bytes:
    """Create an Excel file containing all tables with professional formatting."""
    conn = get_db_connection()
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_defects = pd.read_sql("SELECT * FROM defects", conn)
        df_measurements = pd.read_sql("SELECT * FROM measurements", conn)
        df_capa = pd.read_sql("SELECT * FROM capa", conn)
        df_fmea = pd.read_sql("SELECT * FROM fmea", conn)
        
        # 1. Provide an Executive Summary Sheet at the front
        summary_data = {
            "Rapor Özeti Metrikleri": ["Oluşturulma Tarihi", "Toplam Hata Kaydı (Adet)", "Sistemdeki Ölçüm Sayısı", "Açılan CAPA Dosyası", "FMEA Risk Satırları"],
            "Değer / Kayıt": [
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                f"{len(df_defects):,} Kayıt",
                f"{len(df_measurements):,} Kayıt",
                f"{len(df_capa):,} Dosya",
                f"{len(df_fmea):,} Satır"
            ]
        }
        df_summary = pd.DataFrame(summary_data)
        
        # Write sheets to buffer
        df_summary.to_excel(writer, sheet_name="Özet Rapor", index=False)
        df_defects.to_excel(writer, sheet_name="Defects (Hata Kayıtları)", index=False)
        df_measurements.to_excel(writer, sheet_name="Measurements (Ölçümler)", index=False)
        df_capa.to_excel(writer, sheet_name="CAPA Müşteri Şikayetleri", index=False)
        df_fmea.to_excel(writer, sheet_name="FMEA Tablosu", index=False)
        
        # Apply professional corporate formatting
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from utils.export import format_excel_sheet
        
        ws_summary = writer.sheets["Özet Rapor"]
        format_excel_sheet(ws_summary, auto_filter=False)
        
        # Provide wider columns for summary specifically
        ws_summary.column_dimensions['A'].width = 35
        ws_summary.column_dimensions['B'].width = 25
        
        format_excel_sheet(writer.sheets["Defects (Hata Kayıtları)"])
        format_excel_sheet(writer.sheets["Measurements (Ölçümler)"])
        format_excel_sheet(writer.sheets["CAPA Müşteri Şikayetleri"])
        format_excel_sheet(writer.sheets["FMEA Tablosu"])

    conn.close()
    return output.getvalue()

def show():
    inject_css()
    page_header(
        f"{get_svg(DOWNLOAD_SVG, size=32)} Veri Dışa Aktarım",
        "Tüm veritabanını veya seçili modülleri Excel (.xlsx) formatında indirin"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    left, right = st.columns([2, 2], gap="large")
    
    with left:
        section_header(f"{get_svg(FILE_EXCEL, size=24)} Excel Raporu")
        st.write("Sistemde bulunan tüm **Hata Kayıtları**, **Ölçümler**, **CAPA** ve **FMEA** verilerinizi tek bir Excel dosyası halinde bilgisayarınıza indirebilirsiniz.")
        st.write("Veriler doğrudan veritabanından anlık (canlı) olarak çekilerek hazırlanır.")
        
        excel_data = create_excel_export()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        st.download_button(
            label="Tüm Veriyi İndir (Excel)",
            data=excel_data,
            file_name=f"QualityPulse_Export_{timestamp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            icon=":material/download:",
            type="primary",
            use_container_width=True
        )

    with right:
        section_header(f"{get_svg(DASHBOARD, size=24)} İstatistikler")
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            def_count = cur.execute("SELECT COUNT(*) FROM defects").fetchone()[0]
            meas_count = cur.execute("SELECT COUNT(*) FROM measurements").fetchone()[0]
            capa_count = cur.execute("SELECT COUNT(*) FROM capa").fetchone()[0]
            fmea_count = cur.execute("SELECT COUNT(*) FROM fmea").fetchone()[0]
        except Exception:
            def_count, meas_count, capa_count, fmea_count = 0, 0, 0, 0
            
        conn.close()
        
        st.markdown(f"""
        <div style="background:#f1f5f9;border-radius:10px;padding:20px;border:1px solid #e2e8f0;">
            <ul style="list-style:none;padding:0;margin:0;color:#334155;font-weight:500;">
                <li style="display:flex;justify-content:space-between;margin-bottom:8px;">
                    <span>Hata Kayıtları:</span> <span style="color:#0f172a;font-weight:700;">{def_count}</span>
                </li>
                <li style="display:flex;justify-content:space-between;margin-bottom:8px;">
                    <span>Ölçüm Kayıtları:</span> <span style="color:#0f172a;font-weight:700;">{meas_count}</span>
                </li>
                <li style="display:flex;justify-content:space-between;margin-bottom:8px;">
                    <span>CAPA Dosyaları:</span> <span style="color:#0f172a;font-weight:700;">{capa_count}</span>
                </li>
                <li style="display:flex;justify-content:space-between;">
                    <span>FMEA Satırları:</span> <span style="color:#0f172a;font-weight:700;">{fmea_count}</span>
                </li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    show()
