"""
QualityPulse — Page 2: Pareto Analizi
Date/line filters, Pareto combo chart, defect table, and drill-down.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date

from db.database import get_defects, get_lines
from components.styles import inject_css, page_header, section_header
from components.charts import pareto_chart
from components.icons import PARETO, get_svg


def show():
    inject_css()
    page_header(f"{get_svg(PARETO, size=32)} Pareto Analizi", "Hata türlerinin frekans ve kümülatif etki analizi")

    # ── Filter Bar ───────────────────────────────────────────────────────────
    section_header("Filtreler")
    col_start, col_end, col_line = st.columns([1, 1, 1])

    with col_start:
        start_date = st.date_input(
            "Başlangıç Tarihi",
            value=date.today() - timedelta(days=30),
            key="pareto_start",
        )
    with col_end:
        end_date = st.date_input(
            "Bitiş Tarihi",
            value=date.today(),
            key="pareto_end",
        )
    with col_line:
        lines = ["Tümü"] + get_lines()
        selected_line = st.selectbox("Hat", options=lines, key="pareto_line")

    if start_date > end_date:
        st.error("Başlangıç tarihi bitiş tarihinden büyük olamaz.")
        return

    # ── Load data ────────────────────────────────────────────────────────────
    defects = get_defects(
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        line=selected_line,
    )

    if not defects:
        st.info("Seçilen filtreler için kayıt bulunamadı.")
        return

    df = pd.DataFrame(defects)

    # ── Pareto Chart ─────────────────────────────────────────────────────────
    section_header("Pareto Grafiği")
    fig = pareto_chart(defects)
    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

    # ── Summary Stats ─────────────────────────────────────────────────────────
    agg = df.groupby("defect_type")["quantity"].sum().reset_index()
    agg = agg.sort_values("quantity", ascending=False)
    agg["kümülatif_%"] = (agg["quantity"].cumsum() / agg["quantity"].sum() * 100).round(1)
    agg["oran_%"] = (agg["quantity"] / agg["quantity"].sum() * 100).round(1)
    agg.columns = ["Hata Türü", "Toplam Adet", "Kümülatif %", "Pay %"]

    col_tbl, col_meta = st.columns([2, 1])
    with col_tbl:
        section_header("Özet Tablo")
        st.dataframe(agg, hide_index=True, width='stretch')

    with col_meta:
        section_header("Dönem Özeti")
        total_def = df["quantity"].sum()
        total_prod = df["total_produced"].sum()
        scrap_rate = total_def / total_prod * 100 if total_prod > 0 else 0
        st.metric("Toplam Hata", f"{total_def:,}")
        st.metric("Toplam Üretim", f"{total_prod:,}")
        st.metric("Hurda Oranı", f"{scrap_rate:.2f}%")
        st.metric("Kayıt Sayısı", f"{len(df)}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Detailed Table ────────────────────────────────────────────────────────
    section_header("Detaylı Hata Kayıtları")

    # Column rename for display
    df_display = df[["date", "shift", "line", "defect_type", "quantity", "total_produced", "notes"]].copy()
    df_display.columns = ["Tarih", "Vardiya", "Hat", "Hata Türü", "Adet", "Toplam Üretim", "Not"]
    df_display = df_display.sort_values("Tarih", ascending=False)
    st.dataframe(df_display, hide_index=True, width='stretch', height=280)

    # ── Drill-Down ────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Hata Türü Detayı")
    defect_types = sorted(df["defect_type"].unique().tolist())
    selected_type = st.selectbox("Hata türü seçin:", defect_types, key="pareto_drilldown")

    if selected_type:
        filtered = df[df["defect_type"] == selected_type].copy()
        filtered = filtered[["date", "shift", "line", "quantity", "total_produced", "notes"]].copy()
        filtered.columns = ["Tarih", "Vardiya", "Hat", "Adet", "Toplam Üretim", "Not"]
        filtered = filtered.sort_values("Tarih", ascending=False)

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Toplam Kayıt", len(filtered))
        col_b.metric("Toplam Adet", f"{filtered['Adet'].sum():,}")
        col_c.metric("Ortalama Günlük", f"{filtered['Adet'].mean():.1f}")

        st.dataframe(filtered, hide_index=True, width='stretch', height=260)


show()
