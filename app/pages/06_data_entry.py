"""
QualityPulse — Page 6: Veri Girişi (Data Entry Hub)
Unified quality engineer workspace: defect log, measurement, CAPA, FMEA
All four entry types in one place with live feedback and smart defaults.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime, date, timedelta
import statistics

from db.database import (
    insert_defect, insert_measurement, insert_capa, insert_fmea,
    get_lines, get_measurement_points,
)
from components.styles import inject_css, page_header, section_header
from components.icons import get_svg, PENCIL, RULER, CALENDAR, FACTORY, BOX, MAP_PIN, USER, SEARCH, SHIELD, TREND_UP, REFRESH, SUN, MOON, CLOCK, WRENCH, CHECK, CIRCLE_GREEN, CIRCLE_YELLOW, CIRCLE_RED, ALERT
# ── Constants ─────────────────────────────────────────────────────────────────
DEFECT_TYPES = [
    "Boyutsal Sapma", "Yüzey Hatası", "Gözeneklilik",
    "Çekme Boşluğu", "Çapak",
]
MEASUREMENT_POINTS_DEFAULT = [
    ("Çap-A",      50.00, 50.10, 49.90),
    ("Çap-B",      25.00, 25.05, 24.95),
    ("Derinlik-C", 12.50, 12.60, 12.40),
    ("Kalınlık-D",  8.00,  8.08,  7.92),
    ("Uzunluk-E", 100.00,100.20, 99.80),
]
POINT_META = {r[0]: r for r in MEASUREMENT_POINTS_DEFAULT}
SHIFTS   = ["A", "B", "C"]
OWNERS   = ["Ahmet Yılmaz", "Fatma Demir", "Mehmet Kaya", "Ayşe Çelik", "Hasan Öztürk"]
PROCESS_STEPS = [
    "Eritme", "Döküm", "Kalıp Kapatma", "Basınç Uygulama",
    "Soğutma", "Kalıp Açma", "Parça Çıkarma", "Çapak Alma",
    "Yüzey İşleme", "Kalite Kontrol",
]

# ── Helpers ───────────────────────────────────────────────────────────────────
def _shift_now() -> str:
    """Auto-detect current shift from current hour."""
    h = datetime.now().hour
    if 6 <= h < 14:   return "A"
    elif 14 <= h < 22: return "B"
    else:              return "C"

def _rpn_badge(rpn: int) -> tuple[str, str, str]:
    if rpn > 200:   return "#fee2e2", "#991b1b", "🔴 YÜKSEK"
    elif rpn >= 100: return "#fef3c7", "#92400e", "🟡 ORTA"
    else:            return "#d1fae5", "#065f46", "🟢 DÜŞÜK"

def _status_card(bg: str, fg: str, label: str, value: str, sub: str = "") -> str:
    return f"""<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>*{{margin:0;padding:0;box-sizing:border-box;font-family:'Inter',sans-serif;}}body{{background:transparent;}}</style>
</head><body>
<div style="background:{bg};border-radius:12px;padding:14px 18px;height:100%;">
  <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;
              letter-spacing:0.07em;color:{fg}cc;margin-bottom:4px;">{label}</div>
  <div style="font-size:1.8rem;font-weight:800;color:{fg};line-height:1;">{value}</div>
  {"<div style='font-size:0.72rem;color:"+fg+"99;margin-top:4px;'>"+sub+"</div>" if sub else ""}
