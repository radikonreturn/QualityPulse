"""
QualityPulse — Page 5: FMEA Risk Matrisi
Risk summary cards, heatmap, sorted table with RPN coloring, add/edit form.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd

from db.database import get_all_fmea, insert_fmea, update_fmea
from components.styles import inject_css, page_header, section_header
from components.charts import fmea_heatmap
from components.icons import FMEA, CIRCLE_RED, CIRCLE_YELLOW, CIRCLE_GREEN, SUMMARY, PLUS, SAVE, get_svg

PROCESS_STEPS = [
    "Eritme", "Döküm", "Kalıp Kapatma", "Basınç Uygulama",
    "Soğutma", "Kalıp Açma", "Parça Çıkarma", "Çapak Alma",
    "Yüzey İşleme", "Kalite Kontrol",
]
OWNERS = ["Ahmet Yılmaz", "Fatma Demir", "Mehmet Kaya", "Ayşe Çelik", "Hasan Öztürk"]


def rpn_badge(rpn: int) -> str:
    """Return colored badge HTML for RPN value."""
    if rpn > 200:
        bg, fg = "#fee2e2", "#991b1b"
        label = "Yüksek"
    elif rpn >= 100:
        bg, fg = "#fef3c7", "#92400e"
        label = "Orta"
    else:
        bg, fg = "#d1fae5", "#065f46"
        label = "Düşük"
    return f'<span style="background:{bg};color:{fg};padding:2px 10px;border-radius:12px;font-size:0.78rem;font-weight:700;">{rpn} — {label}</span>'


def show():
    inject_css()
    page_header(f"{get_svg(FMEA, size=32)} FMEA Risk Matrisi", "Hata Modu ve Etkileri Analizi — proses adımları & RPN değerlendirmesi")

    fmea_all = get_all_fmea()

    # ── Risk Summary Cards ────────────────────────────────────────────────────
    section_header("Risk Dağılımı")
    high   = sum(1 for r in fmea_all if r["rpn"] > 200)
    medium = sum(1 for r in fmea_all if 100 <= r["rpn"] <= 200)
    low    = sum(1 for r in fmea_all if r["rpn"] < 100)
    total  = len(fmea_all)

    col1, col2, col3, col4 = st.columns(4)
    # Note: st.metric doesn't support complex HTML well in label, using plain text for label
    # but we can use st.markdown above them if needed. 
    # For now, keeping labels clean but removing emojis.
    col1.metric("Yüksek Risk (RPN>200)", high)
    col2.metric("Orta Risk (100–200)", medium)
    col3.metric("Düşük Risk (<100)", low)
    col4.metric("Toplam FMEA Kaydı", total)

    # ── Heatmap ───────────────────────────────────────────────────────────────
    section_header("Risk Matrisi — Şiddet × Oluşma")
    fig = fmea_heatmap(fmea_all)
    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

    # ── FMEA Table ─────────────────────────────────────────────────────────────
    section_header("FMEA Kayıt Tablosu (RPN'e Göre Sıralı)")

    if not fmea_all:
        st.info("Henüz FMEA kaydı yok.")
    else:
        df = pd.DataFrame(fmea_all)

        # RPN color function for Styler
        def color_rpn(val):
            if val > 200:
                return "background-color: #fee2e2; color: #991b1b; font-weight: 700"
            elif val >= 100:
                return "background-color: #fef3c7; color: #92400e; font-weight: 700"
            else:
                return "background-color: #d1fae5; color: #065f46; font-weight: 700"

        df_disp = df[["id", "process_step", "failure_mode", "failure_effect",
                        "severity", "occurrence", "detection", "rpn",
                        "current_controls", "recommended_action", "responsible", "status"]].copy()
        df_disp.columns = ["ID", "Proses Adımı", "Hata Modu", "Hata Etkisi",
                            "Ş", "O", "T", "RPN",
                            "Mevcut Kontroller", "Önerilen Aksiyon", "Sorumlu", "Durum"]

        styled = df_disp.style.map(color_rpn, subset=["RPN"])
        st.dataframe(styled, hide_index=True, width='stretch', height=400)

    # ── Add New FMEA ───────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Yeni FMEA Satırı Ekle")
    with st.expander("FMEA Oluştur", expanded=False):
        st.markdown(f"### {get_svg(PLUS)} Yeni Analiz", unsafe_allow_html=True)
        with st.form("add_fmea_form"):
            fc1, fc2 = st.columns(2)
            with fc1:
                fmea_step   = st.selectbox("Proses Adımı *", PROCESS_STEPS, key="fmea_step")
                fmea_mode   = st.text_input("Hata Modu *", key="fmea_mode")
                fmea_effect = st.text_input("Hata Etkisi *", key="fmea_effect")
                fmea_owner  = st.selectbox("Sorumlu *", OWNERS, key="fmea_owner")
                fmea_status = st.selectbox("Durum", ["Open", "In Progress", "Closed"], key="fmea_status")
            with fc2:
                fmea_sev = st.slider("Şiddet (S)", 1, 10, 5, key="fmea_s")
                fmea_occ = st.slider("Oluşma (O)", 1, 10, 5, key="fmea_o")
                fmea_det = st.slider("Tespit (T)", 1, 10, 5, key="fmea_d")

                live_rpn = fmea_sev * fmea_occ * fmea_det
                rpn_color = "#fee2e2" if live_rpn > 200 else "#fef3c7" if live_rpn >= 100 else "#d1fae5"
                rpn_text  = "#991b1b" if live_rpn > 200 else "#92400e" if live_rpn >= 100 else "#065f46"
                st.markdown(
                    f'<div style="background:{rpn_color};color:{rpn_text};padding:10px 16px;'
                    f'border-radius:10px;font-size:1.3rem;font-weight:800;margin-top:8px;">'
                    f'RPN = {live_rpn}</div>',
                    unsafe_allow_html=True
                )
                fmea_controls = st.text_area("Mevcut Kontroller", height=60, key="fmea_ctrl")
                fmea_action   = st.text_area("Önerilen Aksiyon", height=60, key="fmea_act")

            submitted = st.form_submit_button("FMEA Kaydet", use_container_width=True)
            if submitted:
                if not (fmea_mode and fmea_effect):
                    st.error("Hata Modu ve Hata Etkisi zorunludur.")
                else:
                    insert_fmea(
                        fmea_step, fmea_mode, fmea_effect,
                        fmea_sev, fmea_occ, fmea_det,
                        fmea_controls or None,
                        fmea_action or None,
                        fmea_owner, fmea_status,
                    )
                    st.success(f"FMEA kaydedildi. RPN = {live_rpn}")
                    st.rerun()

    # ── Edit Existing FMEA ─────────────────────────────────────────────────────
    if fmea_all:
        st.markdown("<br>", unsafe_allow_html=True)
        section_header("FMEA Kaydı Güncelle")
        with st.expander("Mevcut FMEA Güncelle", expanded=False):
            st.markdown(f"### {get_svg(SAVE)} Kayıt Güncelle", unsafe_allow_html=True)
            id_map = {f"#{r['id']} — {r['process_step']}: {r['failure_mode']} (RPN={r['rpn']})": r
                       for r in fmea_all}
            sel_label = st.selectbox("Kayıt Seç", options=list(id_map.keys()), key="edit_fmea_sel")
            rec = id_map[sel_label]

            with st.form("edit_fmea_form"):
                ec1, ec2 = st.columns(2)
                with ec1:
                    e_step   = st.selectbox("Proses Adımı", PROCESS_STEPS,
                                             index=PROCESS_STEPS.index(rec["process_step"]) if rec["process_step"] in PROCESS_STEPS else 0,
                                             key="edit_step")
                    e_mode   = st.text_input("Hata Modu", value=rec["failure_mode"], key="edit_mode")
                    e_effect = st.text_input("Hata Etkisi", value=rec["failure_effect"], key="edit_effect")
                    e_owner  = st.selectbox("Sorumlu", OWNERS,
                                             index=OWNERS.index(rec["responsible"]) if rec["responsible"] in OWNERS else 0,
                                             key="edit_owner")
                    e_status = st.selectbox("Durum", ["Open", "In Progress", "Closed"],
                                             index=["Open", "In Progress", "Closed"].index(rec["status"]),
                                             key="edit_status")
                with ec2:
                    e_sev = st.slider("Şiddet (S)", 1, 10, int(rec["severity"]), key="edit_s")
                    e_occ = st.slider("Oluşma (O)", 1, 10, int(rec["occurrence"]), key="edit_o")
                    e_det = st.slider("Tespit (T)", 1, 10, int(rec["detection"]), key="edit_d")
                    edit_rpn = e_sev * e_occ * e_det
                    rpn_color = "#fee2e2" if edit_rpn > 200 else "#fef3c7" if edit_rpn >= 100 else "#d1fae5"
                    rpn_text  = "#991b1b" if edit_rpn > 200 else "#92400e" if edit_rpn >= 100 else "#065f46"
                    st.markdown(
                        f'<div style="background:{rpn_color};color:{rpn_text};padding:10px 16px;'
                        f'border-radius:10px;font-size:1.3rem;font-weight:800;margin-top:8px;">'
                        f'RPN = {edit_rpn}</div>',
                        unsafe_allow_html=True
                    )
                    e_ctrl = st.text_area("Mevcut Kontroller", value=rec.get("current_controls") or "", key="edit_ctrl")
                    e_act  = st.text_area("Önerilen Aksiyon", value=rec.get("recommended_action") or "", key="edit_act")

                if st.form_submit_button("Güncelle", use_container_width=True):
                    update_fmea(
                        rec["id"],
                        process_step=e_step, failure_mode=e_mode,
                        failure_effect=e_effect, severity=e_sev,
                        occurrence=e_occ, detection=e_det,
                        current_controls=e_ctrl or None,
                        recommended_action=e_act or None,
                        responsible=e_owner, status=e_status,
                    )
                    st.success(f"FMEA #{rec['id']} güncellendi. Yeni RPN = {edit_rpn}")
                    st.rerun()


show()
