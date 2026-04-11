"""
QualityPulse — Calculations
OEE, scrap rate, monthly deltas, and other KPI helpers.
"""

import statistics
from datetime import datetime, timedelta
from typing import List


def calculate_oee(availability: float, performance: float, quality: float) -> float:
    """
    Calculate Overall Equipment Effectiveness.
    OEE = Availability × Performance × Quality
    Returns percentage (0–100).
    """
    return round(availability * performance * quality * 100, 1)


def calculate_scrap_rate(defects: list[dict]) -> float:
    """
    Calculate scrap rate from defect records.
    scrap_rate = total_defects / total_produced × 100
    """
    total_defects = sum(d["quantity"] for d in defects)
    total_produced = sum(d["total_produced"] for d in defects)
    if total_produced == 0:
        return 0.0
    return round(total_defects / total_produced * 100, 2)


def monthly_scrap_delta(defects: list[dict]) -> float:
    """
    Returns the difference in scrap rate between the current and previous month.
    Positive = getting worse, Negative = improving.
    """
    today = datetime.today()
    first_this = today.replace(day=1)
    first_prev = (first_this - timedelta(days=1)).replace(day=1)

    this_month = [d for d in defects if d["date"] >= first_this.strftime("%Y-%m-%d")]
    prev_month = [d for d in defects if
                  first_prev.strftime("%Y-%m-%d") <= d["date"] < first_this.strftime("%Y-%m-%d")]

    rate_this = calculate_scrap_rate(this_month)
    rate_prev = calculate_scrap_rate(prev_month)
    return round(rate_this - rate_prev, 2)


def calculate_cpk_from_rows(rows: list[dict]) -> dict:
    """
    Calculate Cpk from a list of measurement rows (dicts with keys: value, tolerance_upper, tolerance_lower, nominal).
    Uses the first row's USL/LSL as the spec limits.
    """
    if not rows:
        return {"cp": 0.0, "cpk": 0.0, "mean": 0.0, "sigma": 0.0, "color": "red"}

    values = [r["value"] for r in rows]
    usl = rows[0]["tolerance_upper"]
    lsl = rows[0]["tolerance_lower"]

    from utils.spc_engine import calculate_cpk
    result = calculate_cpk(values, usl, lsl)

    cpk = result["cpk"]
    if cpk >= 1.33:
        color = "green"
    elif cpk >= 1.00:
        color = "amber"
    else:
        color = "red"

    result["color"] = color
    return result


def get_30_day_trend(defects: list[dict]) -> list[dict]:
    """
    Build daily scrap rate for the last 30 days.
    Returns list of {date, scrap_rate}.
    """
    today = datetime.today()
    result = []
    for i in range(29, -1, -1):
        day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        day_records = [d for d in defects if d["date"] == day]
        result.append({
            "date": day,
            "scrap_rate": calculate_scrap_rate(day_records) if day_records else 0.0
        })
    return result


def count_overdue_capa(capa_list: list[dict]) -> int:
    """Count CAPA records that are past due and not closed."""
    today = datetime.today().strftime("%Y-%m-%d")
    return sum(
        1 for c in capa_list
        if c["due_date"] < today and c["status"] != "Closed"
    )
