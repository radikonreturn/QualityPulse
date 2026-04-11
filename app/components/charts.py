"""
QualityPulse — Chart Builders
All Plotly chart factory functions used across pages.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List, Optional

# ── Shared theme ──────────────────────────────────────────────────────────────
PALETTE = {
    "primary":  "#4f8ef7",
    "success":  "#2ecc71",
    "warning":  "#f39c12",
    "danger":   "#e74c3c",
    "bg":       "#ffffff",
    "grid":     "#f0f2f5",
    "text":     "#1a1a2e",
    "muted":    "#6b7280",
}

_LAYOUT_DEFAULTS = dict(
    paper_bgcolor=PALETTE["bg"],
    plot_bgcolor=PALETTE["bg"],
    font=dict(family="Inter, sans-serif", color=PALETTE["text"], size=12),
    margin=dict(l=50, r=30, t=40, b=40),
    legend=dict(
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="#e8ecf0",
        borderwidth=1,
        font=dict(size=11),
    ),
    hoverlabel=dict(
        bgcolor="white",
        bordercolor="#e8ecf0",
        font=dict(family="Inter, sans-serif", size=12),
    ),
)


def _apply_defaults(fig: go.Figure, title: str = "", height: int = 360) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(size=13, weight=700), x=0, xanchor="left"),
        height=height,
        **_LAYOUT_DEFAULTS,
    )
    fig.update_xaxes(showgrid=False, zeroline=False, color=PALETTE["muted"])
    fig.update_yaxes(showgrid=True, gridcolor=PALETTE["grid"], zeroline=False, color=PALETTE["muted"])
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD CHARTS
# ─────────────────────────────────────────────────────────────────────────────

def scrap_trend_chart(trend_data: list[dict], threshold: float = 3.0) -> go.Figure:
    """30-day scrap rate trend — area line chart with threshold annotation."""
    df = pd.DataFrame(trend_data)
    fig = go.Figure()

    # Area fill
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["scrap_rate"],
        mode="lines+markers",
        name="Hurda Oranı",
        line=dict(color=PALETTE["primary"], width=2.5, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(79,142,247,0.10)",
        marker=dict(size=5, color=PALETTE["primary"]),
        hovertemplate="<b>%{x}</b><br>Hurda: %{y:.2f}%<extra></extra>",
    ))

    # Threshold line
    fig.add_hline(
        y=threshold, line_dash="dash", line_color=PALETTE["danger"],
        line_width=1.5,
        annotation_text=f"Hedef: {threshold}%",
        annotation_position="top right",
        annotation_font=dict(color=PALETTE["danger"], size=11),
    )

    _apply_defaults(fig, "30 Günlük Hurda Oranı Trendi", height=320)
    fig.update_yaxes(ticksuffix="%")
    return fig


def defect_donut_chart(defects: list[dict]) -> go.Figure:
    """Monthly defect breakdown — donut chart."""
    df = pd.DataFrame(defects)
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="Veri yok", x=0.5, y=0.5, showarrow=False)
        return _apply_defaults(fig, "Bu Ayki Hata Dağılımı", 320)

    agg = df.groupby("defect_type")["quantity"].sum().reset_index()
    colors = [PALETTE["primary"], PALETTE["success"], PALETTE["warning"],
               PALETTE["danger"], "#9b59b6", "#1abc9c", "#e67e22"]

    fig = go.Figure(go.Pie(
        labels=agg["defect_type"],
        values=agg["quantity"],
        hole=0.55,
        marker=dict(colors=colors[:len(agg)], line=dict(color="#fff", width=2)),
        textinfo="percent",
        hovertemplate="<b>%{label}</b><br>Adet: %{value}<br>Oran: %{percent}<extra></extra>",
    ))
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="v", x=1.02, y=0.5),
        annotations=[dict(text="Hatalar", x=0.5, y=0.5, font_size=13,
                           font_family="Inter", showarrow=False)],
    )
    _apply_defaults(fig, "Bu Ayki Hata Dağılımı", 320)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# PARETO CHART
# ─────────────────────────────────────────────────────────────────────────────

def pareto_chart(defects: list[dict]) -> go.Figure:
    """Pareto combo chart: bars (count) + cumulative % line."""
    df = pd.DataFrame(defects)
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="Seçilen filtreler için veri yok", x=0.5, y=0.5, showarrow=False)
        return _apply_defaults(fig, "Pareto Analizi", 420)

    agg = df.groupby("defect_type")["quantity"].sum().reset_index()
    agg = agg.sort_values("quantity", ascending=False).reset_index(drop=True)
    agg["cumulative_pct"] = agg["quantity"].cumsum() / agg["quantity"].sum() * 100

    colors = [
        PALETTE["danger"] if p <= 80 else PALETTE["muted"]
        for p in agg["cumulative_pct"]
    ]

    fig = go.Figure()

    # Bars
    fig.add_trace(go.Bar(
        x=agg["defect_type"], y=agg["quantity"],
        name="Hata Adedi",
        marker=dict(color=colors, line=dict(color="#fff", width=1)),
        yaxis="y1",
        hovertemplate="<b>%{x}</b><br>Adet: %{y}<extra></extra>",
    ))

    # Cumulative % line
    fig.add_trace(go.Scatter(
        x=agg["defect_type"], y=agg["cumulative_pct"],
        name="Kümülatif %",
        mode="lines+markers",
        line=dict(color=PALETTE["primary"], width=2.5),
        marker=dict(size=7),
        yaxis="y2",
        hovertemplate="%{y:.1f}%<extra></extra>",
    ))

    # 80% threshold
    fig.add_hline(
        y=80, yref="y2", line_dash="dash", line_color=PALETTE["danger"],
        line_width=1.5,
        annotation_text="80%",
        annotation_position="top left",
        annotation_font=dict(color=PALETTE["danger"]),
    )

    fig.update_layout(
        yaxis=dict(title="Hata Adedi", showgrid=True, gridcolor=PALETTE["grid"]),
        yaxis2=dict(title="Kümülatif %", overlaying="y", side="right",
                    range=[0, 105], ticksuffix="%", showgrid=False),
        barmode="group",
        legend=dict(orientation="h", x=0, y=1.08),
    )
    _apply_defaults(fig, "Pareto Analizi — Hata Türleri", 420)
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
    """X-bar SPC control chart with UCL/CL/LCL/USL/LSL and out-of-control highlighting."""
    fig = go.Figure()
    x = list(range(len(values)))
    x_labels = [t[:16] for t in timestamps]

    # In-control points (normal)
    in_ctrl = [i for i in x if i not in ooc_indices]
    fig.add_trace(go.Scatter(
        x=[x_labels[i] for i in in_ctrl],
        y=[values[i] for i in in_ctrl],
        mode="lines+markers",
        name="Ölçüm",
        line=dict(color=PALETTE["primary"], width=1.8),
        marker=dict(size=7, color=PALETTE["primary"]),
        hovertemplate="<b>%{x}</b><br>Değer: %{y:.4f}<extra></extra>",
    ))

    # Out-of-control points
    if ooc_indices:
        fig.add_trace(go.Scatter(
            x=[x_labels[i] for i in ooc_indices if i < len(x_labels)],
            y=[values[i] for i in ooc_indices if i < len(values)],
            mode="markers",
            name="Kontrol Dışı",
            marker=dict(size=11, color=PALETTE["danger"],
                         symbol="circle-open", line=dict(width=2.5, color=PALETTE["danger"])),
            hovertemplate="<b>%{x}</b><br>Değer: %{y:.4f} ⚠️<extra></extra>",
        ))

    # Control lines
    x_axis = x_labels
    for y_val, color, dash, name in [
        (cl,  PALETTE["success"], "dash",   f"CL = {cl:.4f}"),
        (ucl, PALETTE["danger"],  "dot",    f"UCL = {ucl:.4f}"),
        (lcl, PALETTE["danger"],  "dot",    f"LCL = {lcl:.4f}"),
    ]:
        fig.add_hline(y=y_val, line_dash=dash, line_color=color,
                       line_width=1.5,
                       annotation_text=name,
                       annotation_position="top right",
                       annotation_font=dict(color=color, size=10))

    # Spec limits (if different from control limits)
    if usl is not None:
        fig.add_hline(y=usl, line_dash="longdash", line_color=PALETTE["warning"],
                       line_width=1,
                       annotation_text=f"USL={usl}",
                       annotation_position="bottom right",
                       annotation_font=dict(color=PALETTE["warning"], size=10))
    if lsl is not None:
        fig.add_hline(y=lsl, line_dash="longdash", line_color=PALETTE["warning"],
                       line_width=1,
                       annotation_text=f"LSL={lsl}",
                       annotation_position="top right",
                       annotation_font=dict(color=PALETTE["warning"], size=10))

    _apply_defaults(fig, f"SPC — {point_name}", height=420)
    fig.update_xaxes(tickangle=-35, nticks=12, title_text="Zaman")
    fig.update_yaxes(title_text="Değer")
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# FMEA HEATMAP
# ─────────────────────────────────────────────────────────────────────────────

def fmea_heatmap(fmea_rows: list[dict]) -> go.Figure:
    """3×3 Severity vs Occurrence heatmap colored by average RPN."""
    import numpy as np

    if not fmea_rows:
        fig = go.Figure()
        fig.add_annotation(text="Veri yok", x=0.5, y=0.5, showarrow=False)
        return _apply_defaults(fig, "FMEA Risk Matrisi", 360)

    # Build 3×3 grid: severity bands 1-3, 4-6, 7-10; occurrence bands same
    sev_bands = [(1, 3, "Düşük"), (4, 6, "Orta"), (7, 10, "Yüksek")]
    occ_bands = [(1, 3, "Düşük"), (4, 6, "Orta"), (7, 10, "Yüksek")]

    z = []
    text = []
    for s_low, s_high, _ in sev_bands:
        row_z, row_text = [], []
        for o_low, o_high, _ in occ_bands:
            matches = [
                r for r in fmea_rows
                if s_low <= r["severity"] <= s_high and o_low <= r["occurrence"] <= o_high
            ]
            avg_rpn = round(sum(r["rpn"] for r in matches) / len(matches)) if matches else 0
            row_z.append(avg_rpn)
            row_text.append(f"RPN: {avg_rpn}<br>n={len(matches)}")
        z.append(row_z)
        text.append(row_text)

    y_labels = [b[2] for b in sev_bands]
    x_labels = [b[2] for b in occ_bands]

    fig = go.Figure(go.Heatmap(
        z=z,
        x=x_labels,
        y=y_labels,
        text=text,
        texttemplate="%{text}",
        hovertemplate="Şiddet: %{y}<br>Oluşma: %{x}<br>Ort. RPN: %{z}<extra></extra>",
        colorscale=[
            [0.0,  "#d1fae5"],
            [0.3,  "#fef3c7"],
            [0.65, "#fed7aa"],
            [1.0,  "#fee2e2"],
        ],
        showscale=True,
        colorbar=dict(title="Ort. RPN", tickfont=dict(size=10)),
        zmin=0, zmax=500,
    ))

    _apply_defaults(fig, "Risk Matrisi — Şiddet × Oluşma", height=340)
    fig.update_xaxes(title_text="Oluşma Seviyesi")
    fig.update_yaxes(title_text="Şiddet Seviyesi")
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# OEE GAUGE
# ─────────────────────────────────────────────────────────────────────────────

def oee_gauge(oee_value: float, target: float = 85.0) -> go.Figure:
    """Gauge chart for OEE."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=oee_value,
        delta={"reference": target, "valueformat": ".1f",
               "increasing": {"color": PALETTE["success"]},
               "decreasing": {"color": PALETTE["danger"]}},
        number={"suffix": "%", "font": {"size": 32, "family": "Inter"}},
        gauge={
            "axis": {"range": [0, 100], "ticksuffix": "%"},
            "bar": {"color": PALETTE["primary"], "thickness": 0.25},
            "bgcolor": "#f0f2f5",
            "steps": [
                {"range": [0, 65],  "color": "#fee2e2"},
                {"range": [65, 85], "color": "#fef3c7"},
                {"range": [85, 100],"color": "#d1fae5"},
            ],
            "threshold": {
                "line": {"color": PALETTE["danger"], "width": 2},
                "thickness": 0.8,
                "value": target,
            },
        },
        title={"text": "OEE", "font": {"size": 13, "family": "Inter"}},
    ))
    fig.update_layout(
        height=240,
        margin=dict(l=20, r=20, t=40, b=10),
        paper_bgcolor=PALETTE["bg"],
    )
    return fig
