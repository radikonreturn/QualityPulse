"""
QualityPulse — Streamlit Root
Configures page, injects global styles, and wires up all 5 pages via st.navigation.
"""

import sys
import os

# Ensure the app directory is on sys.path for all page imports
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from db.database import init_db
from db.seed import run as seed_run
from components.styles import inject_css
from components.icons import ZAP, get_svg

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="QualityPulse",
    page_icon="⚡", # Browser tab emoji
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Database Initialization ───────────────────────────────────────────────────
if "db_initialized" not in st.session_state:
    db_path = os.path.join(os.path.dirname(__file__), "quality.db")
    # Always ensure db is ready
    init_db()
    # Seed only if it's a new database (heuristic check)
    if not os.path.exists(db_path) or os.path.getsize(db_path) < 10000:
        seed_run()
    st.session_state.db_initialized = True

# Inject CSS at app level
inject_css()

# ── Sidebar logo ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-logo">
        <div style="display: flex; flex-direction: column; align-items: center; gap: 8px;">
            <div style="background: rgba(59, 130, 246, 0.2); padding: 12px; border-radius: 16px;">
                {get_svg(ZAP, color="#3b82f6", size=40)}
            </div>
            <h2 style="margin:0; color: white;">QualityPulse</h2>
            <small style="color: #94a3b8; font-weight: 600;">System v1.0</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Navigation ────────────────────────────────────────────────────────────────
dashboard  = st.Page("pages/01_dashboard.py", title="Dashboard",       icon=":material/dashboard:", default=True)
pareto     = st.Page("pages/02_pareto.py",   title="Pareto Analizi",   icon=":material/bar_chart:")
spc        = st.Page("pages/03_spc.py",      title="SPC Kontrol Grafiği",     icon=":material/show_chart:")
capa       = st.Page("pages/04_capa.py",     title="CAPA",      icon=":material/build:")
fmea       = st.Page("pages/05_fmea.py",     title="FMEA",     icon=":material/warning:")
data_entry = st.Page("pages/06_data_entry.py", title="Veri Girişi",      icon=":material/post_add:")
data_export= st.Page("pages/07_data_export.py",title="Excel İndir",      icon=":material/file_download:")

pg = st.navigation(
    pages=[dashboard, pareto, spc, capa, fmea, data_entry, data_export],
    position="sidebar",
    expanded=True,
)
pg.run()
