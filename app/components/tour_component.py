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
            "icon": "auto_awesome",
            "icon_color": "text-blue-600",
            "bg_color": "bg-blue-50 border border-blue-100"
        },
        {
            "title": "Real-Time Insights",
            "content": "The Executive Insights engine uses NLP to analyze your data and highlight quality drivers instantly.",
            "icon": "psychology",
            "icon_color": "text-indigo-600",
            "bg_color": "bg-indigo-50 border border-indigo-100"
        },
        {
            "title": "Failure Hotspots",
            "content": "Your new Heatmap correlates Defect Types with Production Lines to find systematic issues.",
            "icon": "grid_view",
            "icon_color": "text-purple-600",
            "bg_color": "bg-purple-50 border border-purple-100"
        },
        {
            "title": "Secure Configuration",
            "content": "Head over to Data Entry → Configuration to set up your Shifts, Lines, and Email Alerts.",
            "icon": "settings",
            "icon_color": "text-amber-600",
            "bg_color": "bg-amber-50 border border-amber-100"
        },
        {
            "title": "Ready for Production",
            "content": "You're all set. Start logging data to see the powerhouse of analytical distribution in action!",
            "icon": "check_circle",
            "icon_color": "text-emerald-600",
            "bg_color": "bg-emerald-50 border border-emerald-100"
        }
    ]

    current_idx = [0]
    tour_dialog = ui.dialog().classes('backdrop-blur-md')

    def close_tour():
        app.storage.user['tour_completed'] = True
        tour_dialog.close()
        ui.notify('Tour Completed! Welcome aboard.', type='positive')

    def skip_tour():
        app.storage.user['tour_completed'] = True
        tour_dialog.close()
        ui.notify('Tour skipped. You can explore QualityPulse at your own pace.', type='info')

    def go_step(delta):
        new_idx = current_idx[0] + delta
        if new_idx >= len(steps):
            close_tour()
        elif 0 <= new_idx < len(steps):
            current_idx[0] = new_idx
            step_content.refresh()

    @ui.refreshable
    def step_content():
        idx = current_idx[0]
        step = steps[idx]

        with ui.column().classes('w-full items-center gap-4 relative'):
            # Close/Skip button at top right
            with ui.row().classes('w-full justify-end -mt-2 -mr-2 absolute top-0 right-0'):
                ui.button(icon='close', on_click=skip_tour) \
                    .props('flat round dense text-color=grey-6') \
                    .classes('hover:bg-slate-100 transition-colors')

            # Step badge
            ui.label(f"Step {idx + 1} of {len(steps)}") \
                .classes('text-[10px] font-extrabold px-3 py-1 rounded-full bg-slate-100 text-slate-600 uppercase tracking-widest mt-2')

            # Icon container
            with ui.element('div').classes(f'p-5 rounded-3xl flex items-center justify-center my-1 shadow-sm {step["bg_color"]}'):
                ui.icon(step['icon'], size='48px').classes(step['icon_color'])

            # Title & Content
            ui.label(step['title']) \
                .classes('text-xl font-black text-slate-800 tracking-tight text-center mt-1')
            ui.label(step['content']) \
                .classes('text-center text-slate-500 text-sm leading-relaxed min-h-[48px] px-2')

            # Progress Dots
            with ui.row().classes('w-full justify-center gap-2 my-2'):
                for i in range(len(steps)):
                    if i == idx:
                        ui.element('div').classes('h-1.5 w-6 bg-blue-600 rounded-full transition-all duration-300')
                    else:
                        ui.element('div').classes('h-1.5 w-1.5 bg-slate-200 rounded-full transition-all duration-300')

            # Bottom Bar: Prev / Next Buttons
            with ui.row().classes('w-full mt-4 justify-between items-center pt-4 border-t border-slate-100'):
                if idx > 0:
                    ui.button('PREV', on_click=lambda: go_step(-1)) \
                        .props('flat rounded') \
                        .classes('text-slate-500 px-4 text-xs font-bold hover:bg-slate-100')
                else:
                    ui.element('div')  # spacer to keep NEXT right-aligned

                if idx == len(steps) - 1:
                    ui.button('GET STARTED', on_click=lambda: go_step(1)) \
                        .props('rounded elevated') \
                        .classes('bg-emerald-600 text-white px-6 text-xs font-bold shadow-md hover:bg-emerald-700')
                else:
                    ui.button('NEXT', on_click=lambda: go_step(1)) \
                        .props('rounded elevated') \
                        .classes('bg-blue-600 text-white px-6 text-xs font-bold shadow-md hover:bg-blue-700')

    with tour_dialog:
        with ui.card().classes('p-8 w-[450px] border border-slate-200/80 shadow-2xl rounded-3xl bg-white overflow-hidden'):
            step_content()

    tour_dialog.open()