</div></body></html>"""

def _log_entry(session_key: str, msg: str):
    if session_key not in st.session_state:
        st.session_state[session_key] = []
    st.session_state[session_key].insert(0, {
        "time": datetime.now().strftime("%H:%M:%S"),
        "msg": msg,
    })
    st.session_state[session_key] = st.session_state[session_key][:8]

def _render_log(session_key: str):
    entries = st.session_state.get(session_key, [])
    if not entries:
        st.caption("Henüz kayıt yok.")
        return
    for e in entries:
        st.markdown(
            f'<div style="display:flex;gap:10px;align-items:baseline;padding:5px 0;'
            f'border-bottom:1px solid #f0f2f5;">'
            f'<span style="color:#6b7280;font-size:0.72rem;font-family:monospace;flex-shrink:0;">'
            f'{e["time"]}</span>'
            f'<span style="font-size:0.82rem;color:#1a1a2e;">{e["msg"]}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ── Main ──────────────────────────────────────────────────────────────────────
def show():
    inject_css()
    page_header(f"{get_svg(PENCIL, size=32)} Veri Girişi", "Kalite mühendisi veri giriş merkezi — hata, ölçüm, CAPA ve FMEA")

    # ── Shift Info Banner ─────────────────────────────────────────────────────
    cur_shift = _shift_now()
    shift_label = {"A": "A Vardiyası (06:00–14:00)",
                   "B": "B Vardiyası (14:00–22:00)",
                   "C": "C Vardiyası (22:00–06:00)"}[cur_shift]
    st.markdown(
        f'<div style="background:linear-gradient(135deg,#1a1a2e,#16213e);'
        f'color:#e0e0e0;padding:10px 20px;border-radius:10px;'
        f'display:flex;justify-content:space-between;align-items:center;'
        f'margin-bottom:1rem;font-size:0.88rem;font-weight:500;">'
        f'<span style="display:flex;align-items:center;gap:6px;">{get_svg(CLOCK, size=16)} {datetime.now().strftime("%d.%m.%Y  %H:%M")}</span>'
        f'<span style="color:#4f8ef7;font-weight:700;">{shift_label}</span>'
        f'<span style="color:#6b7280;">Aktif Vardiya Otomatik Seçildi</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "Hata Kaydı",
        "Ölçüm Girişi",
        "CAPA Oluştur",
        "FMEA Satırı",
    ])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — DEFECT ENTRY
    # ══════════════════════════════════════════════════════════════════════════
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        lines = get_lines() or ["Hat-1", "Hat-2"]

        left, right = st.columns([3, 2], gap="large")

        with left:
            section_header(f"{get_svg(PENCIL, size=24)} Hata Kaydı Formu")
            with st.form("defect_form", clear_on_submit=True):
                r1c1, r1c2, r1c3 = st.columns(3)
                with r1c1:
                    d_date = st.date_input("Tarih", value=date.today(), key="d_date")
                with r1c2:
                    d_shift = st.selectbox(
                        "Vardiya", SHIFTS,
                        index=SHIFTS.index(cur_shift), key="d_shift"
                    )
                with r1c3:
                    d_line = st.selectbox("Hat", lines, key="d_line")

                r2c1, r2c2 = st.columns(2)
                with r2c1:
                    d_type = st.selectbox("Hata Türü", DEFECT_TYPES, key="d_type")
                with r2c2:
                    d_qty = st.number_input(
                        "Hata Adedi", min_value=0, max_value=9999,
                        value=0, step=1, key="d_qty"
                    )

                d_total = st.number_input(
                    "Toplam Üretim (adet)", min_value=1, max_value=99999,
                    value=300, step=10, key="d_total"
                )
                d_notes = st.text_area("Not (isteğe bağlı)", height=72, key="d_notes")

                submitted = st.form_submit_button(
                    "Hata Kaydını Kaydet", use_container_width=True, icon=":material/save:"
                )

            if submitted:
                if d_qty > d_total:
                    st.error("⚠️ Hata adedi toplam üretimden büyük olamaz!")
                else:
                    insert_defect(
                        date=d_date.strftime("%Y-%m-%d"),
                        shift=d_shift,
                        defect_type=d_type,
                        quantity=int(d_qty),
                        total_produced=int(d_total),
                        line=d_line,
                        notes=d_notes.strip(),
                    )
                    rate = d_qty / d_total * 100
                    msg = f"{d_type} — {d_qty} adet / {d_total} üretim ({rate:.2f}%) | {d_line} {d_shift} Vardiyası"
                    _log_entry("defect_log", msg)
                    st.success(msg, icon=":material/check_circle:")

        with right:
            # Live rate preview
            section_header(f"{get_svg(TREND_UP, size=24)} Anlık Önizleme")
            prev_qty = st.session_state.get("d_qty", 0)
            prev_total = st.session_state.get("d_total", 300) or 300
            rate = prev_qty / prev_total * 100

            if rate == 0:
                bg, fg = "#d1fae5", "#065f46"
            elif rate < 3:
                bg, fg = "#fef3c7", "#92400e"
            else:
                bg, fg = "#fee2e2", "#991b1b"

            components.html(_status_card(bg, fg, "Anlık Hurda Oranı",
                                         f"{rate:.2f}%", f"{prev_qty} hata / {prev_total} üretim"), height=90)
            st.markdown("<br>", unsafe_allow_html=True)

            # Thresholds
            st.markdown("""
