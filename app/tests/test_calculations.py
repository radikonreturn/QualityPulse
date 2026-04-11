import pytest
from datetime import datetime, timedelta
from app.utils.calculations import (
    calculate_oee,
    calculate_scrap_rate,
    monthly_scrap_delta,
    get_30_day_trend,
    count_overdue_capa,
    calculate_cpk_from_rows
)

def test_calculate_oee():
    # 0.9 * 0.9 * 0.9 = 0.729 -> 72.9%
    assert calculate_oee(0.9, 0.9, 0.9) == 72.9
    assert calculate_oee(1.0, 1.0, 1.0) == 100.0
    assert calculate_oee(0.5, 0.5, 0.5) == 12.5

def test_calculate_scrap_rate():
    defects = [
        {"quantity": 5, "total_produced": 100},
        {"quantity": 10, "total_produced": 200}
    ]
    # Total def: 15, Total prod: 300 -> 15/300 = 5.0%
    assert calculate_scrap_rate(defects) == 5.0

def test_calculate_scrap_rate_empty():
    assert calculate_scrap_rate([]) == 0.0

def test_calculate_scrap_rate_zero_production():
    defects = [{"quantity": 5, "total_produced": 0}]
    assert calculate_scrap_rate(defects) == 0.0

def test_monthly_scrap_delta():
    today = datetime.today()
    this_month_date = today.strftime("%Y-%m-%d")
    prev_month_date = (today.replace(day=1) - timedelta(days=5)).strftime("%Y-%m-%d")
    
    defects = [
        {"date": this_month_date, "quantity": 10, "total_produced": 100}, # 10%
        {"date": prev_month_date, "quantity": 5, "total_produced": 100}   # 5%
    ]
    # delta = 10% - 5% = 5.0%
    assert monthly_scrap_delta(defects) == 5.0

def test_get_30_day_trend():
    today_str = datetime.today().strftime("%Y-%m-%d")
    defects = [{"date": today_str, "quantity": 10, "total_produced": 100}]
    trend = get_30_day_trend(defects)
    assert len(trend) == 30
    assert trend[-1]["date"] == today_str
    assert trend[-1]["scrap_rate"] == 10.0

def test_count_overdue_capa():
    past_date = (datetime.today() - timedelta(days=5)).strftime("%Y-%m-%d")
    future_date = (datetime.today() + timedelta(days=5)).strftime("%Y-%m-%d")
    capa_list = [
        {"due_date": past_date, "status": "Open"}, # Overdue
        {"due_date": past_date, "status": "In Progress"}, # Overdue
        {"due_date": past_date, "status": "Closed"}, # Not overdue (closed)
        {"due_date": future_date, "status": "Open"} # Not overdue (future)
    ]
    assert count_overdue_capa(capa_list) == 2

def test_calculate_cpk_from_rows():
    rows = [
        {"value": 10.0, "tolerance_upper": 12.0, "tolerance_lower": 8.0, "nominal": 10.0},
        {"value": 10.5, "tolerance_upper": 12.0, "tolerance_lower": 8.0, "nominal": 10.0},
        {"value": 11.0, "tolerance_upper": 12.0, "tolerance_lower": 8.0, "nominal": 10.0},
        {"value": 9.5, "tolerance_upper": 12.0, "tolerance_lower": 8.0, "nominal": 10.0},
        {"value": 10.0, "tolerance_upper": 12.0, "tolerance_lower": 8.0, "nominal": 10.0}
    ]
    result = calculate_cpk_from_rows(rows)
    assert result["cpk"] > 0
    # For this sample, Cpk is around 1.052, so color should be amber (>=1.0)
    assert result["color"] == "amber"

def test_calculate_cpk_from_rows_empty():
    assert calculate_cpk_from_rows([])["cpk"] == 0.0
