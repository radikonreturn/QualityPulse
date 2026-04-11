"""
QualityPulse — KPI Card Component
Renders styled HTML metric cards with icon, value, delta, and color variants.
"""

import streamlit as st
import streamlit.components.v1 as components
from components.icons import DASHBOARD, CHECK, ALERT, get_svg


def kpi_card(
    label: str,
    value: str,
    delta: str = "",
    delta_label: str = "",
    color: str = "blue",  # "blue" | "green" | "amber" | "red"
    icon: str = None,
    suffix: str = "",
):
    """
    Render a styled KPI card using st.markdown.

    Args:
        label:       Card title / KPI name
        value:       Primary numeric value (string, e.g. "3.24%")
        delta:       Delta string, e.g. "+0.12" or "-0.05"
        delta_label: Extra context, e.g. "vs önceki ay"
        color:       Accent color key
        icon:        SVG string
        suffix:      Unit suffix shown after value
    """
    color_map = {
        "blue":  ("#4f8ef7", "#dbeafe", "#1d4ed8"),
        "green": ("#2ecc71", "#d1fae5", "#065f46"),
        "amber": ("#f39c12", "#fef3c7", "#92400e"),
        "red":   ("#e74c3c", "#fee2e2", "#991b1b"),
    }
    accent, bg, text = color_map.get(color, color_map["blue"])

    # Default icon if none provided
    if icon is None:
        icon = get_svg(DASHBOARD, color=accent, size=24)

    # Determine delta arrow and color
    delta_html = ""
    if delta:
        delta_str = str(delta)
        # Try to determine sign from numeric value; fall back to string prefix
        try:
            numeric = float(delta_str.replace("%", "").replace("+", "").strip())
            is_positive = numeric > 0
            is_zero = numeric == 0
        except ValueError:
            # Non-numeric delta (e.g. "Toplam 5 kritik") — infer from leading sign char
            is_positive = delta_str.startswith("+")
            is_zero = False

        if is_zero:
            delta_color = "#6b7280"
            arrow = "●"
        elif is_positive:
            delta_color = "#dc2626"
            arrow = "▲"
        else:
            delta_color = "#16a34a"
            arrow = "▼"

        delta_html = f"""
        <div style="display:flex;align-items:center;gap:4px;margin-top:4px;">
            <span style="color:{delta_color};font-size:0.78rem;font-weight:600;">
                {arrow} {delta}
            </span>
            <span style="color:#9ca3af;font-size:0.72rem;">{delta_label}</span>
        </div>
        """

    full_html = f"""<!DOCTYPE html>
<html>
<head>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }}
  body {{ background: transparent; }}
</style>
</head>
<body>
<div style="
    background:#ffffff;
    border:1px solid #e8ecf0;
    border-top:3px solid {accent};
    border-radius:12px;
    padding:1.1rem 1.3rem;
    box-shadow:0 2px 8px rgba(0,0,0,0.06);
    height:100%;
">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;">
        <div>
            <div style="font-size:0.72rem;font-weight:700;text-transform:uppercase;
                        letter-spacing:0.06em;color:#6b7280;margin-bottom:0.5rem;">
                {label}
            </div>
            <div style="font-size:2rem;font-weight:800;color:#1a1a2e;
                        line-height:1;letter-spacing:-0.02em;">
                {value}<span style="font-size:1rem;font-weight:500;
                               color:#6b7280;margin-left:2px;">{suffix}</span>
            </div>
            {delta_html}
        </div>
        <div style="background:{bg};color:{accent};width:44px;height:44px;
                    border-radius:10px;display:flex;align-items:center;
                    justify-content:center;font-size:1.4rem;flex-shrink:0;">
            {icon}
        </div>
    </div>
</div>
</body></html>"""
    components.html(full_html, height=145)


def cpk_card(cpk_value: float, label: str = "Cpk"):
    """Specialized Cpk card with dynamic color based on value."""
    if cpk_value >= 1.33:
        color, status, icon_svg = "green", "Kapasiteli ✓", CHECK
    elif cpk_value >= 1.00:
        color, status, icon_svg = "amber", "Sınırda !", ALERT
    else:
        color, status, icon_svg = "red", "Yetersiz ✗", ALERT

    color_map = {
        "green": "#2ecc71",
        "amber": "#f39c12",
        "red":   "#e74c3c",
    }

    kpi_card(
        label=label,
        value=f"{cpk_value:.3f}",
        delta=status,
        delta_label="",
        color=color,
        icon=get_svg(icon_svg, color=color_map[color], size=24),
    )