<div style="background:#f8fafc;border-radius:10px;padding:12px 16px;font-size:0.8rem;">
<b style="color:#1a1a2e;">Referans Limitler</b><br><br>
<div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #e8ecf0;">
  <span>🟢 Hedef</span><span style="font-weight:600;">≤ 2.0%</span>
</div>
<div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #e8ecf0;">
  <span>🟡 Uyarı</span><span style="font-weight:600;">2.0 – 3.5%</span>
</div>
<div style="display:flex;justify-content:space-between;padding:4px 0;">
  <span>🔴 Kritik</span><span style="font-weight:600;">&gt; 3.5%</span>
</div>
</div>
""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            section_header(f"{get_svg(SEARCH, size=24)} Son Kayıtlar")
            _render_log("defect_log")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — MEASUREMENT ENTRY
    # ══════════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        lines = get_lines() or ["Hat-1", "Hat-2"]
        existing_points = get_measurement_points() or [r[0] for r in MEASUREMENT_POINTS_DEFAULT]

        left, right = st.columns([3, 2], gap="large")

        with left:
            section_header(f"{get_svg(RULER, size=24)} Ölçüm Giriş Formu")
            with st.form("meas_form", clear_on_submit=True):
                mc1, mc2 = st.columns(2)
                with mc1:
                    m_line = st.selectbox("Hat", lines, key="m_line")
                with mc2:
                    m_point = st.selectbox("Ölçüm Noktası", existing_points, key="m_point")

                # Auto-fill nominal/USL/LSL from known points
                meta = POINT_META.get(m_point)
                nom_def  = meta[1] if meta else 0.0
                usl_def  = meta[2] if meta else 0.0
                lsl_def  = meta[3] if meta else 0.0

                m_value = st.number_input(
                    "Ölçüm Değeri (mm)", format="%.4f",
                    value=nom_def, key="m_value"
                )

                sc1, sc2, sc3 = st.columns(3)
                with sc1:
                    m_nom = st.number_input("Nominal (mm)", format="%.4f",
                                             value=nom_def, key="m_nom")
                with sc2:
                    m_usl = st.number_input("USL (mm)", format="%.4f",
                                             value=usl_def, key="m_usl")
                with sc3:
                    m_lsl = st.number_input("LSL (mm)", format="%.4f",
                                             value=lsl_def, key="m_lsl")

                m_submitted = st.form_submit_button(
                    "Ölçümü Kaydet", use_container_width=True, icon=":material/save:"
                )

            if m_submitted:
                if m_usl <= m_lsl:
                    st.error("USL, LSL'den büyük olmalıdır.")
                elif m_value > m_usl or m_value < m_lsl:
                    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    insert_measurement(ts, m_line, m_point,
                                       m_value, m_nom, m_usl, m_lsl)
                    msg = f"TOLERANS DIŞI — {m_point} = {m_value:.4f} ({m_line})"
                    _log_entry("meas_log", msg)
                    st.error(msg, icon=":material/cancel:")
                else:
                    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    insert_measurement(ts, m_line, m_point,
                                       m_value, m_nom, m_usl, m_lsl)
                    dev = m_value - m_nom
                    msg = f"{m_point} = {m_value:.4f} mm (sapma {dev:+.4f}) | {m_line}"
                    _log_entry("meas_log", msg)
                    st.success(msg, icon=":material/check_circle:")

        with right:
            section_header(f"{get_svg(SEARCH, size=24)} Tolerans Analizi")
            try:
                mval   = st.session_state.get("m_value", nom_def)
                musl   = st.session_state.get("m_usl",   usl_def)
                mlsl   = st.session_state.get("m_lsl",   lsl_def)
                mnom   = st.session_state.get("m_nom",   nom_def)
                tol_range = musl - mlsl
                dev = mval - mnom
                pct = (mval - mlsl) / tol_range * 100 if tol_range > 0 else 50

                if mval > musl or mval < mlsl:
                    bg, fg, status = "#fee2e2", "#991b1b", "TOLERANS DIŞI ❌"
                elif abs(dev) > (tol_range * 0.35):
                    bg, fg, status = "#fef3c7", "#92400e", "DİKKAT ⚠️"
                else:
                    bg, fg, status = "#d1fae5", "#065f46", "TOLERANS İÇİ ✅"

                components.html(_status_card(bg, fg, "Durum", status,
                                              f"Sapma: {dev:+.4f} mm"), height=90)
                st.markdown("<br>", unsafe_allow_html=True)

                # Visual bar
                bar_pct = max(0, min(100, pct))
                bar_col = "#2ecc71" if bg == "#d1fae5" else \
                          "#f39c12" if bg == "#fef3c7" else "#e74c3c"
                st.markdown(
                    f'<div style="background:#f0f2f5;border-radius:8px;height:12px;overflow:hidden;margin-bottom:6px;">'
                    f'<div style="width:{bar_pct:.1f}%;background:{bar_col};height:100%;border-radius:8px;'
                    f'transition:width 0.4s ease;"></div></div>'
                    f'<div style="display:flex;justify-content:space-between;font-size:0.7rem;color:#6b7280;">'
                    f'<span>LSL {mlsl:.4f}</span><span>NOM {mnom:.4f}</span><span>USL {musl:.4f}</span></div>',
                    unsafe_allow_html=True,
                )
            except Exception:
                st.info("Form değerleri girildiğinde önizleme görünür.")

            st.markdown("<br>", unsafe_allow_html=True)
            section_header(f"{get_svg(SEARCH, size=24)} Son Kayıtlar")
            _render_log("meas_log")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3 — CAPA
    # ══════════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown("<br>", unsafe_allow_html=True)
        left, right = st.columns([3, 2], gap="large")

        with left:
            section_header(f"{get_svg(WRENCH, size=24)} CAPA Oluşturma Formu")
            with st.form("capa_entry_form", clear_on_submit=True):
                c_title = st.text_input("Başlık *", placeholder="CAPA konusunu kısaca tanımlayın", key="ce_title")

                cc1, cc2, cc3 = st.columns(3)
                with cc1:
                    c_crit = st.selectbox("Kritiklik *", ["Critical", "Major", "Minor"], key="ce_crit")
                with cc2:
                    c_owner = st.selectbox("Sorumlu *", OWNERS, key="ce_owner")
                with cc3:
                    c_due = st.date_input("Vade *", value=date.today() + timedelta(days=14), key="ce_due")

                c_desc = st.text_area("Sorun Tanımı *", height=90,
                                       placeholder="Tespit edilen sorunu detaylı açıklayın…", key="ce_desc")

                rc1, rc2 = st.columns(2)
                with rc1:
                    c_root = st.text_area("Kök Neden", height=72,
                                           placeholder="5 Why, Balık kılçığı…", key="ce_root")
                with rc2:
                    c_action = st.text_area("Düzeltici Faaliyet", height=72,
                                             placeholder="Alınacak aksiyonlar…", key="ce_act")

                c_status = st.selectbox("Durum", ["Open", "In Progress", "Closed"], key="ce_status")

                c_sub = st.form_submit_button("CAPA Kaydet", use_container_width=True, icon=":material/save:")

            if c_sub:
                if not (c_title and c_desc):
                    st.error("Başlık ve Açıklama zorunludur.")
                else:
                    insert_capa(
                        created_date=date.today().strftime("%Y-%m-%d"),
                        title=c_title, description=c_desc,
                        root_cause=c_root or None,
                        corrective_action=c_action or None,
                        owner=c_owner,
                        due_date=c_due.strftime("%Y-%m-%d"),
                        criticality=c_crit,
                        status=c_status,
                    )
                    days_left = (c_due - date.today()).days
                    due_str = f"{days_left} gün kaldı" if days_left > 0 else "Bugün son gün!"
                    msg = f"{c_title} [{c_crit}] | {c_owner} | {due_str}"
                    _log_entry("capa_log", msg)
                    st.success(msg, icon=":material/check_circle:")

        with right:
            section_header("Kritiklik Rehberi")
            st.markdown("""
<div style="font-size:0.8rem;line-height:1.8;">
<div style="background:#fee2e2;border-left:4px solid #991b1b;border-radius:0 8px 8px 0;
            padding:10px 14px;margin-bottom:8px;">
  <b style="color:#991b1b;">🔴 Critical</b><br>
  <span style="color:#7f1d1d;">Müşteri etkisi, güvenlik riski, üretim durması.
  24 saat içinde aksiyon başlatılmalı.</span>
</div>
<div style="background:#fef3c7;border-left:4px solid #92400e;border-radius:0 8px 8px 0;
            padding:10px 14px;margin-bottom:8px;">
  <b style="color:#92400e;">🟡 Major</b><br>
  <span style="color:#78350f;">Kalite hedefini etkiler, müşteri şikayeti riski.
  1 hafta içinde aksiyon.</span>
</div>
<div style="background:#d1fae5;border-left:4px solid #065f46;border-radius:0 8px 8px 0;
            padding:10px 14px;">
  <b style="color:#065f46;">🟢 Minor</b><br>
  <span style="color:#064e3b;">Süreç iyileştirme fırsatı, müşteri etkisi yok.
  1 ay içinde aksiyon.</span>
</div>
</div>
""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            section_header("Son Kayıtlar")
            _render_log("capa_log")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 4 — FMEA
    # ══════════════════════════════════════════════════════════════════════════
    with tab4:
        st.markdown("<br>", unsafe_allow_html=True)
        left, right = st.columns([3, 2], gap="large")

        with left:
            section_header(f"{get_svg(SHIELD, size=24)} FMEA Satırı Formu")
            with st.form("fmea_entry_form", clear_on_submit=True):
                fc1, fc2 = st.columns(2)
                with fc1:
                    f_step = st.selectbox("Proses Adımı *", PROCESS_STEPS, key="fe_step")
                    f_mode = st.text_input("Hata Modu *",
                                            placeholder="Ne yanlış gidebilir?", key="fe_mode")
                    f_effect = st.text_input("Hata Etkisi *",
                                              placeholder="Müşteri ne görür?", key="fe_effect")
                    f_owner = st.selectbox("Sorumlu", OWNERS, key="fe_owner")
                    f_status = st.selectbox("Durum", ["Open", "In Progress", "Closed"], key="fe_status")

                with fc2:
                    f_sev = st.slider("Şiddet (S)", 1, 10, 5, key="fe_s",
                                       help="1=önemsiz → 10=güvenlik/uyumluluk")
                    f_occ = st.slider("Oluşma (O)",  1, 10, 5, key="fe_o",
                                       help="1=nadiren → 10=kaçınılmaz")
                    f_det = st.slider("Tespit (T)",  1, 10, 5, key="fe_d",
                                       help="1=kesin tespite → 10=tespiti imkansız")

                    live_rpn = f_sev * f_occ * f_det
                    rpn_bg, rpn_fg, rpn_label = _rpn_badge(live_rpn)
                    st.markdown(
                        f'<div style="background:{rpn_bg};border:2px solid {rpn_fg}33;'
                        f'border-radius:10px;padding:14px;text-align:center;margin-top:8px;">'
                        f'<div style="font-size:0.7rem;font-weight:700;color:{rpn_fg};'
                        f'text-transform:uppercase;letter-spacing:0.06em;">Risk Öncelik Sayısı</div>'
                        f'<div style="font-size:2.4rem;font-weight:900;color:{rpn_fg};line-height:1;">'
                        f'{live_rpn}</div>'
                        f'<div style="font-size:0.78rem;font-weight:700;color:{rpn_fg};'
                        f'margin-top:4px;">{rpn_label}</div>'
                        f'<div style="font-size:0.7rem;color:{rpn_fg}99;margin-top:2px;">'
                        f'S={f_sev} × O={f_occ} × T={f_det}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                f_ctrl   = st.text_area("Mevcut Kontroller", height=60, key="fe_ctrl")
                f_action = st.text_area("Önerilen Aksiyon",   height=60, key="fe_act")

                f_sub = st.form_submit_button("FMEA Satırını Kaydet", use_container_width=True, icon=":material/save:")

            if f_sub:
                if not (f_mode and f_effect):
                    st.error("Hata Modu ve Hata Etkisi zorunludur.")
                else:
                    insert_fmea(
                        process_step=f_step, failure_mode=f_mode,
                        failure_effect=f_effect, severity=f_sev,
                        occurrence=f_occ, detection=f_det,
                        current_controls=f_ctrl or None,
                        recommended_action=f_action or None,
                        responsible=f_owner, status=f_status,
                    )
                    rpn = f_sev * f_occ * f_det
                    _, _, rl = _rpn_badge(rpn)
                    msg = f"{f_step} / {f_mode} — RPN={rpn} {rl} | {f_owner}"
                    _log_entry("fmea_log", msg)
                    st.success(msg, icon=":material/check_circle:")

        with right:
            section_header("RPN Rehberi")
            st.markdown("""
<div style="font-size:0.8rem;line-height:1.7;">
<div style="background:#fee2e2;border-left:4px solid #991b1b;border-radius:0 8px 8px 0;
            padding:10px 14px;margin-bottom:8px;">
  <b style="color:#991b1b;">🔴 RPN &gt; 200 — Yüksek Risk</b><br>
  <span style="color:#7f1d1d;">Acil aksiyon gerekli. Üretimi etkiler.
  Bir hafta içinde kontrol altına alın.</span>
</div>
<div style="background:#fef3c7;border-left:4px solid #92400e;border-radius:0 8px 8px 0;
            padding:10px 14px;margin-bottom:8px;">
  <b style="color:#92400e;">🟡 RPN 100–200 — Orta Risk</b><br>
  <span style="color:#78350f;">Planlı iyileştirme gerekli.
  Kontroller güçlendirilmeli.</span>
</div>
<div style="background:#d1fae5;border-left:4px solid #065f46;border-radius:0 8px 8px 0;
            padding:10px 14px;margin-bottom:16px;">
  <b style="color:#065f46;">🟢 RPN &lt; 100 — Düşük Risk</b><br>
  <span style="color:#064e3b;">Mevcut kontroller yeterli.
  Periyodik gözlem yeterli.</span>
</div>

<div style="background:#f0f2f5;border-radius:8px;padding:10px 14px;">
<b style="color:#1a1a2e;font-size:0.78rem;">Puanlama Rehberi</b>
<table style="width:100%;margin-top:8px;border-collapse:collapse;font-size:0.75rem;color:#374151;">
<tr><td style="padding:2px 6px;color:#6b7280;"><b>S</b></td><td>Şiddet: Etkinin ciddiyeti</td></tr>
<tr><td style="padding:2px 6px;color:#6b7280;"><b>O</b></td><td>Oluşma: Hata sıklığı</td></tr>
<tr><td style="padding:2px 6px;color:#6b7280;"><b>T</b></td><td>Tespit: Kaçma olasılığı</td></tr>
</table>
</div>
</div>
""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            section_header(f"{get_svg(SEARCH, size=24)} Son Kayıtlar")
            _render_log("fmea_log")


show()
