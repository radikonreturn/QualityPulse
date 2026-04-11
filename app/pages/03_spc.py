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
from components.icons import SPC, ALERT, CHECK, SUMMARY, PLUS, SAVE, get_svg


def show():
    inject_css()
    page_header(f"{get_svg(SPC, size=32)} SPC Kontrol Grafiği", "İstatistiksel süreç kontrolü — X-bar grafiği ve Nelson kuralları")

    # ── Controls ─────────────────────────────────────────────────────────────
    points = get_measurement_points()
    if not points:
        st.warning("Henüz ölçüm verisi yok. Önce veri tabanını seed.py ile doldurun.")
        return

    section_header("Veri Seçimi")
    col_pt, col_n = st.columns([2, 1])
    with col_pt:
        selected_point = st.selectbox("Ölçüm Noktası", options=points, key="spc_point")
    with col_n:
        n_obs = st.slider("Gözlem Sayısı", min_value=10, max_value=100, value=25, step=5, key="spc_n")

    # ── Load measurements ────────────────────────────────────────────────────
    rows = get_measurements(measurement_point=selected_point, limit=n_obs)
    if len(rows) < 5:
        st.info("Seçilen ölçüm noktası için yeterli veri yok (min 5 kayıt).")
        return

    values = [r["value"] for r in rows]
    timestamps = [r["timestamp"] for r in rows]
    usl = rows[0]["tolerance_upper"]
    lsl = rows[0]["tolerance_lower"]
    nominal = rows[0]["nominal"]

    # Reverse so oldest → newest
    values = list(reversed(values))
    timestamps = list(reversed(timestamps))

    # ── SPC Calculations ─────────────────────────────────────────────────────
    limits = calculate_control_limits(values)
    cl  = limits["mean"]
    ucl = limits["ucl"]
    lcl = limits["lcl"]
    ooc = get_ooc_indices(values, ucl, lcl, cl)

    # ── Chart ─────────────────────────────────────────────────────────────────
    fig = spc_chart(
        values=values,
        timestamps=timestamps,
        cl=cl, ucl=ucl, lcl=lcl,
        usl=usl, lsl=lsl,
        ooc_indices=ooc,
        point_name=selected_point,
    )
    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

    # Nelson violations alert
    if ooc:
        st.markdown(f'<div style="background-color:#fee2e2;color:#991b1b;padding:12px;border-radius:8px;margin-bottom:1rem;display:flex;align-items:center;gap:8px;">{get_svg(ALERT, color="#991b1b")} {len(ooc)} kontrol dışı nokta tespit edildi (Nelson Kural 1 & 2). İndeksler: {ooc[:10]}{"..." if len(ooc) > 10 else ""}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="background-color:#d1fae5;color:#065f46;padding:12px;border-radius:8px;margin-bottom:1rem;display:flex;align-items:center;gap:8px;">{get_svg(CHECK, color="#065f46")} Tüm noktalar kontrol sınırları içinde. Süreç kararlı görünüyor.</div>', unsafe_allow_html=True)

    # ── Capability Summary ────────────────────────────────────────────────────
    section_header("Yetenek Özeti")
    cap = calculate_cpk(values, usl, lsl)

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Cp",    f"{cap['cp']:.3f}")
    col2.metric("Cpk",   f"{cap['cpk']:.3f}")
    col3.metric("Ortalama",  f"{cap['mean']:.4f}")
    col4.metric("σ",    f"{cap['sigma']:.4f}")
    col5.metric("Min",  f"{min(values):.4f}")
    col6.metric("Max",  f"{max(values):.4f}")

    st.markdown(f"""
    <div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:0.6rem;">
        <span style="background:#f0f2f5;padding:4px 12px;border-radius:6px;font-size:0.82rem;">
            <b>Nominal:</b> {nominal}
        </span>
        <span style="background:#f0f2f5;padding:4px 12px;border-radius:6px;font-size:0.82rem;">
            <b>USL:</b> {usl}
        </span>
        <span style="background:#f0f2f5;padding:4px 12px;border-radius:6px;font-size:0.82rem;">
            <b>LSL:</b> {lsl}
        </span>
        <span style="background:#f0f2f5;padding:4px 12px;border-radius:6px;font-size:0.82rem;">
            <b>UCL:</b> {ucl:.4f}
        </span>
        <span style="background:#f0f2f5;padding:4px 12px;border-radius:6px;font-size:0.82rem;">
            <b>LCL:</b> {lcl:.4f}
        </span>
        <span style="background:#f0f2f5;padding:4px 12px;border-radius:6px;font-size:0.82rem;">
            <b>n:</b> {len(values)}
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Cpk status
    cpk_val = cap["cpk"]
    if cpk_val >= 1.33:
        st.markdown(f'<div style="background-color:#d1fae5;color:#065f46;padding:12px;border-radius:8px;margin-top:1rem;display:flex;align-items:center;gap:8px;">{get_svg(CHECK, color="#065f46")} Cpk = {cpk_val:.3f} — Süreç kapasiteli (≥ 1.33)</div>', unsafe_allow_html=True)
    elif cpk_val >= 1.00:
        st.markdown(f'<div style="background-color:#fef3c7;color:#92400e;padding:12px;border-radius:8px;margin-top:1rem;display:flex;align-items:center;gap:8px;">{get_svg(ALERT, color="#92400e")} Cpk = {cpk_val:.3f} — Sınırda kapasite (1.00–1.33)</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="background-color:#fee2e2;color:#991b1b;padding:12px;border-radius:8px;margin-top:1rem;display:flex;align-items:center;gap:8px;">{get_svg(ALERT, color="#991b1b")} Cpk = {cpk_val:.3f} — Yetersiz kapasite (< 1.00). Acil iyileştirme gerekli!</div>', unsafe_allow_html=True)

    # ── Recent Measurements Table ─────────────────────────────────────────────
    with st.expander(f"Ölçüm Verisi Tablosu", expanded=False):
        st.markdown(f"### {get_svg(SUMMARY)} Veri Listesi", unsafe_allow_html=True)
        df = pd.DataFrame(rows[::-1])
        df_disp = df[["timestamp", "line", "measurement_point", "value",
                       "nominal", "tolerance_upper", "tolerance_lower"]].copy()
        df_disp.columns = ["Zaman", "Hat", "Nokta", "Değer", "Nominal", "USL", "LSL"]
        df_disp["Sapma"] = (df_disp["Değer"] - df_disp["Nominal"]).round(4)
        st.dataframe(df_disp, hide_index=True, width='stretch')

    # ── Add Measurement Form ──────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Yeni Ölçüm Ekle")
    with st.expander(f"Ölçüm Formu", expanded=False):
        st.markdown(f"### {get_svg(PLUS)} Yeni Kayıt", unsafe_allow_html=True)
        with st.form("add_measurement_form"):
            fc1, fc2 = st.columns(2)
            with fc1:
                form_line = st.selectbox("Hat", options=get_lines(), key="form_line")
                form_point = st.selectbox("Ölçüm Noktası", options=points, key="form_point")
                form_value = st.number_input("Ölçüm Değeri", format="%.4f", key="form_value")
            with fc2:
                form_nominal = st.number_input("Nominal", format="%.4f", key="form_nominal")
                form_usl = st.number_input("Üst Tolerans (USL)", format="%.4f", key="form_usl")
                form_lsl = st.number_input("Alt Tolerans (LSL)", format="%.4f", key="form_lsl")

            submitted = st.form_submit_button("Kaydet", use_container_width=True)
            if submitted:
                if form_usl <= form_lsl:
                    st.error("USL, LSL'den büyük olmalıdır.")
                else:
                    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    insert_measurement(ts, form_line, form_point,
                                        form_value, form_nominal, form_usl, form_lsl)
                    st.success(f"Ölçüm kaydedildi: {form_point} = {form_value:.4f}")
                    st.rerun()


show()
