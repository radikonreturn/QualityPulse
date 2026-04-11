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
    "Open":        (CIRCLE_RED, "#fee2e2", "#991b1b"),
    "In Progress": (CIRCLE_YELLOW, "#fef3c7", "#92400e"),
    "Closed":      (CIRCLE_GREEN, "#d1fae5", "#065f46"),
}

CRITICALITY_COLORS = {
    "Critical": ("#fee2e2", "#991b1b"),
    "Major":    ("#fef3c7", "#92400e"),
    "Minor":    ("#f0fdf4", "#166534"),
}

OWNERS = ["Ahmet Yılmaz", "Fatma Demir", "Mehmet Kaya", "Ayşe Çelik", "Hasan Öztürk"]


def show():
    inject_css()
    page_header(f"{get_svg(CAPA, size=32)} CAPA Takibi", "Düzeltici ve Önleyici Faaliyet yönetimi — izleme, güncelleme ve planlama")

    capa_all = get_all_capa()

    # ── Summary Cards ─────────────────────────────────────────────────────────
    section_header("Durum Özeti")
    open_cnt = sum(1 for c in capa_all if c["status"] == "Open")
    prog_cnt = sum(1 for c in capa_all if c["status"] == "In Progress")
    closed_cnt = sum(1 for c in capa_all if c["status"] == "Closed")
    overdue_cnt = count_overdue_capa(capa_all)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Açık", open_cnt)
    col2.metric("Devam Eden", prog_cnt)
    col3.metric("Kapalı", closed_cnt)
    col4.metric("Gecikmiş", overdue_cnt, delta=f"-{overdue_cnt}" if overdue_cnt else "0",
                delta_color="inverse")

    # ── Filter Bar ────────────────────────────────────────────────────────────
    section_header("Filtreler")
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        status_filter = st.multiselect(
            "Durum", options=["Open", "In Progress", "Closed"],
            default=["Open", "In Progress"], key="capa_status_filter",
        )
    with fc2:
        criticality_filter = st.multiselect(
            "Kritiklik", options=["Critical", "Major", "Minor"],
            default=["Critical", "Major", "Minor"], key="capa_crit_filter",
        )
    with fc3:
        owner_search = st.text_input("Sahip Ara", placeholder="İsim...", key="capa_owner_search")

    filtered = get_all_capa(
        status_filter=status_filter if status_filter else None,
        criticality_filter=criticality_filter if criticality_filter else None,
        owner_search=owner_search,
    )

    # ── Color-coded Table ──────────────────────────────────────────────────────
    section_header(f"CAPA Listesi ({len(filtered)} kayıt)")

    if not filtered:
        st.info("Seçilen filtreler için kayıt bulunamadı.")
    else:
        today_str = date.today().strftime("%Y-%m-%d")
        df = pd.DataFrame(filtered)

        # Flag overdue
        df["overdue"] = (df["due_date"] < today_str) & (df["status"] != "Closed")

        # Build display df
        df_disp = df[["id", "title", "owner", "criticality", "status",
                        "created_date", "due_date", "closed_date", "overdue"]].copy()
        df_disp.columns = ["ID", "Başlık", "Sahip", "Kritiklik", "Durum",
                            "Oluşturma", "Vade", "Kapanma", "Gecikmiş"]

        # Apply row coloring via Pandas Styler
        def row_style(row):
            if row["Gecikmiş"]:
                return ["background-color: #fff3cd"] * len(row)
            status = row["Durum"]
            bg = STATUS_COLORS.get(status, ("", "", ""))[1]
            return [f"background-color: {bg}22"] * len(row)

        styled = df_disp.style.apply(row_style, axis=1)
        st.dataframe(styled, hide_index=True, width='stretch', height=320)

    # ── Update Status ─────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Durum Güncelle")
    with st.expander("Durum Güncelleme", expanded=False):
        st.markdown(f"### {get_svg(SAVE)} Durum Değiştir", unsafe_allow_html=True)
        if capa_all:
            capa_ids = {f"#{c['id']} — {c['title']}": c["id"] for c in capa_all}
            selected_label = st.selectbox("CAPA Seç", options=list(capa_ids.keys()), key="update_capa_sel")
            selected_id = capa_ids[selected_label]
            current = next(c for c in capa_all if c["id"] == selected_id)

            col_s, col_d = st.columns(2)
            with col_s:
                new_status = st.selectbox(
                    "Yeni Durum", options=["Open", "In Progress", "Closed"],
                    index=["Open", "In Progress", "Closed"].index(current["status"]),
                    key="update_status",
                )
            with col_d:
                closed_date_input = None
                if new_status == "Closed":
                    closed_date_input = st.date_input("Kapanma Tarihi", value=date.today(), key="update_closed")

            if st.button("Güncelle", key="update_capa_btn"):
                closed_str = closed_date_input.strftime("%Y-%m-%d") if closed_date_input else None
                update_capa_status(selected_id, new_status, closed_str)
                st.success(f"CAPA #{selected_id} durumu '{new_status}' olarak güncellendi.")
                st.rerun()

    # ── Add New CAPA ───────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Yeni CAPA Ekle")
    with st.expander("Yeni CAPA Oluştur", expanded=False):
        st.markdown(f"### {get_svg(PLUS)} Yeni Kayıt", unsafe_allow_html=True)
        with st.form("add_capa_form"):
            fc1, fc2 = st.columns(2)
            with fc1:
                capa_title = st.text_input("Başlık *", key="capa_title")
                capa_owner = st.selectbox("Sahip *", options=OWNERS, key="capa_owner")
                capa_crit = st.selectbox("Kritiklik *", options=["Critical", "Major", "Minor"], key="capa_crit")
                capa_status = st.selectbox("Durum", options=["Open", "In Progress", "Closed"], key="capa_status")
            with fc2:
                capa_due = st.date_input("Vade Tarihi *", value=date.today(), key="capa_due")
                capa_desc = st.text_area("Açıklama *", height=80, key="capa_desc")
                capa_root = st.text_area("Kök Neden", height=60, key="capa_root")
                capa_action = st.text_area("Düzeltici Faaliyet", height=60, key="capa_action")

            submitted = st.form_submit_button("CAPA Kaydet", use_container_width=True)
            if submitted:
                if not (capa_title and capa_desc):
                    st.error("Başlık ve Açıklama zorunludur.")
                else:
                    insert_capa(
                        created_date=date.today().strftime("%Y-%m-%d"),
                        title=capa_title,
                        description=capa_desc,
                        root_cause=capa_root or None,
                        corrective_action=capa_action or None,
                        owner=capa_owner,
                        due_date=capa_due.strftime("%Y-%m-%d"),
                        criticality=capa_crit,
                        status=capa_status,
                    )
                    st.success(f"CAPA '{capa_title}' başarıyla oluşturuldu.")
                    st.rerun()

    # ── CAPA Detail View ───────────────────────────────────────────────────────
    if filtered:
        st.markdown("<br>", unsafe_allow_html=True)
        section_header("CAPA Detayı")
        detail_options = {f"#{c['id']} — {c['title']}": c for c in filtered}
        detail_choice = st.selectbox("CAPA Seç", options=list(detail_options.keys()), key="capa_detail")
        capa = detail_options[detail_choice]

        svg_icon, ss, _ = STATUS_COLORS.get(capa["status"], ("", "#fff", "#000"))
        st.markdown(f"""
        <div style="background:#ffffff;border:1px solid #e8ecf0;border-radius:12px;padding:1.4rem;box-shadow:0 2px 8px rgba(0,0,0,0.06);">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1rem;">
                <div>
                    <h4 style="margin:0;color:#1a1a2e;display:flex;align-items:center;gap:8px;">
                        {svg_icon} {capa['title']}
                    </h4>
                    <p style="color:#6b7280;font-size:0.82rem;margin:4px 0 0;">
                        #{capa['id']} | Sahip: {capa['owner']} | Oluşturulma: {capa['created_date']}
                    </p>
                </div>
                <div style="background:{ss};color:{STATUS_COLORS.get(capa['status'],('','','#000'))[2]};
                            padding:4px 14px;border-radius:20px;font-size:0.8rem;font-weight:600;">
                    {capa['status']}
                </div>
            </div>
            <hr style="border:none;border-top:1px solid #f0f2f5;margin:0.8rem 0;">
            <table style="width:100%;font-size:0.85rem;border-collapse:collapse;">
                <tr><td style="color:#6b7280;padding:4px 0;width:160px;">Açıklama</td>
                    <td style="color:#1a1a2e;">{capa['description']}</td></tr>
                <tr><td style="color:#6b7280;padding:4px 0;">Kök Neden</td>
                    <td style="color:#1a1a2e;">{capa.get('root_cause') or '—'}</td></tr>
                <tr><td style="color:#6b7280;padding:4px 0;">Düzeltici Faaliyet</td>
                    <td style="color:#1a1a2e;">{capa.get('corrective_action') or '—'}</td></tr>
                <tr><td style="color:#6b7280;padding:4px 0;">Kritiklik</td>
                    <td style="color:#1a1a2e;font-weight:600;">{capa['criticality']}</td></tr>
                <tr><td style="color:#6b7280;padding:4px 0;">Vade Tarihi</td>
                    <td style="color:{'#991b1b' if capa['due_date'] < date.today().strftime('%Y-%m-%d') and capa['status'] != 'Closed' else '#1a1a2e'};font-weight:500;">
                        <div style="display:flex;align-items:center;gap:4px;">
                            {capa['due_date']} 
                            {('<span style="color:#991b1b;display:flex;align-items:center;gap:4px;margin-left:8px;">' + get_svg(ALERT, color="#991b1b", size=14) + ' GECİKMİŞ</span>') if capa['due_date'] < date.today().strftime('%Y-%m-%d') and capa['status'] != 'Closed' else ''}
                        </div>
                    </td></tr>
                <tr><td style="color:#6b7280;padding:4px 0;">Kapanma Tarihi</td>
                    <td style="color:#1a1a2e;">{capa.get('closed_date') or '—'}</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)


show()
