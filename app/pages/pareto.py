from nicegui import ui
from datetime import datetime, timedelta
from db.database import get_defects
from components.charts import pareto_chart
import pandas as pd

from components.layout import frame
from core.auth import auth_guard

@ui.page('/pareto')
def pareto_page():
    if not auth_guard():
        return
    with frame('Pareto Analysis'):
        content()

def content():
    today = datetime.today()
    default_start = (today - timedelta(days=90)).strftime('%Y-%m-%d')
    default_end = today.strftime('%Y-%m-%d')

    @ui.refreshable
    def chart_container(start_date, end_date):
        defects = get_defects(start_date=start_date, end_date=end_date)
        if not defects:
            with ui.column().classes('w-full items-center py-20 bg-slate-50 rounded-xl border-2 border-dashed border-slate-200'):
                ui.icon('search_off', size='4rem').classes('text-slate-300')
                ui.label('No data found for the selected period.').classes('text-slate-400 mt-4 font-medium')
            return
        
        with ui.row().classes('w-full gap-6 items-stretch'):
            with ui.card().classes('flex-[3] p-6 shadow-sm border border-slate-200 rounded-xl overflow-hidden'):
                fig = pareto_chart(defects)
                ui.plotly(fig).classes('w-full h-[500px]')
            
            with ui.column().classes('flex-[1] gap-4'):
                # Data Insights Card
                df = pd.DataFrame(defects)
                agg = df.groupby('defect_type')['quantity'].sum().sort_values(ascending=False).reset_index()
                agg['cumulative_pct'] = agg['quantity'].cumsum() / agg['quantity'].sum() * 100
                vital_few = agg[agg['cumulative_pct'] <= 85]
                
                with ui.card().classes('w-full p-6 shadow-sm border border-slate-200 rounded-xl bg-blue-50/30'):
                    ui.label('Vital Few Analysis').classes('font-bold text-slate-800 mb-4 uppercase tracking-wider text-xs')
                    ui.label(f'{len(vital_few)} Defect Types').classes('text-2xl font-black text-blue-600')
                    ui.label('account for 85% of total losses. Focus your improvement efforts here.').classes('text-xs text-slate-500 mt-1')
                
                with ui.card().classes('w-full p-0 shadow-sm border border-slate-200 rounded-xl overflow-hidden'):
                    ui.table(
                        columns=[
                            {'name': 'type', 'label': 'Defect Type', 'field': 'defect_type', 'align': 'left'},
                            {'name': 'qty', 'label': 'Qty', 'field': 'quantity', 'align': 'right'},
                        ],
                        rows=agg.to_dict('records')[:5],
                    ).classes('w-full').props('flat dense hide-bottom')

    # ── Filters ──────────────────────────────────────────────────────────────
    with ui.row().classes('w-full items-center justify-between mb-8 bg-white p-6 rounded-xl border border-slate-200 shadow-sm'):
        with ui.row().classes('items-center gap-6'):
            with ui.column().classes('gap-0'):
                ui.label('Date Range').classes('text-[10px] font-bold text-slate-400 uppercase ml-1 mb-1')
                with ui.row().classes('items-center gap-3'):
                    start_input = ui.input(value=default_start).props('type=date dense outlined').classes('w-44')
                    ui.label('to').classes('text-slate-400 font-bold')
                    end_input = ui.input(value=default_end).props('type=date dense outlined').classes('w-44')
        
        ui.button('Update Analysis', icon='refresh', 
                  on_click=lambda: chart_container.refresh(start_input.value, end_input.value)) \
            .props('elevated no-caps').classes('bg-blue-600 text-white px-8 py-2 rounded-lg h-12 font-bold')

    chart_container(default_start, default_end)

    with ui.row().classes('mt-12 w-full p-6 bg-slate-900 text-slate-300 rounded-xl items-center gap-6 shadow-xl'):
        ui.icon('lightbulb', size='3rem').classes('text-amber-400')
        with ui.column().classes('gap-1'):
            ui.label('Pareto Principle (80/20 Rule)').classes('font-bold text-white')
            ui.label('This chart identifies the "vital few" defects that cause most of your quality issues. By eliminating the top 2-3 defect types, you can reduce total scrap by up to 80%.').classes('text-sm opacity-80 leading-relaxed')
