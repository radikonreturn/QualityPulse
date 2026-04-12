"""
QualityPulse — Page 3: SPC Kontrol Grafiği
X-bar chart with Nelson rules, capability summary, and add-measurement form.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
from datetime import datetime

from db.database import get_measurements, get_measurement_points, insert_measurement, get_lines
from utils.spc_engine import calculate_control_limits, get_ooc_indices, calculate_cpk
from components.styles import inject_css, page_header, section_header
from components.charts import spc_chart
from components.icons import SPC, ALERT, CHECK, get_svg


def show():
    inject_css()
    page_header(f"{get_svg(SPC, size=32)} SPC Kontrol Grafiği", "İstatistiksel süreç kontrolü ve Nelson kuralları")

    # ── Controls ─────────────────────────────────────────────────────────────
    points = get_measurement_points()
    if not points:
        st.warning("Henüz ölçüm verisi yok. Önce veri tabanını seed.py ile doldurun.")
        return

    with st.container(border=True):
        col_pt, col_n = st.columns([2, 1])
        with col_pt:
            selected_point = st.selectbox("Ölçüm Noktası", options=points)
        with col_n:
            n_obs = st.slider("Son Gözlem Sayısı", 10, 100, 25, 5)

    # ── Load measurements ────────────────────────────────────────────────────
    rows = get_measurements(measurement_point=selected_point, limit=n_obs)
    if len(rows) < 5:
        st.info("Seçilen ölçüm noktası için yeterli veri yok (min 5 kayıt).")
        return

    values = list(reversed([r["value"] for r in rows]))
    timestamps = list(reversed([r["timestamp"] for r in rows]))
    usl, lsl, nominal = rows[0]["tolerance_upper"], rows[0]["tolerance_lower"], rows[0]["nominal"]

    # ── SPC Calculations ─────────────────────────────────────────────────────
    limits = calculate_control_limits(values)
    cl, ucl, lcl = limits["mean"], limits["ucl"], limits["lcl"]
    ooc = get_ooc_indices(values, ucl, lcl, cl)

    # ── Chart ─────────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        fig = spc_chart(values, timestamps, cl, ucl, lcl, usl, lsl, ooc, selected_point)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        if ooc:
            st.markdown(f"""
            <div style="background:#fee2e2;color:#991b1b;padding:12px;border-radius:10px;display:flex;align-items:center;gap:10px;font-size:0.9rem;">
                {get_svg(ALERT, color="#991b1b", size=20)} 
                <b>{len(ooc)} Kontrol Dışı Nokta:</b> Nelson Kural ihlali tespit edildi.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:#ecfdf5;color:#065f46;padding:12px;border-radius:10px;display:flex;align-items:center;gap:10px;font-size:0.9rem;">
                {get_svg(CHECK, color="#065f46", size=20)} 
                <b>Süreç Kararlı:</b> Tüm noktalar kontrol sınırları içerisinde.
            </div>
            """, unsafe_allow_html=True)

    # ── Capability Summary ────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        section_header("Süreç Yetenek Analizi")
        cap = calculate_cpk(values, usl, lsl)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Cp", f"{cap['cp']:.3f}")
        c2.metric("Cpk", f"{cap['cpk']:.3f}", delta=f"{'Kapasiteli' if cap['cpk']>=1.33 else 'Yetersiz'}")
        c3.metric("Ortalama", f"{cap['mean']:.4f}")
        c4.metric("Standart Sapma", f"{cap['sigma']:.4f}")

        # Specs row
        st.markdown(f"""
        <div style="display:flex;gap:12px;margin-top:15px;padding-top:15px;border-top:1px solid #f1f5f9;">
            <div style="font-size:0.8rem;color:#64748b;"><b>USL:</b> {usl}</div>
            <div style="font-size:0.8rem;color:#64748b;"><b>Nominal:</b> {nominal}</div>
            <div style="font-size:0.8rem;color:#64748b;"><b>LSL:</b> {lsl}</div>
            <div style="font-size:0.8rem;color:#64748b;margin-left:auto;"><b>N:</b> {len(values)}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Tables & Forms ────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    col_t, col_f = st.columns([1, 1])

    with col_t:
        with st.expander("Ölçüm Listesi", expanded=False, icon=":material/list:"):
            df = pd.DataFrame(rows[::-1])
            df_disp = df[["timestamp", "line", "value", "nominal"]].copy()
            df_disp.columns = ["Zaman", "Hat", "Değer", "Nominal"]
            st.dataframe(df_disp, hide_index=True, use_container_width=True)

    with col_f:
        with st.expander("Yeni Veri Girişi", expanded=False, icon=":material/add_circle:"):
            with st.form("add_measurement_form", clear_on_submit=True):
                f_line = st.selectbox("Hat", options=get_lines())
                f_point = st.selectbox("Nokta", options=points)
                f_val = st.number_input("Ölçüm", format="%.4f")
                
                if st.form_submit_button("Kaydet", use_container_width=True):
                    insert_measurement(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                                       f_line, f_point, f_val, nominal, usl, lsl)
                    st.toast("Veri başarıyla kaydedildi!")
                    st.rerun()


show()
