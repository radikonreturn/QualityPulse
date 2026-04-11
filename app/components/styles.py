"""
QualityPulse — Custom CSS Injector
Applies a dark sidebar, Inter font, metric card styling, and Streamlit chrome removal.
"""

import streamlit as st

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    color: var(--text-color) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%) !important;
    border-right: 1px solid #2a2a4a;
}
[data-testid="stSidebar"] * {
    color: #e0e0e0 !important;
}
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: #e0e0e0 !important;
}
[data-testid="stSidebarNav"] a {
    color: #c0c0d0 !important;
    border-radius: 8px;
    padding: 6px 12px;
    margin: 2px 0;
    transition: all 0.2s ease;
    display: block;
}
[data-testid="stSidebarNav"] a:hover {
    background: rgba(79, 142, 247, 0.18) !important;
    color: #4f8ef7 !important;
}
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: rgba(79, 142, 247, 0.25) !important;
    color: #4f8ef7 !important;
    border-left: 3px solid #4f8ef7;
    font-weight: 600;
}

/* ── Main content ── */
[data-testid="stAppViewContainer"] > .main {
    background: var(--background-color);
}
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1400px !important;
}

/* ── Metric cards override ── */
[data-testid="stMetric"] {
    background: var(--secondary-background-color);
    border: 1px solid rgba(128,128,128,0.2);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    transition: box-shadow 0.2s ease, transform 0.2s ease;
}
[data-testid="stMetric"]:hover {
    box-shadow: 0 6px 18px rgba(79,142,247,0.15);
    transform: translateY(-2px);
}
[data-testid="stMetricLabel"] {
    font-size: 0.80rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}
[data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 700 !important;
}
[data-testid="stMetricDelta"] {
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}

/* ── Remove Streamlit chrome ── */
#MainMenu, footer, [data-testid="stToolbar"] {
    display: none !important;
}

/* ── Section headers ── */
.section-header {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-color);
    padding: 0.4rem 0 0.4rem 0.8rem;
    border-left: 4px solid #4f8ef7;
    margin: 1.2rem 0 0.8rem;
    background: linear-gradient(90deg, rgba(79,142,247,0.15) 0%, transparent 100%);
    border-radius: 0 6px 6px 0;
}

/* ── KPI status badges ── */
.badge-green  { background: #d1fae5; color: #065f46; padding: 2px 10px; border-radius: 12px; font-size: 0.78rem; font-weight: 600; }
.badge-amber  { background: #fef3c7; color: #92400e; padding: 2px 10px; border-radius: 12px; font-size: 0.78rem; font-weight: 600; }
.badge-red    { background: #fee2e2; color: #991b1b; padding: 2px 10px; border-radius: 12px; font-size: 0.78rem; font-weight: 600; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 2px 6px rgba(0,0,0,0.06);
}

/* ── Expanders ── */
[data-testid="stExpander"] {
    border: 1px solid rgba(128,128,128,0.2);
    border-radius: 10px;
    background: var(--secondary-background-color);
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #4f8ef7, #357abd) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 6px rgba(79,142,247,0.35) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(79,142,247,0.45) !important;
}

/* ── Page titles ── */
.page-title {
    font-size: 1.8rem;
    font-weight: 800;
    color: var(--text-color);
    margin-bottom: 0.2rem;
    letter-spacing: -0.02em;
}
.page-subtitle {
    font-size: 0.9rem;
    color: var(--text-color);
    opacity: 0.7;
    margin-bottom: 1.5rem;
}

/* ── Sidebar logo area ── */
.sidebar-logo {
    text-align: center;
    padding: 1.2rem 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 0.8rem;
}
.sidebar-logo h2 {
    color: #4f8ef7 !important;
    font-size: 1.3rem;
    font-weight: 800;
    letter-spacing: 0.05em;
    margin: 0;
}
.sidebar-logo small {
    color: rgba(224,224,224,0.55) !important;
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* ── Smooth page transition ── */
[data-testid="stAppViewContainer"] {
    animation: fadeIn 0.25s ease-in-out;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(4px); }
    to   { opacity: 1; transform: translateY(0); }
}
"""


def inject_css():
    st.markdown(f"<style>{_CSS}</style>", unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def section_header(text: str):
    st.markdown(f'<div class="section-header">{text}</div>', unsafe_allow_html=True)
