"""
QualityPulse — SPC Engine
Statistical Process Control calculations and Nelson Rule detection.
"""

import statistics
from typing import List


def calculate_control_limits(values: List[float]) -> dict:
    """
    Calculate control limits from a list of measurement values.
    Returns: {mean, ucl, lcl, sigma}
    UCL = mean + 3σ, LCL = mean - 3σ
    """
    if not values or len(values) < 2:
        return {"mean": 0.0, "ucl": 0.0, "lcl": 0.0, "sigma": 0.0}

    mean = statistics.mean(values)
    sigma = statistics.stdev(values)

    return {
        "mean": round(mean, 4),
        "ucl": round(mean + 3 * sigma, 4),
        "lcl": round(mean - 3 * sigma, 4),
        "sigma": round(sigma, 4),
    }


def nelson_rule_1(values: List[float], ucl: float, lcl: float) -> List[int]:
    """
    Nelson Rule 1: Any single point beyond UCL or LCL (3σ).
    Returns list of indices where rule is violated.
    """
    return [i for i, v in enumerate(values) if v > ucl or v < lcl]


def nelson_rule_2(values: List[float], mean: float) -> List[int]:
    """
    Nelson Rule 2: 9 or more consecutive points on the same side of the center line.
    Returns the starting index of each such run.
    """
    if len(values) < 9:
        return []

    violations = []
    run_length = 1
    run_side = 1 if values[0] >= mean else -1
    run_start = 0

    for i in range(1, len(values)):
        side = 1 if values[i] >= mean else -1
        if side == run_side:
            run_length += 1
            if run_length == 9:
                violations.append(run_start)
        else:
            run_side = side
            run_start = i
            run_length = 1

    return violations


def calculate_cpk(values: List[float], usl: float, lsl: float) -> dict:
    """
    Calculate process capability indices.
    Returns: {cp, cpk, cpu, cpl, mean, sigma}
    """
    if not values or len(values) < 2 or usl <= lsl:
        return {"cp": 0.0, "cpk": 0.0, "cpu": 0.0, "cpl": 0.0, "mean": 0.0, "sigma": 0.0}

    mean = statistics.mean(values)
    sigma = statistics.stdev(values)

    if sigma == 0:
        return {"cp": float("inf"), "cpk": float("inf"), "cpu": float("inf"),
                "cpl": float("inf"), "mean": mean, "sigma": 0.0}

    cp = (usl - lsl) / (6 * sigma)
    cpu = (usl - mean) / (3 * sigma)
    cpl = (mean - lsl) / (3 * sigma)
    cpk = min(cpu, cpl)

    return {
        "cp": round(cp, 3),
        "cpk": round(cpk, 3),
        "cpu": round(cpu, 3),
        "cpl": round(cpl, 3),
        "mean": round(mean, 4),
        "sigma": round(sigma, 4),
    }


def get_ooc_indices(values: List[float], ucl: float, lcl: float, mean: float) -> List[int]:
    """Combined out-of-control indices from Nelson Rules 1 and 2."""
    r1 = set(nelson_rule_1(values, ucl, lcl))
    r2 = set(nelson_rule_2(values, mean))
    return sorted(r1 | r2)
