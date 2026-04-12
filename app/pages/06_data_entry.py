"""
QualityPulse — Page 6: Veri Girişi (Data Entry Hub)
Unified quality engineer workspace: defect log, measurement, CAPA, FMEA
All four entry types in one place with live feedback and smart defaults.
"""

import sys
import os
import json
import base64
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, date, timedelta

from db.database import (
    insert_defect, insert_measurement, insert_capa, insert_fmea,
    get_lines, get_measurement_points,
)
from components.styles import inject_css, page_header, section_header
from components.icons import get_svg, PENCIL, RULER, SEARCH, SHIELD, TREND_UP, CLOCK, WRENCH
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
DEFAULT_SHIFTS = [
    {"name": "A", "label": "A Vardiyası", "start": 6,  "end": 14, "active": True},
    {"name": "B", "label": "B Vardiyası", "start": 14, "end": 22, "active": True},
    {"name": "C", "label": "C Vardiyası", "start": 22, "end": 6,  "active": True},
]

def _shift_now(shift_cfg: list | None = None) -> str:
    """Auto-detect current shift from current hour using configured schedule."""
    h = datetime.now().hour
    schedules = shift_cfg if shift_cfg else DEFAULT_SHIFTS
    active = [s for s in schedules if s.get("active", True)]
    for s in active:
        start, end = s["start"], s["end"]
        if start < end:  # Normal span e.g. 06–14
            if start <= h < end:
                return s["name"]
        else:  # Overnight span e.g. 22–06
            if h >= start or h < end:
                return s["name"]
    # Fallback: return first active shift
    return active[0]["name"] if active else "A"

