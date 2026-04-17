from nicegui import ui, app
import collections
from datetime import datetime
from db.database import (
    insert_defect, insert_measurement
)
from components.layout import frame

# ── Constants ─────────────────────────────────────────────────────────────────
DEFECT_TYPES_DEFAULT = ["Dimensional Deviation", "Surface Defect", "Porosity", "Shrinkage", "Flash"]
MEASUREMENT_POINTS_DEFAULT = [
    ("Diameter-A", 50.00, 50.10, 49.90),
    ("Diameter-B", 25.00, 25.05, 24.95),
]
DEFAULT_SHIFTS = [
    {"name": "Shift 1 (08-16)", "label": "Morning", "start": 8,  "end": 16, "active": True},
    {"name": "Shift 2 (16-00)", "label": "Evening", "start": 16, "end": 0,  "active": True},
    {"name": "Shift 3 (00-08)", "label": "Night",   "start": 0,  "end": 8,  "active": True},
]

def _shift_now(shift_cfg) -> str:
    h = datetime.now().hour
    for s in shift_cfg:
        start, end = int(s["start"]), int(s["end"])
        if start < end:
            if start <= h < end: return s["name"]
        else: # Overnight shift
            if h >= start or h < end: return s["name"]
    return shift_cfg[0]["name"]

@ui.page('/data_entry')
def data_entry_page():
    if 'config' not in app.storage.user:
        app.storage.user['config'] = {
            "company": {"name": "QualityPulse Demo", "sector": "Metal Casting", "facility": "Plant-1", "city": "Istanbul", "employees": 150, "qe": "Admin"},
            "lines": [{"name": "Line-1", "shifts": 3, "target": 100}, {"name": "Line-2", "shifts": 3, "target": 100}],
            "quality": {"defects": DEFECT_TYPES_DEFAULT.copy(), "scrap_target": 2.0},
            "spc_points": [{"point": r[0], "nom": r[1], "usl": r[2], "lsl": r[3]} for r in MEASUREMENT_POINTS_DEFAULT],
            "shifts": DEFAULT_SHIFTS,
        }
    
    cfg = app.storage.user['config']
    
    with frame('Data Entry Center'):
        content(cfg)

