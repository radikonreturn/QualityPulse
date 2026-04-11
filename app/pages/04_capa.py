"""
QualityPulse — Page 4: CAPA Takibi
Summary cards, filter bar, color-coded table, add/update forms, overdue detection.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
from datetime import datetime, date

from db.database import get_all_capa, insert_capa, update_capa_status
from components.styles import inject_css, page_header, section_header
from utils.calculations import count_overdue_capa
from components.icons import CAPA, CIRCLE_RED, CIRCLE_YELLOW, CIRCLE_GREEN, ALERT, PLUS, SAVE, CHECK, get_svg


STATUS_COLORS = {
    "Open":        (CIRCLE_RED, "#fef2f2", "#991b1b"),
    "In Progress": (CIRCLE_YELLOW, "#fffbeb", "#92400e"),
    "Closed":      (CIRCLE_GREEN, "#ecfdf5", "#065f46"),
}

OWNERS = ["Ahmet Yılmaz", "Fatma Demir", "Mehmet Kaya", "Ayşe Çelik", "Hasan Öztürk"]


def show():
    inject_css()
    page_header(f"{get_svg(CAPA, size=32)} CAPA Takibi", "Düzeltici ve Önleyici Faaliyet yönetimi")

    capa_all = get_all_capa()

    # ── Summary Cards ─────────────────────────────────────────────────────────
    open_cnt = sum(1 for c in capa_all if c["status"] == "Open")
    prog_cnt = sum(1 for c in capa_all if c["status"] == "In Progress")
    closed_cnt = sum(1 for c in capa_all if c["status"] == "Closed")
    overdue_cnt = count_overdue_capa(capa_all)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Açık", open_cnt)
    col2.metric("Devam Eden", prog_cnt)
    col3.metric("Kapalı", closed_cnt)
    col4.metric("Gecikmiş", overdue_cnt, delta=f"-{overdue_cnt}" if overdue_cnt else None, delta_color="inverse")

    # ── Filter Bar ────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        fc1, fc2, fc3 = st.columns([1, 1, 1.5])
        with fc1:
            status_filter = st.multiselect("Durum", ["Open", "In Progress", "Closed"], ["Open", "In Progress"])
        with fc2:
            crit_filter = st.multiselect("Kritiklik", ["Critical", "Major", "Minor"], ["Critical", "Major", "Minor"])
        with fc3:
            owner_search = st.text_input("Sorumlu / Başlık Ara", placeholder="Arama yapın...")

    filtered = get_all_capa(
        status_filter=status_filter if status_filter else None,
        criticality_filter=crit_filter if crit_filter else None,
        owner_search=owner_search,
    )

    # ── Table View ────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        section_header(f"Faaliyet Listesi ({len(filtered)})")
        if not filtered:
            st.info("Kayıt bulunamadı.")
        else:
            df = pd.DataFrame(filtered)
            df["overdue"] = (df["due_date"] < date.today().strftime("%Y-%m-%d")) & (df["status"] != "Closed")
            
            df_disp = df[["id", "title", "owner", "criticality", "status", "due_date"]].copy()
            df_disp.columns = ["ID", "Başlık", "Sorumlu", "Önem", "Durum", "Vade"]
            
            st.dataframe(df_disp, hide_index=True, use_container_width=True, height=300)

    # ── Actions ───────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    ca1, ca2 = st.columns(2)
    
    with ca1:
        with st.expander("Durum Güncelle", expanded=False, icon=":material/update:"):
            if capa_all:
                capa_map = {f"#{c['id']} - {c['title']}": c for c in capa_all}
                sel_capa = st.selectbox("CAPA Seç", options=list(capa_map.keys()))
                curr = capa_map[sel_capa]
                
                sc1, sc2 = st.columns(2)
                with sc1:
                    new_st = st.selectbox("Yeni Durum", ["Open", "In Progress", "Closed"], 
                                          index=["Open", "In Progress", "Closed"].index(curr["status"]))
                with sc2:
                    cl_date = st.date_input("Kapanma Tarihi", value=date.today()) if new_st == "Closed" else None
                
                if st.button("Güncelle", use_container_width=True):
                    update_capa_status(curr["id"], new_st, cl_date.strftime("%Y-%m-%d") if cl_date else None)
                    st.toast("Durum güncellendi!")
                    st.rerun()

    with ca2:
        with st.expander("Yeni CAPA Ekle", expanded=False, icon=":material/add_circle:"):
            with st.form("new_capa_form", clear_on_submit=True):
                nt = st.text_input("Başlık *")
                no = st.selectbox("Sorumlu", OWNERS)
                nc = st.selectbox("Kritiklik", ["Critical", "Major", "Minor"])
                nd = st.date_input("Vade", value=date.today())
                desc = st.text_area("Açıklama")
                
                if st.form_submit_button("Kaydet", use_container_width=True):
                    if nt:
                        insert_capa(date.today().strftime("%Y-%m-%d"), nt, desc, None, None, no, nd.strftime("%Y-%m-%d"), nc, "Open")
                        st.toast("Yeni CAPA oluşturuldu!")
                        st.rerun()
                    else:
                        st.error("Başlık zorunludur.")

    # ── Detail View ───────────────────────────────────────────────────────────
    if filtered:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            section_header("Seçili CAPA Detayı")
            detail_opts = {f"#{c['id']} - {c['title']}": c for c in filtered}
            choice = st.selectbox("Görüntülemek için seçin", options=list(detail_opts.keys()), label_visibility="collapsed")
            c = detail_opts[choice]
            
            svg_icon, bg, fg = STATUS_COLORS.get(c["status"], (CIRCLE_RED, "#fff", "#000"))
            
            st.markdown(f"""
            <div style="background: var(--secondary-background-color); border: 1px solid rgba(128,128,128,0.2); border-radius: 12px; padding: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        {get_svg(svg_icon, color=fg, size=24)}
                        <h3 style="margin: 0; color: var(--text-color);">{c['title']}</h3>
                    </div>
                    <span style="background: {bg}; color: {fg}; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 700;">
                        {c['status'].upper()}
                    </span>
                </div>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; font-size: 0.9rem;">
                    <div>
                        <div style="color: var(--text-color); opacity: 0.7; font-weight: 600; text-transform: uppercase; font-size: 0.7rem; margin-bottom: 4px;">Sorumlu</div>
                        <div style="color: var(--text-color);">{c['owner']}</div>
                    </div>
                    <div>
                        <div style="color: var(--text-color); opacity: 0.7; font-weight: 600; text-transform: uppercase; font-size: 0.7rem; margin-bottom: 4px;">Vade Tarihi</div>
                        <div style="color: {'#ef4444' if c['due_date'] < date.today().strftime('%Y-%m-%d') and c['status'] != 'Closed' else 'var(--text-color)'}; font-weight: 600;">
                            {c['due_date']} {f' (GECİKMİŞ)' if c['due_date'] < date.today().strftime('%Y-%m-%d') and c['status'] != 'Closed' else ''}
                        </div>
                    </div>
                    <div style="grid-column: span 2;">
                        <div style="color: var(--text-color); opacity: 0.7; font-weight: 600; text-transform: uppercase; font-size: 0.7rem; margin-bottom: 4px;">Açıklama</div>
                        <div style="color: var(--text-color); line-height: 1.5;">{c['description']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


show()
