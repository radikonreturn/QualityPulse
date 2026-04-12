"""
QualityPulse — Chart Builders
Polished Plotly charts with a modern, professional aesthetic.
"""

import plotly.graph_objects as go
import pandas as pd
from typing import List, Optional

# ── Modern UI Theme Palette ──
PALETTE = {
    "primary":  "#3b82f6", # Blue 500
    "success":  "#10b981", # Emerald 500
    "warning":  "#f59e0b", # Amber 500
    "danger":   "#ef4444", # Red 500
    "bg":       "#ffffff",
    "grid":     "#f1f5f9", # Slate 100
    "text":     "#0f172a", # Slate 900
    "muted":    "#64748b", # Slate 500
}

_LAYOUT_DEFAULTS = dict(
    paper_bgcolor="rgba(0,0,0,0)", # Transparent to match container
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", size=12),
    margin=dict(l=40, r=20, t=60, b=40),
    legend=dict(
        bgcolor="rgba(255,255,255,0.0)",
        font=dict(size=11),
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    hoverlabel=dict(
        font=dict(family="Inter, sans-serif", size=12),
    ),
)


def _apply_defaults(fig: go.Figure, title: str = "", height: int = 360) -> go.Figure:
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>", 
            font=dict(size=14),
            x=0, xanchor="left",
            pad=dict(b=10)
        ),
        height=height,
        **_LAYOUT_DEFAULTS,
    )
    fig.update_xaxes(
        showgrid=False, 
        zeroline=False, 
        tickfont=dict(size=10)
    )
    fig.update_yaxes(
        showgrid=True, 
        gridcolor="rgba(128,128,128,0.2)", 
        zeroline=False, 
        tickfont=dict(size=10)
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD CHARTS
# ─────────────────────────────────────────────────────────────────────────────

def scrap_trend_chart(trend_data: list[dict], threshold: float = 3.0) -> go.Figure:
    """30-day scrap rate trend — polished area chart."""
    df = pd.DataFrame(trend_data)
    fig = go.Figure()

    # Smooth spline line with area fill
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["scrap_rate"],
        mode="lines",
        name="Hurda Oranı",
        line=dict(color=PALETTE["primary"], width=3, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(59, 130, 246, 0.08)",
        hovertemplate="<b>%{x}</b><br>Hurda: %{y:.2f}%<extra></extra>",
    ))

    # Threshold line
    fig.add_hline(
        y=threshold, line_dash="dot", line_color=PALETTE["danger"],
        line_width=1.5,
        annotation_text=f"Target {threshold}%",
        annotation_position="top right",
        annotation_font=dict(color=PALETTE["danger"], size=10),
    )

    _apply_defaults(fig, "30 Günlük Hurda Oranı Trendi", height=320)
    fig.update_yaxes(ticksuffix="%")
    return fig


def defect_donut_chart(defects: list[dict]) -> go.Figure:
    """Monthly defect breakdown — modern donut chart."""
    df = pd.DataFrame(defects)
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="Veri yok", x=0.5, y=0.5, showarrow=False)
        return _apply_defaults(fig, "Bu Ayki Hata Dağılımı", 320)

    agg = df.groupby("defect_type")["quantity"].sum().reset_index()
    # Refined palette
    colors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4", "#f43f5e"]

    fig = go.Figure(go.Pie(
        labels=agg["defect_type"],
        values=agg["quantity"],
        hole=0.7,
        marker=dict(colors=colors, line=dict(color="#fff", width=2)),
        textinfo="none", # Keep it clean, use hover
        hovertemplate="<b>%{label}</b><br>Adet: %{value}<br>Oran: %{percent}<extra></extra>",
    ))
    
    _apply_defaults(fig, "Bu Ayki Hata Dağılımı", 320)
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="v", x=1.0, y=0.5, xanchor="left", yanchor="middle"),
        margin=dict(r=120),
        annotations=[dict(text="Hata Türleri", x=0.5, y=0.5, font=dict(size=12, weight=600), showarrow=False)],
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# PARETO CHART
# ─────────────────────────────────────────────────────────────────────────────

