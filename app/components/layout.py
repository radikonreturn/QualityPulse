from nicegui import ui

def menu():
    with ui.column().classes('w-full items-center mb-8 q-pa-md'):
        with ui.row().classes('items-center gap-3 mb-6'):
            ui.image('/assets/icon.png').classes('w-12 h-12 rounded-xl shadow-md')
            with ui.column().classes('gap-0'):
                ui.label('QualityPulse').classes('text-lg text-white font-bold tracking-tight')
                ui.label('SYSTEM v1.0').classes('text-[10px] text-blue-400 font-black tracking-widest')
        
        ui.separator().classes('bg-slate-700 opacity-30 mb-6')
        
        def nav_btn(label, icon, target):
            return ui.button(label, icon=icon, on_click=lambda: ui.navigate.to(target)) \
                .props('flat align=left no-caps') \
                .classes('w-full text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg py-2 transition-all')

        nav_btn('Dashboard', 'dashboard', '/')
        nav_btn('Pareto Analysis', 'bar_chart', '/pareto')
        nav_btn('SPC Control Chart', 'show_chart', '/spc')
        nav_btn('CAPA Management', 'build', '/capa')
        nav_btn('FMEA Risk Matrix', 'warning', '/fmea')
        
        ui.label('OPERATIONS').classes('text-[10px] text-slate-500 font-bold mt-8 mb-2 w-full px-4 tracking-widest')
        nav_btn('Data Entry', 'post_add', '/data_entry')
        nav_btn('Export Data', 'file_download', '/data_export')

def frame(page_title: str):
    ui.colors(primary='#3b82f6', secondary='#64748b', accent='#10b981')
    
    # Global styles for a more modern look
    ui.add_head_html('''
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
            body { font-family: 'Inter', sans-serif !important; background-color: #f8fafc; }
            .q-drawer { background: #0f172a !important; }
            .q-header { background: rgba(255, 255, 255, 0.8) !important; backdrop-filter: blur(8px); border-bottom: 1px solid #e2e8f0; }
            .q-page-container { background: #f8fafc; }
            .card-gradient { background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); }
        </style>
    ''')
    
    with ui.left_drawer(value=True, top_corner=True, bottom_corner=True).classes('q-pa-none border-r border-slate-800') as drawer:
        menu()
        
    with ui.header().classes('text-slate-900 q-py-sm px-6 shadow-none'):
        with ui.row().classes('w-full items-center justify-between'):
            with ui.row().classes('items-center gap-4'):
                ui.button(on_click=lambda: drawer.toggle(), icon='menu').props('flat round dense color=primary')
                ui.label(page_title).classes('text-xl font-extrabold tracking-tight text-slate-800 uppercase')
            
            with ui.row().classes('items-center gap-4'):
                ui.icon('notifications', size='20px').classes('text-slate-400 cursor-pointer')
                
                def logout():
                    from core.auth import logout_user
                    logout_user()
                    ui.navigate.to('/login')
                
                ui.button(on_click=logout, icon='logout').props('flat round dense color=negative').classes('hover:bg-red-50 transition-all')
    
    # Content wrapper
    return ui.column().classes('p-8 w-full max-w-[1600px] mx-auto animate-fade-in')
