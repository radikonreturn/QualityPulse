"""
QualityPulse — Insights Engine
Analyzes production data to generate natural language executive summaries.
"""

from datetime import datetime, timedelta
from collections import Counter

def generate_quality_insights(defects: list[dict]) -> list[str]:
    """
    Analyzes a list of defect records and returns a list of high-impact insight strings.
    """
    if not defects:
        return ["No production data available for analysis."]

    insights = []
    
    # 1. Pareto Winner (Worst Defect)
    type_counts = Counter(d['defect_type'] for d in defects)
    if type_counts:
        top_defect, count = type_counts.most_common(1)[0]
        total_defects = sum(type_counts.values())
        pct = (count / total_defects) * 100
        insights.append(f"**{top_defect}** remains the primary quality driver, accounting for {pct:.1f}% of total scrap.")

    # 2. Trouble Line (Worst Line)
    line_counts = {}
    for d in defects:
        line_counts[d['line']] = line_counts.get(d['line'], 0) + d['quantity']
    
    if line_counts:
        worst_line = max(line_counts, key=line_counts.get)
        line_rate = line_counts[worst_line]
        insights.append(f"**{worst_line}** is currently showing the highest instability; recommend checking tool alignment.")

    # 3. Shift Performance
    shift_counts = Counter(d['shift'] for d in defects)
    if shift_counts:
        worst_shift, s_count = shift_counts.most_common(1)[0]
        insights.append(f"Performance dip detected during **{worst_shift[:7]}**; consider review of shift-start handover procedures.")

    # 4. Trend Analysis (Simple)
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    qty_today = sum(d['quantity'] for d in defects if d['date'] == today)
    qty_yesterday = sum(d['quantity'] for d in defects if d['date'] == yesterday)
    
    if qty_today > qty_yesterday and qty_yesterday > 0:
        diff = ((qty_today - qty_yesterday) / qty_yesterday) * 100
        insights.append(f"Scrap volume is trending **up by {diff:.0f}%** compared to yesterday. Immediate audit required.")
    elif qty_today < qty_yesterday:
        insights.append("Continuous improvement detected: Daily scrap volume is trending downwards.")

    return insights

def get_defect_heatmap_data(defects: list[dict]):
    """
    Pivots defect data to create a matrix of [Line] vs [Defect Type].
    Returns (x_axis, y_axis, z_matrix)
    """
    if not defects:
        return [], [], []
    
    lines = sorted(list(set(d['line'] for d in defects)))
    d_types = sorted(list(set(d['defect_type'] for d in defects)))
    
    # Initialize matrix with zeros
    matrix = [[0 for _ in range(len(lines))] for _ in range(len(d_types))]
    
    # Fill matrix
    line_map = {name: i for i, name in enumerate(lines)}
    type_map = {name: i for i, name in enumerate(d_types)}
    
    for d in defects:
        lx = line_map[d['line']]
        ty = type_map[d['defect_type']]
        matrix[ty][lx] += d['quantity']
        
    return lines, d_types, matrix