def pareto_chart(defects: list[dict]) -> go.Figure:
    """Pareto chart: modern vibrant bars + glowing cumulative line."""
    df = pd.DataFrame(defects)
    if df.empty:
        fig = go.Figure()
        return _apply_defaults(fig, "Pareto Analizi", 420)

    agg = df.groupby("defect_type")["quantity"].sum().reset_index()
    agg = agg.sort_values("quantity", ascending=False).reset_index(drop=True)
    agg["cumulative_pct"] = agg["quantity"].cumsum() / agg["quantity"].sum() * 100

    # Bars: Highlight vital few (80/20 rule) with premium aesthetics
    # Vital few: Glassy primary blue. Trivial many: Translucent muted slate.
    colors = [
        "rgba(59, 130, 246, 0.85)" if p <= 85 else "rgba(100, 116, 139, 0.15)"
        for p in agg["cumulative_pct"]
    ]
    marker_line_color = [
        "rgba(59, 130, 246, 1.0)" if p <= 85 else "rgba(100, 116, 139, 0.4)"
        for p in agg["cumulative_pct"]
    ]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=agg["defect_type"], y=agg["quantity"],
        name="Hata Adedi",
        marker=dict(
            color=colors, 
            line=dict(color=marker_line_color, width=1.5)
        ),
        text=agg["quantity"],
        textposition="auto",
        textfont=dict(family="Inter, sans-serif"),
        yaxis="y1",
        hovertemplate="<b>%{x}</b><br>Adet: %{y}<extra></extra>",
    ))

    # Glow effect for the cumulative line
    fig.add_trace(go.Scatter(
        x=agg["defect_type"], y=agg["cumulative_pct"],
        mode="lines",
        name="Kümülatif % G",
        line=dict(color="rgba(245, 158, 11, 0.25)", width=8, shape="spline"),
        hoverinfo="skip",
        showlegend=False,
        yaxis="y2",
    ))

    # Actual cumulative percentage line
    fig.add_trace(go.Scatter(
        x=agg["defect_type"], y=agg["cumulative_pct"],
        name="Kümülatif %",
        mode="lines+markers",
        line=dict(color=PALETTE["warning"], width=3, shape="spline"),
        marker=dict(size=9, color=PALETTE["warning"], line=dict(width=2, color="#ffffff")),
        yaxis="y2",
        hovertemplate="%{y:.1f}%<extra></extra>",
    ))

    _apply_defaults(fig, "Hata Türleri Pareto Analizi", 420)
    fig.update_layout(
        yaxis=dict(title="", showgrid=True, gridcolor="rgba(128,128,128,0.1)"),
        yaxis2=dict(title="", overlaying="y", side="right", range=[0, 105], ticksuffix="%", showgrid=False),
        legend=dict(x=1, y=1.1, orientation="h", xanchor="right", yanchor="bottom"),
        margin=dict(t=80),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# SPC CHART
# ─────────────────────────────────────────────────────────────────────────────

def spc_chart(
    values: List[float],
    timestamps: List[str],
    cl: float,
    ucl: float,
    lcl: float,
    usl: Optional[float],
    lsl: Optional[float],
    ooc_indices: List[int],
    point_name: str = "",
) -> go.Figure:
    """X-bar SPC control chart — clean and data-focused."""
    fig = go.Figure()
    x_labels = [t[:16] for t in timestamps]

    # Main measurement line
    fig.add_trace(go.Scatter(
        x=x_labels, y=values,
        mode="lines+markers",
        name="Ölçüm",
        line=dict(color="#cbd5e1", width=1.5),
        marker=dict(size=6, color=PALETTE["primary"], line=dict(width=1, color="white")),
        hovertemplate="<b>%{x}</b><br>Değer: %{y:.4f}<extra></extra>",
    ))

    # Highlight violations
    if ooc_indices:
        ooc_x = [x_labels[i] for i in ooc_indices]
        ooc_y = [values[i] for i in ooc_indices]
        fig.add_trace(go.Scatter(
            x=ooc_x, y=ooc_y,
            mode="markers",
            name="Kontrol Dışı",
            marker=dict(size=10, color=PALETTE["danger"], symbol="circle", line=dict(width=2, color="white")),
            hovertemplate="<b>%{x}</b><br>Değer: %{y:.4f} <span style='color:red;'>⚠️</span><extra></extra>",
        ))

    # Add lines (CL, UCL, LCL)
    for y_val, color, style, label in [
        (cl,  PALETTE["success"], "solid", f"CL {cl:.3f}"),
        (ucl, PALETTE["danger"],  "dash",  f"UCL {ucl:.3f}"),
        (lcl, PALETTE["danger"],  "dash",  f"LCL {lcl:.3f}"),
    ]:
        fig.add_hline(y=y_val, line_dash=style, line_color=color, line_width=1.5, opacity=0.6,
                       annotation_text=label, annotation_position="top right")

    # USL/LSL if provided
    if usl is not None:
        fig.add_hline(y=usl, line_color="#94a3b8", line_width=1, line_dash="dot",
                       annotation_text=f"USL {usl}", annotation_position="bottom right")
    if lsl is not None:
        fig.add_hline(y=lsl, line_color="#94a3b8", line_width=1, line_dash="dot",
                       annotation_text=f"LSL {lsl}", annotation_position="top right")

    _apply_defaults(fig, f"SPC Kontrol Grafiği: {point_name}", height=420)
    fig.update_xaxes(tickangle=-45, nticks=10)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# FMEA HEATMAP
# ─────────────────────────────────────────────────────────────────────────────

def fmea_heatmap(fmea_rows: list[dict]) -> go.Figure:
    """Refined FMEA Risk Heatmap."""
    if not fmea_rows:
        fig = go.Figure()
        return _apply_defaults(fig, "FMEA Risk Matrisi", 360)

    sev_bands = [(1, 3, "Düşük (1-3)"), (4, 6, "Orta (4-6)"), (7, 10, "Yüksek (7-10)")]
    occ_bands = [(1, 3, "Düşük (1-3)"), (4, 6, "Orta (4-6)"), (7, 10, "Yüksek (7-10)")]

    z, text = [], []
    for s_low, s_high, _ in sev_bands:
        row_z, row_text = [], []
        for o_low, o_high, _ in occ_bands:
            matches = [r for r in fmea_rows if s_low <= r["severity"] <= s_high and o_low <= r["occurrence"] <= o_high]
            avg_rpn = round(sum(r["rpn"] for r in matches) / len(matches)) if matches else 0
            row_z.append(avg_rpn)
            row_text.append(f"<b>{avg_rpn}</b><br>n={len(matches)}")
        z.append(row_z)
        text.append(row_text)

    fig = go.Figure(go.Heatmap(
        z=z,
        x=[b[2] for b in occ_bands],
        y=[b[2] for b in sev_bands],
        text=text, texttemplate="%{text}",
        colorscale=[[0, "#ecfdf5"], [0.2, "#fef3c7"], [0.5, "#fff7ed"], [1, "#fee2e2"]],
        showscale=False
    ))

    _apply_defaults(fig, "Risk Öncelik Matrisi (Şiddet × Oluşma)", height=360)
    fig.update_xaxes(title_text="Oluşma Olasılığı")
    fig.update_yaxes(title_text="Hata Şiddeti")
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# OEE GAUGE
# ─────────────────────────────────────────────────────────────────────────────

def oee_gauge(oee_value: float, target: float = 85.0) -> go.Figure:
    """Modern OEE Gauge indicator."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=oee_value,
        number={"suffix": "%", "font": {"size": 40, "weight": 800, "color": PALETTE["text"]}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#94a3b8"},
            "bar": {"color": PALETTE["primary"], "thickness": 0.3},
            "bgcolor": "#f1f5f9",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 65], "color": "rgba(239, 68, 68, 0.1)"},
                {"range": [65, 85], "color": "rgba(245, 158, 11, 0.1)"},
                {"range": [85, 100], "color": "rgba(16, 185, 129, 0.1)"},
            ],
            "threshold": {"line": {"color": PALETTE["danger"], "width": 3}, "thickness": 0.8, "value": target}
        }
    ))
    fig.update_layout(
        height=240, margin=dict(l=30, r=30, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig
