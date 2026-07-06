from nicegui import ui
import pandas as pd
from datetime import datetime, timedelta

from db.database import get_defects, get_measurements, get_all_capa
from utils.calculations import (
    calculate_scrap_rate, calculate_oee,
    calculate_cpk_from_rows, get_30_day_trend
)
from components.kpi_card import kpi_card, cpk_card
from components.charts import scrap_trend_chart, defect_donut_chart, oee_gauge
from components.icons import SCRAP, OEE, ALERT, get_svg
from components.layout import frame
from components.tour_component import guided_tour
from core.auth import auth_guard
from utils.insights import generate_quality_insights, get_defect_heatmap_data

@ui.page('/')
def dashboard_page():
    if not auth_guard():
        return
    with frame('Analytical Dashboard'):
        content()

def content():
    # ── Load data ────────────────────────────────────────────────────────────
    today = datetime.today()
    this_month_start = today.replace(day=1).strftime("%Y-%m-%d")
    prev_month_end = (today.replace(day=1) - timedelta(days=1))
    prev_month_start = prev_month_end.replace(day=1).strftime("%Y-%m-%d")
    prev_month_end_str = prev_month_end.strftime("%Y-%m-%d")

    all_defects = get_defects()
    this_month_defects = get_defects(start_date=this_month_start)
    prev_month_defects = get_defects(start_date=prev_month_start, end_date=prev_month_end_str)
    last_30_defects = get_defects(start_date=(today - timedelta(days=30)).strftime("%Y-%m-%d"))
    measurements_all = get_measurements(limit=500)
    capa_all = get_all_capa()

    # ── KPI Calculations ─────────────────────────────────────────────────────
    scrap_this = calculate_scrap_rate(this_month_defects)
    scrap_prev = calculate_scrap_rate(prev_month_defects)
    scrap_delta = round(scrap_this - scrap_prev, 2)
    delta_sign = "+" if scrap_delta >= 0 else ""

    oee_quality = 1 - (scrap_this / 100) if scrap_this < 100 else 0.01
    oee_val = calculate_oee(0.92, 0.89, oee_quality)

    critical_open = sum(1 for c in capa_all if c["criticality"] == "Critical" and c["status"] != "Closed")
    critical_total = sum(1 for c in capa_all if c["criticality"] == "Critical")

    # ── Executive Insights ───────────────────────────────────────────────────
    insights = generate_quality_insights(last_30_defects)

    # Cpk from latest 25 measurements
    cpk_data = {}
    if measurements_all:
        latest_25 = measurements_all[:25]
        cpk_data = calculate_cpk_from_rows(latest_25)

    # ── UI Layout ────────────────────────────────────────────────────────────
    ui.label('Key Performance Indicators').classes('text-lg font-bold text-slate-700 mb-4 ml-1')
    
    # KPI Cards Row
    with ui.row().classes('w-full gap-4 items-stretch mb-8'):
        with ui.column().classes('flex-1 min-w-[200px]'):
            kpi_card(
                label="Scrap Rate",
                value=f"{scrap_this:.2f}",
                suffix="%",
                delta=f"{delta_sign}{scrap_delta}%",
                delta_label="vs prev month",
                color="green" if scrap_this < 3 else "amber" if scrap_this < 5 else "red",
                icon=get_svg(SCRAP, color="#2ecc71" if scrap_this < 3 else "#f39c12" if scrap_this < 5 else "#e74c3c", size=24),
            )
        with ui.column().classes('flex-1 min-w-[200px]'):
            kpi_card(
                label="OEE",
                value=f"{oee_val:.1f}",
                suffix="%",
                delta=f"{'+' if oee_val >= 85 else ''}{oee_val - 85:.1f}%",
                delta_label="vs target (85%)",
                color="green" if oee_val >= 85 else "amber" if oee_val >= 65 else "red",
                icon=get_svg(OEE, color="#3b82f6", size=24),
            )
        with ui.column().classes('flex-1 min-w-[200px]'):
            kpi_card(
                label="Critical CAPA (Open)",
                value=str(critical_open),
                delta=f"Total {critical_total} critical",
                delta_label="",
                color="green" if critical_open == 0 else "amber" if critical_open <= 3 else "red",
                icon=get_svg(ALERT, color="#e74c3c", size=24),
            )
        with ui.column().classes('flex-1 min-w-[200px]'):
            cpk_val = cpk_data.get("cpk", 0.0)
            cpk_card(cpk_val, label="Process Capability (Cpk)")

    ui.label('Trend & Defect Analysis').classes('text-lg font-bold text-slate-700 mb-4 ml-1')
    
    # Graphs Row
    with ui.row().classes('w-full gap-6 mb-8 items-stretch'):
        with ui.card().classes('flex-[3] p-4 shadow-sm border border-slate-200 rounded-xl overflow-hidden'):
            trend_data = get_30_day_trend(all_defects)
            fig_trend = scrap_trend_chart(trend_data, threshold=3.0)
            ui.plotly(fig_trend).classes('w-full h-[320px]')
        
        with ui.card().classes('flex-[2] p-4 shadow-sm border border-slate-200 rounded-xl overflow-hidden'):
            fig_donut = defect_donut_chart(this_month_defects)
            ui.plotly(fig_donut).classes('w-full h-[320px]')

    ui.label('Quality Interconnectivity Matrix').classes('text-lg font-bold text-slate-700 mb-4 ml-1')
    
    with ui.row().classes('w-full gap-6 mb-8 items-stretch'):
        with ui.card().classes('w-full p-6 shadow-sm border border-slate-200 rounded-xl overflow-hidden'):
            import plotly.graph_objects as go
            h_lines, h_types, h_matrix = get_defect_heatmap_data(last_30_defects)
            if h_matrix:
                fig_hm = go.Figure(data=go.Heatmap(
                    z=h_matrix, x=h_lines, y=h_types,
                    colorscale='Viridis', showscale=True,
                    hoverongaps = False)
                )
                fig_hm.update_layout(
                    title='Line vs Defect Correlation (30 Days)',
                    margin=dict(l=20, r=20, t=40, b=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=300
                )
                ui.plotly(fig_hm).classes('w-full')
            else:
                ui.label('Insufficient data for correlation matrix.').classes('text-slate-400 italic text-center w-full py-20')

    ui.label('Operational Insights').classes('text-lg font-bold text-slate-700 mb-4 ml-1')
    
    # OEE & Summary Row
    with ui.row().classes('w-full gap-6 items-stretch'):
        with ui.card().classes('flex-[1] p-6 shadow-sm border border-slate-200 rounded-xl items-center justify-center'):
            fig_gauge = oee_gauge(oee_val, target=85.0)
            ui.plotly(fig_gauge).classes('w-full')
            ui.label(f"Availability: 92% | Performance: 89% | Quality: {oee_quality*100:.1f}%").classes('text-[10px] text-slate-400 mt-2 font-bold uppercase tracking-widest')
            
        with ui.card().classes('flex-[2] p-6 shadow-sm border border-slate-200 rounded-xl bg-slate-50'):
            with ui.row().classes('items-center gap-2 mb-4'):
                ui.icon('auto_awesome', size='24px').classes('text-blue-500')
                ui.label('Executive Insights').classes('font-black text-slate-800 uppercase tracking-tighter text-lg')
            
            with ui.column().classes('gap-3 w-full'):
                for insight in insights:
                    with ui.row().classes('items-start gap-3 p-3 bg-white rounded-lg border border-slate-200 shadow-xs'):
                        ui.icon('chevron_right', size='16px').classes('text-slate-300 mt-1')
                        ui.markdown(insight).classes('text-xs text-slate-600')

    # ── Photo Gallery Section ────────────────────────────────────────────────
    defect_photos = [d for d in last_30_defects if d.get('photo_path')]
    if defect_photos:
        ui.label('Visual Quality Inspection (Recent)').classes('text-lg font-bold text-slate-700 mt-8 mb-4 ml-1')
        with ui.row().classes('w-full gap-4 overflow-x-auto pb-4 no-wrap'):
            for d in defect_photos[-10:]: # Show last 10 photos
                with ui.card().classes('min-w-[200px] p-0 shadow-sm border border-slate-200 rounded-xl overflow-hidden hover:border-blue-400 transition-all cursor-pointer'):
                    ui.image(d['photo_path']).classes('w-full h-32 object-cover')
                    with ui.column().classes('p-3 gap-0'):
                        ui.label(f"{d['defect_type']}").classes('text-[10px] font-black uppercase text-slate-800')
                        ui.label(f"{d['date']} | {d['line']}").classes('text-[9px] text-slate-400')

    # Trigger Guided Tour
    guided_tour()
