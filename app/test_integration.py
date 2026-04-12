import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.database import get_defects, get_measurements, get_all_capa, get_all_fmea, get_measurement_points
from utils.spc_engine import calculate_control_limits, calculate_cpk
from utils.calculations import calculate_oee, calculate_scrap_rate, get_30_day_trend
from components.charts import scrap_trend_chart, defect_donut_chart, pareto_chart, fmea_heatmap, oee_gauge

def test_integration():
    defects = get_defects()
    print(f"Defects: {len(defects)} records")
    assert defects is not None

    measurements = get_measurements()
    print(f"Measurements: {len(measurements)} records")
    assert measurements is not None

    capa = get_all_capa()
    print(f"CAPA: {len(capa)} records")
    assert capa is not None

    fmea = get_all_fmea()
    print(f"FMEA: {len(fmea)} records")
    assert fmea is not None

    points = get_measurement_points()
    print(f"Measurement points: {points}")
    assert points is not None

    vals = [m["value"] for m in measurements[:25]]
    if len(vals) >= 2:
        cl = calculate_control_limits(vals)
        print(f"Control limits: mean={cl['mean']:.4f}, UCL={cl['ucl']:.4f}, LCL={cl['lcl']:.4f}")
        assert "mean" in cl

    oee = calculate_oee(0.92, 0.89, 0.97)
    print(f"OEE: {oee}%")
    assert oee > 0

    if len(vals) >= 2:
        cpk = calculate_cpk(vals, max(vals) + 0.05, min(vals) - 0.05)
        print(f"Cpk: {cpk['cpk']}")
        assert "cpk" in cpk

    trend = get_30_day_trend(defects)
    fig1 = scrap_trend_chart(trend)
    fig2 = defect_donut_chart(defects[:50])
    fig3 = pareto_chart(defects)
    fig4 = fmea_heatmap(fmea)
    fig5 = oee_gauge(oee)
    print("All charts: OK")
    assert fig1 is not None

    scrap = calculate_scrap_rate(defects)
    print(f"Scrap rate: {scrap}%")
    assert scrap >= 0

    print("ALL CHECKS PASSED")

