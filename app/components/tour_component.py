from nicegui import ui, app

def guided_tour():
    """
    Triggers a multi-step guided tour of the QualityPulse ecosystem.
    Only runs if app.storage.user['tour_completed'] is not set.
    """
    if app.storage.user.get('tour_completed', False):
        return

    steps = [
        {
            "title": "Welcome to QualityPulse Elite",
            "content": "Your intelligent Digital Quality Management system is now active. Let's take a 30-second tour of your new production hub.",
            "icon": "auto_awesome"
        },
        {
            "title": "Real-Time Insights",
            "content": "The Executive Insights engine uses NLP to analyze your data and highlight quality drivers instantly.",
            "icon": "psychology"
        },
        {
            "title": "Failure Hotspots",
            "content": "Your new Heatmap correlates Defect Types with Production Lines to find systematic issues.",
            "icon": "grid_view"
        },
        {
            "title": "Secure Configuration",
            "content": "Head over to Data Entry -> Configuration to set up your Shifts, Lines, and Email Alerts.",
            "icon": "settings"
        },
        {
            "title": "Ready for Production",
            "content": "You're all set. Start logging data to see the powerhouse of analytical distribution in action!",
            "icon": "check_circle"
        }
    ]

    def show_step(index):
        if index >= len(steps):
            app.storage.user['tour_completed'] = True
            tour_dialog.close()
            ui.notify('Tour Completed! Welcome aboard.', type='positive')
            return

        step = steps[index]
        with tour_dialog, ui.card().classes('p-8 w-[400px] border-none shadow-2xl rounded-3xl'):
            with ui.column().classes('w-full items-center gap-4'):
                ui.icon(step['icon'], size='48px').classes('text-blue-500')
                ui.label(step['title']).classes('text-xl font-black text-slate-800 tracking-tighter uppercase')
                ui.label(step['content']).classes('text-center text-slate-500 text-sm')
                
                with ui.row().classes('w-full mt-4 justify-between items-center'):
                    ui.label(f"Step {index+1} of {len(steps)}").classes('text-[10px] font-bold text-slate-300 uppercase tracking-widest')
                    ui.button('NEXT', on_click=lambda: show_step(index + 1)).props('rounded elevated').classes('bg-blue-600 text-white px-6')

    tour_dialog = ui.dialog().classes('backdrop-blur-sm')
    show_step(0)
    tour_dialog.open()
