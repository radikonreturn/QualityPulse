"""
QualityPulse — Page 1: Dashboard (KPI Özeti)
4 KPI cards + 30-day trend + monthly defect donut.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from db.database import get_defects, get_measurements, get_all_capa
from utils.calculations import (
    calculate_scrap_rate, monthly_scrap_delta, calculate_oee,
    calculate_cpk_from_rows, get_30_day_trend
)
from utils.spc_engine import calculate_cpk
from components.styles import inject_css, page_header, section_header
from components.kpi_card import kpi_card, cpk_card
from components.charts import scrap_trend_chart, defect_donut_chart, oee_gauge
from components.icons import DASHBOARD, SCRAP, OEE, ALERT, SUMMARY, get_svg


def show():
    inject_css()
    page_header(f"{get_svg(DASHBOARD, size=32)} KPI Özeti", "Gerçek zamanlı kalite performans göstergesi — Alüminyum Basınçlı Döküm")

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
    critical_prev = sum(1 for c in capa_all if c["criticality"] == "Critical")

    # Cpk from latest 25 measurements for first available point
    cpk_data = {}
    if measurements_all:
        latest_25 = measurements_all[:25]
        cpk_data = calculate_cpk_from_rows(latest_25)

    # ── KPI Cards Row ────────────────────────────────────────────────────────
    section_header("Ana Performans Göstergeleri")
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi_card(
            label="Hurda Oranı",
            value=f"{scrap_this:.2f}",
            suffix="%",
            delta=f"{delta_sign}{scrap_delta}%",
            delta_label="vs önceki ay",
            color="green" if scrap_this < 3 else "amber" if scrap_this < 5 else "red",
            icon=get_svg(SCRAP, color="#2ecc71" if scrap_this < 3 else "#f39c12" if scrap_this < 5 else "#e74c3c", size=24),
        )

    with c2:
        kpi_card(
            label="OEE",
            value=f"{oee_val:.1f}",
            suffix="%",
            delta=f"{'+' if oee_val >= 85 else ''}{oee_val - 85:.1f}%",
            delta_label="vs hedef (85%)",
            color="green" if oee_val >= 85 else "amber" if oee_val >= 65 else "red",
            icon=get_svg(OEE, color="#4f8ef7", size=24),
        )

    with c3:
        kpi_card(
            label="Kritik CAPA (Açık)",
            value=str(critical_open),
            delta=f"Toplam {critical_prev} kritik",
            delta_label="",
            color="green" if critical_open == 0 else "amber" if critical_open <= 3 else "red",
            icon=get_svg(ALERT, color="#e74c3c", size=24),
        )

    with c4:
        cpk_val = cpk_data.get("cpk", 0.0)
        cpk_card(cpk_val)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts Row ───────────────────────────────────────────────────────────
    section_header("Trend & Dağılım")
    col_chart1, col_chart2 = st.columns([3, 2])

    with col_chart1:
        trend_data = get_30_day_trend(all_defects)
        fig_trend = scrap_trend_chart(trend_data, threshold=3.0)
        st.plotly_chart(fig_trend, width='stretch', config={"displayModeBar": False})

    with col_chart2:
        fig_donut = defect_donut_chart(this_month_defects)
        st.plotly_chart(fig_donut, width='stretch', config={"displayModeBar": False})

    st.markdown("<br>", unsafe_allow_html=True)

    # ── OEE Gauge + Summary Stats ────────────────────────────────────────────
    section_header("OEE Detayı & Özet")
    col_oee, col_summary = st.columns([1, 2])

    with col_oee:
        fig_gauge = oee_gauge(oee_val, target=85.0)
        st.plotly_chart(fig_gauge, width='stretch', config={"displayModeBar": False})
        st.caption(f"Kullanılabilirlik: 92% | Performans: 89% | Kalite: {oee_quality*100:.1f}%")

    with col_summary:
        st.markdown(f"##### {get_svg(SUMMARY)} Özet Tablo", unsafe_allow_html=True)
        summary_data = {
            "Gösterge": [
                "Bu Ay Toplam Hata", "Bu Ay Toplam Üretim",
                "30 Gün Hata Adedi", "Açık CAPA Sayısı",
                "Cpk (Son 25 ölçüm)", "OEE"
            ],
            "Değer": [
                f"{sum(d['quantity'] for d in this_month_defects):,}",
                f"{sum(d['total_produced'] for d in this_month_defects):,}",
                f"{sum(d['quantity'] for d in last_30_defects):,}",
                f"{sum(1 for c in capa_all if c['status'] != 'Closed')}",
                f"{cpk_data.get('cpk', 0):.3f}",
                f"{oee_val:.1f}%",
            ],
        }
        df_summary = pd.DataFrame(summary_data)
        st.dataframe(df_summary, hide_index=True, width='stretch')


show()
