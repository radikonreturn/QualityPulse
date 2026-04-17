from nicegui import ui
from datetime import datetime
from db.database import get_all_capa, insert_capa, update_capa_status

from components.layout import frame

@ui.page('/capa')
def capa_page():
    with frame('CAPA Management'):
        content()

def content():
    @ui.refreshable
    def capa_list_container():
        sev_bands = [(1, 3, "Low (1-3)"), (4, 6, "Medium (4-6)"), (7, 10, "High (7-10)")]
        rows = get_all_capa()
        if not rows:
            with ui.column().classes('w-full items-center py-12 bg-slate-50 rounded-xl border-2 border-dashed border-slate-200'):
                ui.icon('assignment_turned_in', size='4rem').classes('text-slate-300')
                ui.label('No CAPA records found.').classes('text-slate-400 mt-4 font-medium')
            return

        with ui.column().classes('w-full gap-4'):
            for r in rows:
                is_overdue = r['status'] != 'Closed' and r['due_date'] < datetime.now().strftime('%Y-%m-%d')
                
                card_color = {
                    'Critical': 'border-red-500 bg-red-50/10',
                    'Major':    'border-amber-500 bg-amber-50/10',
                    'Minor':    'border-blue-500 bg-blue-50/10'
                }.get(r['criticality'], 'border-slate-200')

                status_color = {
                    'Open':        'text-blue-600',
                    'In Progress': 'text-amber-600',
                    'Closed':      'text-emerald-600'
                }.get(r['status'], 'text-slate-600')

                with ui.card().classes(f'w-full p-0 shadow-sm border-l-4 {card_color} overflow-hidden rounded-xl border-y border-r border-slate-200'):
                    with ui.row().classes('w-full p-5 items-center gap-6 no-wrap'):
                        # Status & Criticality
                        with ui.column().classes('items-center min-w-[120px] bg-slate-50 p-3 rounded-lg'):
                            ui.label(r['status']).classes(f'font-bold {status_color} text-xs uppercase tracking-widest')
                            ui.badge(r['criticality'], color='red' if r['criticality'] == 'Critical' else 'orange' if r['criticality'] == 'Major' else 'blue').props('outline dense').classes('text-[10px] mt-1')
                        
                        # Content
                        with ui.column().classes('flex-1 gap-1'):
                            with ui.row().classes('items-center gap-2'):
                                ui.label(r['title']).classes('text-base font-bold text-slate-900')
                                if is_overdue:
                                    ui.badge('OVERDUE', color='red').classes('animate-pulse')
                            
                            ui.label(r['description']).classes('text-xs text-slate-500 line-clamp-2 leading-relaxed')
                            
                            with ui.row().classes('items-center gap-6 mt-3'):
                                with ui.row().classes('items-center gap-1'):
                                    ui.icon('person', size='14px').classes('text-slate-400')
                                    ui.label(f"Owner: {r['owner']}").classes('text-[10px] text-slate-500 font-bold')
                                with ui.row().classes('items-center gap-1'):
                                    ui.icon('event', size='14px').classes('text-slate-400')
                                    ui.label(f"Due: {r['due_date']}").classes(f'text-[10px] {"text-red-600 font-bold" if is_overdue else "text-slate-500"}')

                        # Actions
                        if r['status'] != 'Closed':
                            with ui.row().classes('gap-2 pr-4'):
                                if r['status'] == 'Open':
                                    with ui.button(icon='play_arrow', 
                                              on_click=lambda r=r: [update_capa_status(r['id'], 'In Progress'), ui.notify('Status updated: In Progress'), capa_list_container.refresh()]
                                             ).props('flat round color=amber'):
                                        ui.tooltip('Start Action')
                                
                                with ui.button(icon='check_circle', 
                                          on_click=lambda r=r: [update_capa_status(r['id'], 'Closed', datetime.now().strftime('%Y-%m-%d')), ui.notify('CAPA Closed Successfully'), capa_list_container.refresh()]
                                         ).props('flat round color=green'):
                                    ui.tooltip('Close CAPA')

    # ── Input Form ───────────────────────────────────────────────────────────
    with ui.expansion('Create New Corrective Action (CAPA)', icon='add_circle').classes('w-full bg-white border border-slate-200 rounded-xl mb-8 shadow-sm'):
        with ui.column().classes('p-8 gap-6 w-full'):
            with ui.row().classes('w-full gap-6'):
                title_in = ui.input('Action Title / Subject').classes('flex-2').props('outlined dense')
                owner_in = ui.input('Responsible Owner').classes('flex-1').props('outlined dense')
                date_in = ui.input('Due Date', value=datetime.today().strftime('%Y-%m-%d')).props('type=date outlined dense').classes('w-48')
            
            desc_in = ui.textarea('Problem Description and Root Cause Analysis').classes('w-full').props('outlined')
            
            with ui.row().classes('w-full justify-between items-center mt-2'):
                crit_in = ui.select(['Minor', 'Major', 'Critical'], label='Criticality', value='Major').props('outlined dense options-dense').classes('w-48')
                
                def save_capa():
                    if not title_in.value or not title_in.value.strip():
                        ui.notify('Action Title is required.', type='warning')
                        return
                    if not owner_in.value or not owner_in.value.strip():
                        ui.notify('Responsible Owner is required.', type='warning')
                        return
                    if not desc_in.value or not desc_in.value.strip():
                        ui.notify('Problem Description is required.', type='warning')
                        return

                    insert_capa(
                        created_date=datetime.now().strftime('%Y-%m-%d'),
                        title=title_in.value.strip(),
                        description=desc_in.value.strip(),
                        root_cause='',
                        corrective_action='',
                        owner=owner_in.value.strip(),
                        due_date=date_in.value,
                        criticality=crit_in.value
                    )
                    ui.notify('CAPA Successfully Created', type='positive')
                    title_in.value = owner_in.value = desc_in.value = ''
                    capa_list_container.refresh()

                ui.button('Initialize CAPA', on_click=save_capa, icon='bolt').props('elevated no-caps').classes('bg-blue-600 text-white px-10 py-2 h-12 font-bold rounded-lg')

    # ── Header ───────────────────────────────────────────────────────────────
    with ui.row().classes('w-full items-center justify-between mb-4 px-1'):
        ui.label('Active Action Items').classes('text-lg font-black text-slate-800 uppercase tracking-tighter')
        with ui.row().classes('gap-2'):
            ui.badge('Open', color='blue')
            ui.badge('In Progress', color='amber')
            ui.badge('Closed', color='green')

    capa_list_container()
