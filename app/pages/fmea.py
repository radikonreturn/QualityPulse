from nicegui import ui
from db.database import get_all_fmea, insert_fmea
from components.charts import fmea_heatmap
from core.auth import auth_guard

def rpn_badge(rpn: int):
    """Helper to render a colored badge based on RPN."""
    if rpn >= 200:
        bg, text = '#fee2e2', '#991b1b' # Red
    elif rpn >= 100:
        bg, text = '#fef3c7', '#92400e' # Amber
    else:
        bg, text = '#d1fae5', '#065f46' # Green
    
    return ui.label(str(rpn)).style(f'background: {bg}; color: {text}; font-weight: bold; border-radius: 6px; padding: 4px 12px; min-width: 45px; text-align: center;')

from components.layout import frame

@ui.page('/fmea')
def fmea_page():
    if not auth_guard():
        return
    with frame('FMEA Risk Matrix'):
        content()

def content():
    @ui.refreshable
    def fmea_content():
        rows = get_all_fmea()
        
        with ui.row().classes('w-full gap-6 items-stretch mb-8'):
            # Heatmap Card
            with ui.card().classes('flex-[3] p-6 shadow-sm border border-slate-200 rounded-xl overflow-hidden'):
                fig = fmea_heatmap(rows)
                ui.plotly(fig).classes('w-full h-[360px]')
            
            # Risk Summary Card
            with ui.card().classes('flex-[2] p-8 shadow-sm bg-slate-50 border border-slate-200 rounded-xl'):
                ui.label('Risk Profile Summary').classes('font-bold text-slate-800 text-xs uppercase tracking-widest mb-6')
                
                high_risk = sum(1 for r in rows if r['rpn'] >= 200)
                med_risk  = sum(1 for r in rows if 100 <= r['rpn'] < 200)
                low_risk  = sum(1 for r in rows if r['rpn'] < 100)
                
                with ui.column().classes('gap-4 w-full'):
                    def risk_row(label, count, bg, text, border):
                        with ui.row().classes(f'w-full justify-between items-center {bg} p-4 rounded-xl border {border} shadow-sm'):
                            ui.label(label).classes(f'{text} font-bold text-sm')
                            ui.label(str(count)).classes(f'{text} font-black text-2xl')

                    risk_row('High Risk (RPN ≥ 200)', high_risk, 'bg-red-50', 'text-red-700', 'border-red-100')
                    risk_row('Medium Risk (100-199)', med_risk, 'bg-amber-50', 'text-amber-700', 'border-amber-100')
                    risk_row('Low Risk (RPN < 100)', low_risk, 'bg-emerald-50', 'text-emerald-700', 'border-emerald-100')

        # ── Expansion for New Entry ──────────────────────────────────────────
        with ui.expansion('Register New Failure Mode (FMEA Entry)', icon='add_alert').classes('w-full bg-white border border-slate-200 rounded-xl mb-8 shadow-sm'):
            with ui.column().classes('p-8 gap-6 w-full'):
                with ui.row().classes('w-full gap-6'):
                    step_in = ui.input('Process Step').classes('flex-1').props('outlined dense')
                    mode_in = ui.input('Potential Failure Mode').classes('flex-2').props('outlined dense')
                
                with ui.row().classes('w-full gap-6'):
                    effect_in = ui.input('Potential Failure Effects').classes('flex-1').props('outlined dense')
                    cause_in = ui.input('Potential Causes').classes('flex-1').props('outlined dense')

                with ui.row().classes('w-full gap-8 items-end'):
                    with ui.column().classes('gap-1'):
                        ui.label('Severity (S)').classes('text-[10px] font-bold text-slate-400')
                        s_in = ui.slider(min=1, max=10, value=5).classes('w-32')
                    with ui.column().classes('gap-1'):
                        ui.label('Occurrence (O)').classes('text-[10px] font-bold text-slate-400')
                        o_in = ui.slider(min=1, max=10, value=5).classes('w-32')
                    with ui.column().classes('gap-1'):
                        ui.label('Detection (D)').classes('text-[10px] font-bold text-slate-400')
                        d_in = ui.slider(min=1, max=10, value=5).classes('w-32')
                    
                    with ui.column().classes('flex-1'):
                        def save_fmea():
                            if not step_in.value or not step_in.value.strip():
                                ui.notify('Process Step is required.', type='warning')
                                return
                            if not mode_in.value or not mode_in.value.strip():
                                ui.notify('Failure Mode is required.', type='warning')
                                return
                            if not effect_in.value or not effect_in.value.strip():
                                ui.notify('Failure Effect is required.', type='warning')
                                return

                            insert_fmea(
                                process_step=step_in.value.strip(),
                                failure_mode=mode_in.value.strip(),
                                failure_effect=effect_in.value.strip(),
                                severity=int(s_in.value),
                                occurrence=int(o_in.value),
                                detection=int(d_in.value),
                                recommended_action='',
                                responsible=''
                            )
                            ui.notify(f'FMEA entry for {step_in.value} added successfully.', type='positive')
                            step_in.value = mode_in.value = effect_in.value = ''
                            fmea_content.refresh()

                        ui.button('Add to Risk Register', on_click=save_fmea, icon='security').props('elevated no-caps').classes('bg-slate-900 text-white w-full h-12 rounded-lg font-bold')

        ui.label('Failure Mode and Effects Analysis Register').classes('text-lg font-black text-slate-800 mb-4 ml-1 uppercase tracking-tighter')
        
        # FMEA List
        with ui.column().classes('w-full gap-4'):
            for r in rows:
                with ui.card().classes('w-full p-6 shadow-sm border border-slate-200 rounded-xl hover:border-blue-300 transition-all'):
                    with ui.row().classes('w-full justify-between items-center no-wrap'):
                        with ui.column().classes('gap-1 flex-1'):
                            with ui.row().classes('items-center gap-2'):
                                ui.label(r['process_step']).classes('text-[10px] text-blue-600 font-black uppercase tracking-widest bg-blue-50 px-2 py-1 rounded')
                                ui.label(f"ID: FMEA-{r['id']}").classes('text-[10px] text-slate-400 font-mono')
                            
                            ui.label(r['failure_mode']).classes('text-lg font-bold text-slate-900 leading-tight mt-1')
                            ui.label(f"Effect: {r['failure_effect']}").classes('text-xs text-slate-500 italic mt-1')
                        
                        with ui.row().classes('items-center gap-8 bg-slate-50 p-4 rounded-xl'):
                            def score_box(label, val):
                                with ui.column().classes('items-center gap-0'):
                                    ui.label(label).classes('text-[9px] text-slate-400 font-bold')
                                    ui.label(str(val)).classes('text-sm font-black text-slate-700')
                            
                            score_box('SEV', r['severity'])
                            score_box('OCC', r['occurrence'])
                            score_box('DET', r['detection'])
                            
                            with ui.column().classes('items-center gap-1'):
                                ui.label('RPN').classes('text-[9px] text-slate-400 font-black')
                                rpn_badge(r['rpn'])
                    
                    if r['recommended_action']:
                        ui.separator().classes('my-4 opacity-50')
                        with ui.row().classes('w-full items-center gap-3 p-3 bg-blue-50/50 rounded-lg border border-blue-100/50'):
                            ui.icon('auto_fix_high', size='18px').classes('text-blue-500')
                            with ui.column().classes('gap-0'):
                                ui.label(f"Mitigation: {r['recommended_action']}").classes('text-[11px] text-slate-700 font-bold')
                                if r['responsible']:
                                    ui.label(f"Owner: {r['responsible']}").classes('text-[10px] text-slate-500')
    
    fmea_content()
