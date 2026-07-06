from nicegui import app, ui

from core.auth import authenticate, login_user, logout_user


@ui.page('/login')
def login_page():
    if app.storage.user.get('authenticated', False):
        ui.navigate.to('/')
        return

    def try_login():
        user = authenticate(email.value, password.value)
        if not user:
            ui.notify('Invalid email or password', type='negative', position='top')
            return

        login_user(user["email"], user["tenant_id"])
        ui.navigate.to('/')

    with ui.column().classes('absolute-center w-full items-center p-4'):
        with ui.card().classes('w-full max-w-md p-10 shadow-2xl border-none backdrop-blur-md bg-white/70 rounded-3xl'):
            with ui.column().classes('w-full items-center gap-6'):
                ui.avatar('security', color='blue-600', text_color='white', size='64px').classes('shadow-lg shadow-blue-200')
                with ui.column().classes('items-center gap-0'):
                    ui.label('QualityPulse').classes('text-3xl font-black text-slate-900 tracking-tighter')
                    ui.label('SAAS TENANT LOGIN').classes('text-[10px] font-black tracking-[0.3em] text-blue-500 uppercase')

                ui.label('Sign in with your company account.').classes('text-center text-slate-500 text-sm font-medium mt-2 px-4')

                email = ui.input('Email').classes('w-full mt-4').props('outlined rounded dense autofocus')
                password = ui.input('Password', password=True).classes('w-full').props('outlined rounded dense')
                email.on('keydown.enter', try_login)
                password.on('keydown.enter', try_login)

                ui.button('SIGN IN', on_click=try_login).props('elevated rounded-xl').classes('w-full h-14 bg-blue-600 text-white font-bold mt-4 shadow-lg shadow-blue-100')

                with ui.column().classes('w-full items-center gap-1 mt-4'):
                    ui.label('Bootstrap account: admin@example.com').classes('text-[10px] text-slate-400 font-bold uppercase tracking-widest')
                    ui.label('Password: admin2026').classes('text-[10px] text-slate-400 font-bold uppercase tracking-widest')


@ui.page('/logout')
def logout_page():
    logout_user()
    ui.navigate.to('/login')
