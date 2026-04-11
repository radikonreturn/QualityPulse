import sys
sys.path.insert(0, ".")

from db.database import get_defects, get_measurements, get_all_capa, get_all_fmea, get_measurement_points
from utils.spc_engine import calculate_control_limits, calculate_cpk
from utils.calculations import calculate_oee, calculate_scrap_rate, get_30_day_trend
from components.charts import scrap_trend_chart, defect_donut_chart, pareto_chart, fmea_heatmap, oee_gauge

defects = get_defects()
print(f"Defects: {len(defects)} records")

measurements = get_measurements()
print(f"Measurements: {len(measurements)} records")

capa = get_all_capa()
print(f"CAPA: {len(capa)} records")

fmea = get_all_fmea()
print(f"FMEA: {len(fmea)} records")

points = get_measurement_points()
print(f"Measurement points: {points}")

vals = [m["value"] for m in measurements[:25]]
cl = calculate_control_limits(vals)
print(f"Control limits: mean={cl['mean']:.4f}, UCL={cl['ucl']:.4f}, LCL={cl['lcl']:.4f}")

oee = calculate_oee(0.92, 0.89, 0.97)
print(f"OEE: {oee}%")

cpk = calculate_cpk(vals, max(vals) + 0.05, min(vals) - 0.05)
print(f"Cpk: {cpk['cpk']}")

trend = get_30_day_trend(defects)
fig1 = scrap_trend_chart(trend)
fig2 = defect_donut_chart(defects[:50])
fig3 = pareto_chart(defects)
fig4 = fmea_heatmap(fmea)
fig5 = oee_gauge(oee)
print("All charts: OK")

scrap = calculate_scrap_rate(defects)
print(f"Scrap rate: {scrap}%")

print("ALL CHECKS PASSED")
