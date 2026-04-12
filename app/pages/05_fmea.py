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
from components.icons import FMEA, get_svg

PROCESS_STEPS = [
    "Eritme", "Döküm", "Kalıp Kapatma", "Basınç Uygulama",
    "Soğutma", "Kalıp Açma", "Parça Çıkarma", "Çapak Alma",
    "Yüzey İşleme", "Kalite Kontrol",
]
OWNERS = ["Ahmet Yılmaz", "Fatma Demir", "Mehmet Kaya", "Ayşe Çelik", "Hasan Öztürk"]


def show():
    inject_css()
    page_header(f"{get_svg(FMEA, size=32)} FMEA Analizi", "Hata modu ve etkileri yönetimi")

    fmea_all = get_all_fmea()

    # ── Summary ───────────────────────────────────────────────────────────────
    high   = sum(1 for r in fmea_all if r["rpn"] > 200)
    medium = sum(1 for r in fmea_all if 100 <= r["rpn"] <= 200)
    low    = sum(1 for r in fmea_all if r["rpn"] < 100)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Yüksek Risk", high, delta="RPN > 200", delta_color="inverse")
    col2.metric("Orta Risk", medium, delta="100-200")
    col3.metric("Düşük Risk", low, delta="RPN < 100")
    col4.metric("Toplam Kayıt", len(fmea_all))

    # ── Heatmap ───────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        fig = fmea_heatmap(fmea_all)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ── Table ─────────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        section_header("FMEA Kayıt Listesi")
        if not fmea_all:
            st.info("Kayıt bulunamadı.")
        else:
            df = pd.DataFrame(fmea_all)
            df_disp = df[["id", "process_step", "failure_mode", "rpn", "responsible", "status"]].copy()
            df_disp.columns = ["ID", "Proses Adımı", "Hata Modu", "RPN", "Sorumlu", "Durum"]
            st.dataframe(df_disp.sort_values("RPN", ascending=False), hide_index=True, use_container_width=True, height=350)

    # ── Forms ─────────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    fa1, fa2 = st.columns(2)
    
    with fa1:
        with st.expander("Yeni FMEA Kaydı", expanded=False, icon=":material/add_circle:"):
            with st.form("add_fmea_form", clear_on_submit=True):
                f_step = st.selectbox("Proses Adımı", PROCESS_STEPS)
                f_mode = st.text_input("Hata Modu *")
                f_effect = st.text_input("Hata Etkisi")
                
                c1, c2, c3 = st.columns(3)
                s = c1.slider("S", 1, 10, 5)
                o = c2.slider("O", 1, 10, 5)
                d = c3.slider("T", 1, 10, 5)
                
                rpn = s * o * d
                st.info(f"Hesaplanan RPN: {rpn}")
                
                f_owner = st.selectbox("Sorumlu", OWNERS)
                
                if st.form_submit_button("Kaydet", use_container_width=True):
                    if f_mode:
                        insert_fmea(f_step, f_mode, f_effect, s, o, d, None, None, f_owner, "Open")
                        st.toast("FMEA kaydedildi!")
                        st.rerun()
                    else:
                        st.error("Hata Modu zorunludur.")

    with fa2:
        with st.expander("Kayıt Güncelle", expanded=False, icon=":material/update:"):
            if fmea_all:
                id_map = {f"#{r['id']} - {r['process_step']}: {r['failure_mode']}": r for r in fmea_all}
                sel_fmea = st.selectbox("Güncellenecek Kayıt", options=list(id_map.keys()))
                rec = id_map[sel_fmea]
                
                with st.form("edit_fmea_form"):
                    e_status = st.selectbox("Yeni Durum", ["Open", "In Progress", "Closed"], 
                                            index=["Open", "In Progress", "Closed"].index(rec["status"]))
                    e_act = st.text_area("Önerilen Aksiyon", value=rec.get("recommended_action") or "")
                    
                    if st.form_submit_button("Güncelle", use_container_width=True):
                        update_fmea(rec["id"], status=e_status, recommended_action=e_act)
                        st.toast("Kayıt güncellendi!")
                        st.rerun()


show()