def _rpn_badge(rpn: int) -> tuple[str, str, str]:
    if rpn > 200:
        return "#fee2e2", "#991b1b", "🔴 YÜKSEK"
    elif rpn >= 100:
        return "#fef3c7", "#92400e", "🟡 ORTA"
    else:
        return "#d1fae5", "#065f46", "🟢 DÜŞÜK"

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

    if "qp_config" not in st.session_state:
        st.session_state.qp_config = {
            "company": {"name": "", "sector": "Otomotiv", "facility": "", "city": "", "employees": 0, "qe": ""},
            "lines": [{"name": "Hat-1", "shifts": 3, "target": 100}, {"name": "Hat-2", "shifts": 3, "target": 100}],
            "quality": {
                "defects": DEFECT_TYPES.copy(),
                "scrap_target": 2.0,
                "oee_target": 85.0,
                "complaint_target": 0
            },
            "spc_points": [{"point": r[0], "nom": r[1], "usl": r[2], "lsl": r[3]} for r in MEASUREMENT_POINTS_DEFAULT],
            "shifts": [s.copy() for s in DEFAULT_SHIFTS],
        }
    cfg = st.session_state.qp_config
    # Ensure shift config key exists for older session states
    if "shifts" not in cfg:
        cfg["shifts"] = [s.copy() for s in DEFAULT_SHIFTS]

    # ── Shift Info Banner ─────────────────────────────────────────────────────
    shift_schedules = cfg.get("shifts", DEFAULT_SHIFTS)
    cur_shift = _shift_now(shift_schedules)
    active_shift_cfg = next((s for s in shift_schedules if s["name"] == cur_shift), DEFAULT_SHIFTS[0])
    shift_label = f"{active_shift_cfg['label']} ({active_shift_cfg['start']:02d}:00–{active_shift_cfg['end']:02d}:00)"
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
    tab_settings, tab1, tab2, tab3, tab4 = st.tabs([
        "Şirket Bilgisi",
        "Hata Kaydı",
        "Ölçüm Girişi",
        "CAPA Oluştur",
        "FMEA Satırı",
    ])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB SETTINGS — COMPANY CONFIG
    # ══════════════════════════════════════════════════════════════════════════
    with tab_settings:
        st.markdown("<br>", unsafe_allow_html=True)
        left_s, right_s = st.columns([1, 1], gap="large")
        
        with left_s:
            section_header("Section 1 — Company Info")
            c_name = st.text_input("Firma Adı / Company Name *", value=cfg["company"]["name"])
            sectors = ["Otomotiv", "Havacılık", "Elektronik", "Gıda", "Metal Döküm", "Tekstil", "Plastik", "Kimya", "Diğer"]
            c_sect = st.selectbox("Sektör / Sector", sectors, index=sectors.index(cfg["company"]["sector"]) if cfg["company"]["sector"] in sectors else 0)
            c_fac = st.text_input("Tesis Adı / Facility Name", value=cfg["company"]["facility"])
            c_city = st.text_input("Şehir / City", value=cfg["company"]["city"])
            c_emp = st.number_input("Çalışan Sayısı / Employee Count", min_value=0, value=cfg["company"]["employees"], step=10)
            c_qe = st.text_input("Kalite Mühendisi / Quality Engineer", value=cfg["company"]["qe"])
            
            uploaded_logo = st.file_uploader("Firma Logosu / Logo", type=["png", "jpg", "jpeg", "svg"])
            if uploaded_logo:
                b64 = base64.b64encode(uploaded_logo.read()).decode()
                ext = uploaded_logo.name.split('.')[-1].lower()
                mime = f"image/{ext}" if ext != 'svg' else "image/svg+xml"
                st.markdown(f'<img src="data:{mime};base64,{b64}" width="150" style="border-radius:10px;">', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            section_header("Section 2 — Production Lines")
            if "temp_lines" not in st.session_state:
                st.session_state.temp_lines = cfg["lines"].copy()
            
            for i, line in enumerate(st.session_state.temp_lines):
                lc1, lc2, lc3, lc4 = left_s.columns([3, 2, 2, 1])
                line["name"] = lc1.text_input("Hat Adı", value=line.get("name",""), key=f"tl_name_{i}", label_visibility="collapsed")
                line["shifts"] = lc2.selectbox("Vardiya", [1, 2, 3], index=[1,2,3].index(line.get("shifts", 3)), key=f"tl_sh_{i}", label_visibility="collapsed")
                line["target"] = lc3.number_input("Hedef", min_value=1, value=line.get("target",100), step=10, key=f"tl_tgt_{i}", label_visibility="collapsed")
                if lc4.button("Sil", key=f"tl_del_{i}"):
                    st.session_state.temp_lines.pop(i)
                    st.rerun()
            
            if len(st.session_state.temp_lines) < 10:
                if left_s.button("Hat Ekle / Add Line"):
                    st.session_state.temp_lines.append({"name": f"Yeni Hat", "shifts": 3, "target": 100})
                    st.rerun()

        with right_s:
            section_header("Section 3 — Quality Parameters")
            if "temp_defects" not in st.session_state:
                st.session_state.temp_defects = cfg["quality"]["defects"].copy()
            
            def add_temp_defect():
                val = st.session_state.fe_new_dfct.strip()
                if val and val not in st.session_state.temp_defects:
                    st.session_state.temp_defects.append(val)
                st.session_state.fe_new_dfct = ""

            st.text_input("Yeni Hata Türü Ekle (Type & Enter)", key="fe_new_dfct", on_change=add_temp_defect)
            sel_defects = st.multiselect("Hata Türleri / Defect Types", st.session_state.temp_defects, default=st.session_state.temp_defects, key="ms_defects")
            st.session_state.temp_defects = sel_defects
            
            q_scrap = st.slider("Hedef Fire Oranı / Scrap Rate Target (%)", min_value=0.5, max_value=10.0, value=float(cfg["quality"]["scrap_target"]), step=0.1)
            q_oee = st.slider("Hedef OEE / OEE Target (%)", min_value=60.0, max_value=99.0, value=float(cfg["quality"]["oee_target"]), step=0.5)
            q_comp = st.number_input("Aylık Şikayet Hedefi / Monthly Complaint Target", min_value=0, value=cfg["quality"]["complaint_target"])

            st.markdown("<br>", unsafe_allow_html=True)
            section_header("Section 4 — SPC Measurement Points")
            if "temp_spc" not in st.session_state:
                st.session_state.temp_spc = pd.DataFrame(cfg["spc_points"])
                if not st.session_state.temp_spc.empty:
                    st.session_state.temp_spc = st.session_state.temp_spc.rename(columns={"point": "Nokta Adı", "nom": "Nominal", "usl": "USL", "lsl": "LSL"})
                else:
                    st.session_state.temp_spc = pd.DataFrame(columns=["Nokta Adı", "Nominal", "USL", "LSL"])

            spc_df = st.data_editor(
                st.session_state.temp_spc,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "Nokta Adı": st.column_config.TextColumn("Nokta Adı", required=True),
                    "Nominal": st.column_config.NumberColumn("Nominal", format="%.3f"),
                    "USL": st.column_config.NumberColumn("USL", format="%.3f"),
                    "LSL": st.column_config.NumberColumn("LSL", format="%.3f"),
                },
                key="editor_spc"
            )

            st.markdown("<br>", unsafe_allow_html=True)
            section_header("Section 5 — Vardiya Yönetimi / Shift Management")

            if "temp_shifts" not in st.session_state:
                st.session_state.temp_shifts = cfg["shifts"].copy()

            # Column headers
            sh0, sh1, sh2, sh3, sh4, sh5 = right_s.columns([1.5, 2.5, 1.5, 1.5, 1.5, 1.5])
            sh0.markdown("**Aktif**", unsafe_allow_html=True)
            sh1.markdown("**Vardiya Adı**", unsafe_allow_html=True)
            sh2.markdown("**Kısa Ad**", unsafe_allow_html=True)
            sh3.markdown("**Başlangıç**", unsafe_allow_html=True)
            sh4.markdown("**Bitiş**", unsafe_allow_html=True)
            sh5.markdown("**Renk**", unsafe_allow_html=True)

            SHIFT_COLORS = ["#4f8ef7", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"]
            for i, shift in enumerate(st.session_state.temp_shifts):
                sc0, sc1, sc2, sc3, sc4, sc5 = right_s.columns([1.5, 2.5, 1.5, 1.5, 1.5, 1.5])
                shift["active"] = sc0.checkbox("", value=shift.get("active", True), key=f"ts_act_{i}", label_visibility="collapsed")
                shift["label"] = sc1.text_input("Adı", value=shift.get("label", f"Vardiya {i+1}"), key=f"ts_lbl_{i}", label_visibility="collapsed")
                shift["name"]  = sc2.text_input("Kısa", value=shift.get("name", str(i+1)), key=f"ts_nm_{i}", label_visibility="collapsed", max_chars=3)
                shift["start"] = sc3.number_input("Baş", min_value=0, max_value=23, value=int(shift.get("start", 0)), key=f"ts_st_{i}", label_visibility="collapsed")
                shift["end"]   = sc4.number_input("Bit", min_value=0, max_value=23, value=int(shift.get("end", 8)),  key=f"ts_en_{i}", label_visibility="collapsed")
                current_color = shift.get("color", SHIFT_COLORS[i % len(SHIFT_COLORS)])
                shift["color"] = sc5.color_picker("Renk", value=current_color, key=f"ts_col_{i}", label_visibility="collapsed")

            col_add, col_del = right_s.columns(2)
            if col_add.button("➕ Vardiya Ekle", key="shift_add", use_container_width=True):
                next_n = len(st.session_state.temp_shifts) + 1
                st.session_state.temp_shifts.append({
                    "name": str(next_n), "label": f"Vardiya {next_n}",
                    "start": 0, "end": 8, "active": True,
                    "color": SHIFT_COLORS[next_n % len(SHIFT_COLORS)]
                })
                st.rerun()
            if col_del.button("➖ Son Vardiyayı Sil", key="shift_del", disabled=len(st.session_state.temp_shifts) <= 1, use_container_width=True):
                st.session_state.temp_shifts.pop()
                st.rerun()

            # Live preview of configured shift schedule
            if st.session_state.temp_shifts:
                st.markdown("**Vardiya Saatleri Önizleme:**")
                timeline_html = '<div style="display:flex;gap:2px;border-radius:8px;overflow:hidden;height:28px;margin-top:4px;">'
                for s in st.session_state.temp_shifts:
                    if not s.get("active", True):
                        continue
                    start, end = int(s["start"]), int(s["end"])
                    duration = (end - start) % 24 or 24
                    pct = duration / 24 * 100
                    color = s.get("color", "#4f8ef7")
                    timeline_html += (
                        f'<div style="flex:{pct:.1f};background:{color};display:flex;'
                        f'align-items:center;justify-content:center;color:white;'
                        f'font-size:0.72rem;font-weight:700;white-space:nowrap;padding:0 4px;" '
                        f'title="{s["label"]}: {start:02d}:00–{end:02d}:00">'
                        f'{s["name"]} {start:02d}–{end:02d}\'</div>'
                    )
                timeline_html += '</div>'
                st.markdown(timeline_html, unsafe_allow_html=True)

        st.markdown("<br><hr>", unsafe_allow_html=True)
        if st.button("Ayarları Kaydet / Save Settings", type="primary", use_container_width=True, icon=":material/save:"):
            if not c_name.strip():
                st.error("Firma Adı zorunludur! / Company Name is required!")
            else:
                cfg["company"] = {
                    "name": c_name.strip(), "sector": c_sect, "facility": c_fac.strip(),
                    "city": c_city.strip(), "employees": c_emp, "qe": c_qe.strip()
                }
                cfg["lines"] = st.session_state.temp_lines
                cfg["quality"] = {
                    "defects": sel_defects, "scrap_target": q_scrap, "oee_target": q_oee, "complaint_target": q_comp
                }
                spc_points = []
                for _, r in spc_df.iterrows():
                    if r.get("Nokta Adı"):
                        spc_points.append({
                            "point": str(r["Nokta Adı"]),
                            "nom": float(r["Nominal"]) if pd.notnull(r["Nominal"]) else 0.0,
                            "usl": float(r["USL"]) if pd.notnull(r["USL"]) else 0.0,
                            "lsl": float(r["LSL"]) if pd.notnull(r["LSL"]) else 0.0
                        })
                cfg["spc_points"] = spc_points
                cfg["shifts"] = st.session_state.temp_shifts
                st.session_state.qp_config = cfg
                
                json_cfg = json.dumps(cfg)
                js = f"<script>localStorage.setItem('qualitypulse_config', '{json_cfg}');</script>"
                components.html(js, height=0)
                st.success("Ayarlar kaydedildi", icon="✅")
                # Removed toast to use success box that won't disappear if page reloads layout too quickly

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — DEFECT ENTRY
    # ══════════════════════════════════════════════════════════════════════════
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        lines = [l["name"] for l in cfg["lines"]] if cfg["lines"] else ["Hat-1"]
        current_defects = cfg["quality"]["defects"] if cfg["quality"]["defects"] else DEFECT_TYPES
        active_shifts = [s["name"] for s in cfg.get("shifts", DEFAULT_SHIFTS) if s.get("active", True)]
        if not active_shifts:
            active_shifts = ["A"]

        left, right = st.columns([3, 2], gap="large")

        with left:
            section_header(f"{get_svg(PENCIL, size=24)} Hata Kaydı Formu")
            with st.form("defect_form", clear_on_submit=True):
                r1c1, r1c2, r1c3 = st.columns(3)
                with r1c1:
                    d_date = st.date_input("Tarih", value=date.today(), key="d_date")
                with r1c3:
                    d_line = st.selectbox("Hat", lines, key="d_line")
                with r1c2:
                    def_s = cur_shift if cur_shift in active_shifts else active_shifts[-1]
                    d_shift = st.selectbox("Vardiya", active_shifts, index=active_shifts.index(def_s), key="d_shift_sel")

                r2c1, r2c2 = st.columns(2)
                with r2c1:
                    d_type = st.selectbox("Hata Türü", current_defects, key="d_type")
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
        lines = [l["name"] for l in cfg["lines"]] if cfg["lines"] else ["Hat-1"]
        existing_points = [p["point"] for p in cfg["spc_points"]] if cfg["spc_points"] else [r[0] for r in MEASUREMENT_POINTS_DEFAULT]
        current_meta = {p["point"]: (p["point"], p["nom"], p["usl"], p["lsl"]) for p in cfg["spc_points"]} if cfg["spc_points"] else POINT_META

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
                meta = current_meta.get(m_point)
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