def content(cfg):
    today_str = datetime.now().strftime('%Y-%m-%d')
    lines = [l["name"] for l in cfg["lines"]]
    defect_types = cfg["quality"]["defects"]
    cur_shift = _shift_now(cfg["shifts"])

    with ui.tabs().classes('w-full border-b border-slate-200') as tabs:
        defect_tab = ui.tab('DEFECT LOGGING', icon='report_problem')
        measure_tab = ui.tab('MEASUREMENT ENTRY', icon='straighten')
        settings_tab = ui.tab('CONFIGURATION', icon='settings')

    with ui.tab_panels(tabs, value=defect_tab).classes('w-full bg-transparent p-0'):
        # ── Defect Entry Panel ───────────────────────────────────────────────
        with ui.tab_panel(defect_tab):
            with ui.row().classes('w-full gap-8 items-stretch mt-4'):
                with ui.column().classes('flex-[2] gap-6'):
                    with ui.card().classes('w-full p-8 shadow-sm border border-slate-200 rounded-2xl'):
                        ui.label('Production Defect Form').classes('text-xl font-black text-slate-800 mb-6 uppercase tracking-tighter')
                        
                        with ui.row().classes('w-full gap-4'):
                            date_v = ui.input('Date', value=today_str).props('type=date outlined dense').classes('flex-1')
                            line_v = ui.select(lines, label='Production Line', value=lines[0]).props('outlined dense').classes('flex-1')
                        
                        with ui.row().classes('w-full gap-4 mt-2'):
                            shift_v = ui.select([s["name"] for s in cfg["shifts"]], label='Shift', value=cur_shift).props('outlined dense').classes('flex-1')
                            op_v = ui.input('Operator Name', value=cfg["company"]["qe"]).props('outlined dense').classes('flex-1')

                        with ui.row().classes('w-full gap-4 mt-2'):
                            type_v = ui.select(defect_types, label='Defect Type', value=defect_types[0]).props('outlined dense').classes('flex-2')
                            qty_v = ui.number('Defect Qty', value=0, min=0).props('outlined dense').classes('flex-1')
                            total_v = ui.number('Total Produced', value=300, min=1).props('outlined dense').classes('flex-1')

                        # Upload State
                        upload_data = {'path': None}
                        
                        def handle_upload(e):
                            import os
                            import uuid
                            from main import UPLOAD_DIR
                            
                            ext = os.path.splitext(e.name)[1]
                            fname = f"{uuid.uuid4()}{ext}"
                            fpath = os.path.join(UPLOAD_DIR, fname)
                            
                            with open(fpath, 'wb') as f:
                                f.write(e.content.read())
                            
                            upload_data['path'] = f"uploads/{fname}"
                            ui.notify(f'Photo uploaded: {e.name}', type='info')

                        with ui.row().classes('w-full mt-4 p-4 bg-slate-50 rounded-xl border border-dashed border-slate-200'):
                            ui.label('ATTACH PHOTO (OPTIONAL)').classes('text-[10px] font-bold text-slate-400 w-full mb-2')
                            ui.upload(on_upload=handle_upload, label="Click or Drag Image", auto_upload=True) \
                                .props('flat bordered color=primary').classes('w-full text-xs')

                        def submit_defect():
                            if not op_v.value or not op_v.value.strip():
                                ui.notify('Please enter operator name.', type='warning')
                                return
                            if qty_v.value > total_v.value:
                                ui.notify('Defect quantity cannot exceed total production.', type='warning')
                                return
                                
                            insert_defect(
                                date=date_v.value, shift=shift_v.value, defect_type=type_v.value,
                                quantity=int(qty_v.value), total_produced=int(total_v.value),
                                line=line_v.value, operator=op_v.value.strip(),
                                photo_path=upload_data['path']
                            )
                            ui.notify(f'Successfully logged {qty_v.value} defects for {line_v.value}', type='positive')
                            qty_v.value = 0
                            upload_data['path'] = None # Reset for next entry
                            summary_container.refresh()

                        ui.button('Submit Record to Database', on_click=submit_defect, icon='send') \
                            .props('elevated no-caps').classes('bg-blue-600 text-white mt-8 w-full py-3 h-14 font-bold rounded-xl shadow-lg shadow-blue-200')

                    @ui.refreshable
                    def summary_container():
                        from db.database import get_defects
                        today_defects = get_defects(start_date=today_str)
                        if not today_defects: return
                        
                        ui.label('Shift Summary (Today)').classes('text-[10px] font-black text-slate-400 uppercase mt-8 mb-2 ml-1 tracking-widest')
                        with ui.card().classes('w-full p-0 shadow-sm border border-slate-200 rounded-xl overflow-hidden'):
                            data = []
                            for shift in [s["name"] for s in cfg["shifts"]]:
                                s_defects = [d for d in today_defects if d['shift'] == shift]
                                if s_defects:
                                    total_err = sum(d['quantity'] for d in s_defects)
                                    total_prod = sum(d['total_produced'] for d in s_defects)
                                    rate = (total_err / total_prod * 100) if total_prod > 0 else 0
                                    data.append({'Shift': shift, 'Defects': total_err, 'Produced': total_prod, 'Rate': f"{rate:.2f}%"})
                            if data:
                                ui.table(columns=[
                                    {'name': 's', 'label': 'Shift', 'field': 'Shift', 'align': 'left'},
                                    {'name': 'h', 'label': 'Defects', 'field': 'Defects', 'align': 'center'},
                                    {'name': 'u', 'label': 'Produced', 'field': 'Produced', 'align': 'center'},
                                    {'name': 'o', 'label': 'Rate', 'field': 'Rate', 'align': 'right'},
                                ], rows=data).classes('w-full').props('flat dense hide-bottom')
                    summary_container()

                with ui.column().classes('flex-[1] gap-6'):
                    with ui.card().classes('w-full p-6 shadow-sm border border-slate-200 rounded-2xl bg-slate-900 text-white'):
                        ui.label('Quick Statistics').classes('text-xs font-bold text-blue-400 uppercase tracking-widest mb-4')
                        with ui.column().classes('gap-4'):
                            with ui.row().classes('w-full justify-between items-center'):
                                ui.label('Today Total Scrap').classes('text-sm text-slate-300')
                                ui.label('124').classes('text-xl font-black text-white')
                            with ui.row().classes('w-full justify-between items-center'):
                                ui.label('Current Yield').classes('text-sm text-slate-300')
                                ui.label('97.2%').classes('text-xl font-black text-emerald-400')
                    
                    with ui.card().classes('w-full p-6 shadow-sm border border-slate-200 rounded-2xl bg-white'):
                        ui.label('Recent Activity').classes('text-xs font-bold text-slate-400 uppercase tracking-widest mb-4')
                        ui.label('No recent submissions in this session.').classes('text-xs text-slate-400 italic')

        # ── Measurement Entry Panel ──────────────────────────────────────────
        with ui.tab_panel(measure_tab):
            points_map = {p["point"]: p for p in cfg["spc_points"]}
            with ui.card().classes('max-w-2xl mx-auto p-10 shadow-xl border border-slate-200 rounded-3xl mt-8'):
                with ui.row().classes('items-center gap-4 mb-8'):
                    ui.avatar('straighten', color='blue-600', text_color='white')
                    with ui.column().classes('gap-0'):
                        ui.label('Quality Measurement').classes('text-2xl font-black text-slate-800 tracking-tighter')
                        ui.label('Precision part inspection log').classes('text-xs text-slate-400 font-medium')
                
                with ui.row().classes('w-full gap-4 mb-6'):
                    line_m = ui.select(lines, label='Production Line', value=lines[0]).props('outlined dense').classes('flex-1')
                    point_m_select = ui.select(list(points_map.keys()), label='Control Point', value=list(points_map.keys())[0]).props('outlined dense').classes('flex-2')
                
                p_cfg = points_map[point_m_select.value]
                
                with ui.row().classes('w-full items-center gap-6 p-6 bg-slate-50 rounded-2xl border border-slate-100 mb-8'):
                    val_m = ui.number('Measured Value (mm)', value=p_cfg['nom'], format='%.4f').props('outlined').classes('flex-1 bg-white rounded-lg')
                    with ui.column().classes('gap-2'):
                        with ui.badge('SPECS', color='slate-700').classes('px-2 py-1'):
                            ui.label(f"USL: {p_cfg['usl']:.3f} | LSL: {p_cfg['lsl']:.3f}").classes('text-[10px] font-bold')
                
                def update_m_specs(e):
                    p = points_map[e.value]
                    val_m.value = p['nom']
                point_m_select.on('update:model-value', update_m_specs)

                def submit_measure():
                    # Dynamic lookup of current point config to avoid stale closures
                    current_point = point_m_select.value
                    current_cfg = points_map.get(current_point)
                    
                    if not current_cfg:
                        ui.notify('Invalid control point configuration.', type='negative')
                        return
                    
                    if val_m.value is None:
                        ui.notify('Please enter a measurement value.', type='warning')
                        return

                    insert_measurement(
                        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        line=line_m.value, 
                        measurement_point=current_point,
                        value=float(val_m.value), 
                        nominal=current_cfg['nom'],
                        tolerance_upper=current_cfg['usl'], 
                        tolerance_lower=current_cfg['lsl']
                    )
                    ui.notify(f'Measurement for {current_point} recorded: {val_m.value:.4f}', type='positive')
                
                ui.button('Save Inspection Data', on_click=submit_measure, icon='save_alt') \
                    .props('elevated no-caps').classes('bg-emerald-600 text-white w-full h-16 mt-4 font-bold rounded-2xl shadow-lg shadow-emerald-100')

        # ── Settings Panel ──────────────────────────────────────────────────
        with ui.tab_panel(settings_tab):
            with ui.row().classes('w-full gap-8 items-start mt-4'):
                with ui.card().classes('flex-1 p-8 shadow-sm border border-slate-200 rounded-2xl'):
                    ui.label('Enterprise Configuration').classes('text-lg font-black mb-6 uppercase tracking-tighter')
                    c_name = ui.input('Company Name', value=cfg["company"]["name"]).classes('w-full mb-2').props('outlined dense')
                    c_fac = ui.input('Facility / Plant', value=cfg["company"]["facility"]).classes('w-full mb-2').props('outlined dense')
                    c_qe = ui.input('Quality Lead', value=cfg["company"]["qe"]).classes('w-full mb-6').props('outlined dense')
                    
                    def save_local_settings():
                        cfg["company"]["name"] = c_name.value
                        cfg["company"]["facility"] = c_fac.value
                        cfg["company"]["qe"] = c_qe.value
                        app.storage.user['config'] = cfg
                        ui.notify('Configuration Updated', type='positive')

                    ui.button('Apply Changes', on_click=save_local_settings, icon='save').props('outlined').classes('w-full text-blue-600 font-bold h-12 rounded-xl')

                with ui.card().classes('flex-1 p-8 shadow-sm bg-slate-50 border border-slate-200 rounded-2xl'):
                    ui.label('System Health').classes('text-lg font-black mb-6 uppercase tracking-tighter')
                    ui.label(f"Active Lines: {len(cfg['lines'])}").classes('text-sm font-bold text-slate-700')
                    ui.label(f"Defined Defect Types: {len(defect_types)}").classes('text-sm text-slate-500 mt-1')
                    ui.label(f"SPC Points: {len(cfg['spc_points'])}").classes('text-sm text-slate-500 mt-1')
                    
                    ui.separator().classes('my-6')
                    ui.label('Last Database Sync: Just Now').classes('text-[10px] text-slate-400 font-black tracking-widest uppercase')
