from nicegui import ui
from db.database import get_measurement_points, get_measurements
from utils.calculations import calculate_cpk_from_rows
from utils.spc_engine import calculate_control_limits, get_ooc_indices
from components.charts import spc_chart
from components.kpi_card import cpk_card

from components.layout import frame
from core.auth import auth_guard

@ui.page('/spc')
def spc_page():
    if not auth_guard():
        return
    with frame('Statistical Process Control'):
        content()

def content():
    points = get_measurement_points()
    if not points:
        with ui.column().classes('w-full items-center py-20 bg-slate-50 rounded-xl border-2 border-dashed border-slate-200'):
            ui.icon('monitoring', size='4rem').classes('text-slate-300')
            ui.label('No measurement data available.').classes('text-slate-400 mt-4 font-medium')
        return

    @ui.refreshable
    def spc_container(point_name):
        rows = get_measurements(measurement_point=point_name, limit=100)
        if not rows:
            ui.label('No data for this point.').classes('text-slate-400 mt-8 text-center w-full')
            return

        rows_sorted = sorted(rows, key=lambda x: x['timestamp'])
        values = [r['value'] for r in rows_sorted]
        timestamps = [r['timestamp'] for r in rows_sorted]
        
        stats = calculate_control_limits(values)
        ooc_indices = get_ooc_indices(values, stats['ucl'], stats['lcl'], stats['mean'])
        
        usl, lsl = rows[0].get('tolerance_upper'), rows[0].get('tolerance_lower')
        cpk_res = calculate_cpk_from_rows(rows)

        with ui.row().classes('w-full gap-6 mb-4 items-stretch'):
            with ui.card().classes('flex-[3] p-6 shadow-sm border border-slate-200 rounded-xl overflow-hidden'):
                fig = spc_chart(
                    values=values,
                    timestamps=timestamps,
                    cl=stats['mean'],
                    ucl=stats['ucl'],
                    lcl=stats['lcl'],
                    usl=usl,
                    lsl=lsl,
                    ooc_indices=ooc_indices,
                    point_name=point_name
                )
                ui.plotly(fig).classes('w-full h-[450px]')
            
            with ui.column().classes('flex-[1] gap-4'):
                cpk_card(cpk_res['cpk'], label=f"Cpk: {point_name}")
                
                with ui.card().classes('w-full p-6 shadow-sm bg-slate-50 border border-slate-200 rounded-xl'):
                    ui.label('Statistical Summary').classes('font-bold text-slate-800 mb-4 uppercase tracking-widest text-[10px]')
                    
                    def stat_row(label, val, color='slate-700', bold=False):
                        with ui.row().classes('w-full justify-between py-1 border-b border-slate-200/50'):
                            ui.label(label).classes('text-xs text-slate-500')
                            ui.label(f"{val:.4f}").classes(f'text-xs text-{color} {"font-bold" if bold else ""}')

                    stat_row('Process Mean (X̄)', stats['mean'], 'blue-600', True)
                    stat_row('Upper Control Limit (UCL)', stats['ucl'], 'red-600')
                    stat_row('Lower Control Limit (LCL)', stats['lcl'], 'red-600')
                    stat_row('Standard Deviation (σ)', stats['sigma'])
                    
                    with ui.row().classes('w-full justify-between mt-4 bg-white p-2 rounded border border-slate-200'):
                        ui.label('Sample Count').classes('text-xs text-slate-400 font-bold')
                        ui.label(str(len(values))).classes('text-xs text-slate-900 font-black')

    # ── Selection ────────────────────────────────────────────────────────────
    with ui.row().classes('w-full items-center justify-between mb-8 bg-white p-6 rounded-xl border border-slate-200 shadow-sm'):
        with ui.row().classes('items-center gap-4'):
            ui.icon('settings_input_component', size='24px').classes('text-blue-600')
            ui.label('Select Control Point:').classes('font-bold text-slate-800')
            select = ui.select(points, value=points[0], 
                               on_change=lambda e: spc_container.refresh(e.value)) \
                               .props('outlined dense options-dense').classes('min-w-[300px]')
        
        with ui.row().classes('items-center gap-2'):
            ui.badge('Nelson Rules Active', color='green').props('outline')

    spc_container(points[0])
