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
    with st.container(border=True):
        col_start, col_end, col_line = st.columns([1, 1, 1])
        with col_start:
            start_date = st.date_input("Başlangıç", value=date.today() - timedelta(days=30))
        with col_end:
            end_date = st.date_input("Bitiş", value=date.today())
        with col_line:
            lines = ["Tümü"] + get_lines()
            selected_line = st.selectbox("Üretim Hattı", options=lines)

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
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        fig = pareto_chart(defects)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ── Summary Stats ─────────────────────────────────────────────────────────
    agg = df.groupby("defect_type")["quantity"].sum().reset_index()
    agg = agg.sort_values("quantity", ascending=False)
    agg["kümülatif_%"] = (agg["quantity"].cumsum() / agg["quantity"].sum() * 100).round(1)
    agg["oran_%"] = (agg["quantity"] / agg["quantity"].sum() * 100).round(1)
    agg.columns = ["Hata Türü", "Adet", "Kümülatif %", "Pay %"]

    st.markdown("<br>", unsafe_allow_html=True)
    col_tbl, col_meta = st.columns([2, 1])
    
    with col_tbl:
        with st.container(border=True):
            section_header("Özet Tablo")
            st.dataframe(agg, hide_index=True, use_container_width=True)

    with col_meta:
        with st.container(border=True):
            section_header("Dönem Verileri")
            total_def = df["quantity"].sum()
            total_prod = df["total_produced"].sum()
            scrap_rate = total_def / total_prod * 100 if total_prod > 0 else 0
            
            m1, m2 = st.columns(2)
            m1.metric("Toplam Hata", f"{total_def:,}")
            m2.metric("Hurda Oranı", f"{scrap_rate:.2f}%")
            
            m3, m4 = st.columns(2)
            m3.metric("Kayıt", len(df))
            m4.metric("Üretim", f"{total_prod:,}")

    # ── Detailed Table ────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("Detaylı Hata Kayıt Listesi", expanded=False, icon=":material/list:"):
        df_display = df[["date", "shift", "line", "defect_type", "quantity", "total_produced", "notes"]].copy()
        df_display.columns = ["Tarih", "Vardiya", "Hat", "Hata Türü", "Adet", "Üretim", "Not"]
        st.dataframe(df_display.sort_values("Tarih", ascending=False), hide_index=True, use_container_width=True)

    # ── Drill-Down ────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        section_header("Hata Türü Bazlı Derinleme")
        defect_types = sorted(df["defect_type"].unique().tolist())
        selected_type = st.selectbox("Hata türü seçin:", defect_types)

        if selected_type:
            filtered = df[df["defect_type"] == selected_type].copy()
            filtered = filtered[["date", "shift", "line", "quantity", "total_produced", "notes"]].copy()
            filtered.columns = ["Tarih", "Vardiya", "Hat", "Adet", "Üretim", "Not"]
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Kayıt Sayısı", len(filtered))
            c2.metric("Toplam Adet", f"{filtered['Adet'].sum():,}")
            c3.metric("Ortalama Günlük", f"{filtered['Adet'].mean():.1f}")
            
            st.dataframe(filtered.sort_values("Tarih", ascending=False), hide_index=True, use_container_width=True)


show()
