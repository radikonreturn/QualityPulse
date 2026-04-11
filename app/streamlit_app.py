"""
QualityPulse — Streamlit Root
Configures page, injects global styles, and wires up all 5 pages via st.navigation.
"""

import sys
import os

# Ensure the app directory is on sys.path for all page imports
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

# ── Page config (must be first Streamlit call) ────────────────────────────────
icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
st.set_page_config(
    page_title="QualityPulse",
    page_icon=icon_path if os.path.exists(icon_path) else "📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Initialize DB on first run ────────────────────────────────────────────────
from db.database import init_db
from db.seed import run as seed_run
from components.styles import inject_css

_initialized = st.session_state.get("_db_initialized", False)
if not _initialized:
    init_db()
    seed_run()
    st.session_state["_db_initialized"] = True

# Inject CSS at app level (ensures sidebar logo styles are always present)
inject_css()

# ── Sidebar logo ──────────────────────────────────────────────────────────────
from components.icons import ZAP, get_svg

with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-logo">
        <div style="display: flex; align-items: center; gap: 10px;">
            {get_svg(ZAP, color="#FFD700", size=32)}
            <h2 style="margin:0;">QualityPulse</h2>
        </div>
        <small>Quality Management System v1.0</small>
    </div>
    """, unsafe_allow_html=True)

# ── Navigation ────────────────────────────────────────────────────────────────
# Note: st.Page icon parameter only supports emojis or material symbols (as strings).
# Since the user wants SVG images, we will keep emojis for the st.Page objects (as fallback)
# but we will use the SVGs in the page headers themselves.
dashboard = st.Page("pages/01_dashboard.py", title="Dashboard",       icon=":material/dashboard:", default=True)
pareto    = st.Page("pages/02_pareto.py",   title="Pareto Analizi",   icon=":material/bar_chart:")
spc       = st.Page("pages/03_spc.py",      title="SPC Grafiği",      icon=":material/show_chart:")
capa      = st.Page("pages/04_capa.py",     title="CAPA Takibi",      icon=":material/build:")
fmea      = st.Page("pages/05_fmea.py",     title="FMEA Matrisi",     icon=":material/warning:")


pg = st.navigation(
    pages=[dashboard, pareto, spc, capa, fmea],
    position="sidebar",
    expanded=True,
)
pg.run()
