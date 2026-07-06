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

    tour_dialog = ui.dialog().classes('backdrop-blur-md')
    current_idx = [0]

    def close_tour():
        app.storage.user['tour_completed'] = True
        tour_dialog.close()
        ui.notify('Tour Completed! Welcome aboard.', type='positive')

    def skip_tour():
        app.storage.user['tour_completed'] = True
        tour_dialog.close()
        ui.notify('Tour skipped. You can explore QualityPulse at your own pace.', type='info')

    with tour_dialog, ui.card().classes('p-8 w-[450px] border border-slate-200/80 shadow-2xl rounded-3xl bg-white overflow-hidden'):
        with ui.column().classes('w-full items-center gap-4 relative'):
            # Close/Skip button at top right
            with ui.row().classes('w-full justify-end -mt-2 -mr-2 absolute top-0 right-0'):
                ui.button(icon='close', on_click=skip_tour).props('flat round dense text-color=grey-6').classes('hover:bg-slate-100 transition-colors')
            
            # Step badge
            step_badge = ui.label('').classes('text-[10px] font-extrabold px-3 py-1 rounded-full bg-slate-100 text-slate-600 uppercase tracking-widest mt-2')

            # Icon container
            icon_box = ui.element('div').classes('p-5 rounded-3xl flex items-center justify-center my-1 transition-all duration-300 shadow-sm')
            with icon_box:
                icon_el = ui.icon('auto_awesome', size='48px').classes('transition-all duration-300')

            # Title & Content
            title_el = ui.label('').classes('text-xl font-black text-slate-800 tracking-tight text-center mt-1')
            content_el = ui.label('').classes('text-center text-slate-500 text-sm leading-relaxed min-h-[48px] px-2')

            # Progress Dots
            with ui.row().classes('w-full justify-center gap-2 my-2'):
                dots = []
                for i in range(len(steps)):
                    dot = ui.element('div').classes('h-1.5 rounded-full transition-all duration-300')
                    dots.append(dot)

            # Bottom Bar: Prev / Next Buttons
            with ui.row().classes('w-full mt-4 justify-between items-center pt-4 border-t border-slate-100'):
                prev_btn = ui.button('PREV', on_click=lambda: go_step(-1)).props('flat rounded').classes('text-slate-500 px-4 text-xs font-bold hover:bg-slate-100')
                next_btn = ui.button('NEXT', on_click=lambda: go_step(1)).props('rounded elevated').classes('text-white px-6 text-xs font-bold shadow-md transition-all')

    def update_view():
        idx = current_idx[0]
        step = steps[idx]

        step_badge.text = f"Step {idx + 1} of {len(steps)}"
        
        icon_el.name = step['icon']
        icon_el.classes(replace=f"{step['icon_color']} transition-all duration-300")
        icon_box.classes(replace=f"p-5 rounded-3xl flex items-center justify-center my-1 transition-all duration-300 shadow-sm {step['bg_color']}")

        title_el.text = step['title']
        content_el.text = step['content']

        for i, dot in enumerate(dots):
            if i == idx:
                dot.classes(replace='h-1.5 w-6 bg-blue-600 rounded-full transition-all duration-300 shadow-xs')
            else:
                dot.classes(replace='h-1.5 w-1.5 bg-slate-200 rounded-full transition-all duration-300')

        prev_btn.set_visibility(idx > 0)
        if idx == len(steps) - 1:
            next_btn.text = 'GET STARTED'
            next_btn.classes(replace='bg-emerald-600 text-white px-6 text-xs font-bold shadow-md hover:bg-emerald-700 transition-all')
        else:
            next_btn.text = 'NEXT'
            next_btn.classes(replace='bg-blue-600 text-white px-6 text-xs font-bold shadow-md hover:bg-blue-700 transition-all')

    def go_step(delta):
        new_idx = current_idx[0] + delta
        if new_idx >= len(steps):
            close_tour()
        elif 0 <= new_idx < len(steps):
            current_idx[0] = new_idx
            update_view()

    update_view()
    tour_dialog.open()

