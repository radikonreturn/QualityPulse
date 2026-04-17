from nicegui import ui, app
from typing import Optional

# Professional Security Constants
DEFAULT_ADMIN_PASS = "admin2026"

def login_page():
    def try_login():
        if password.value == app.storage.user.get('admin_password', DEFAULT_ADMIN_PASS):
            app.storage.user['authenticated'] = True
            ui.navigate.to('/')
        else:
            ui.notify('Invalid Credentials', type='negative', position='top')

    @ui.page('/login')
    def login():
        if app.storage.user.get('authenticated', False):
            ui.navigate.to('/')
            return

        with ui.column().classes('absolute-center w-full items-center p-4'):
            # Glassmorphism Container
            with ui.card().classes('w-full max-w-md p-10 shadow-2xl border-none backdrop-blur-md bg-white/70 rounded-3xl'):
                with ui.column().classes('w-full items-center gap-6'):
                    # Brand Header
                    ui.avatar('security', color='blue-600', text_color='white', size='64px').classes('shadow-lg shadow-blue-200')
                    with ui.column().classes('items-center gap-0'):
                        ui.label('QualityPulse Elite').classes('text-3xl font-black text-slate-900 tracking-tighter')
                        ui.label('SECURE GATEWAY').classes('text-[10px] font-black tracking-[0.3em] text-blue-500 uppercase')
                    
                    ui.label('Please enter your administrative password to access the quality hub.').classes('text-center text-slate-500 text-sm font-medium mt-2 px-4')
                    
                    # Form
                    password = ui.input('Password', password=True).classes('w-full mt-4').props('outlined rounded dense autofocus')
                    password.on('keydown.enter', try_login)
                    
                    ui.button('UNLOCK HUB', on_click=try_login).props('elevated rounded-xl').classes('w-full h-14 bg-blue-600 text-white font-bold mt-4 shadow-lg shadow-blue-100')
                    
                    with ui.row().classes('w-full justify-center mt-6'):
                        ui.label('© 2026 QualityPulse Manufacturing Systems').classes('text-[10px] text-slate-400 font-bold uppercase tracking-widest')

    return login
