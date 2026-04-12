import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.spc_engine import (
    calculate_control_limits,
    calculate_cpk,
    nelson_rule_1,
    nelson_rule_2,
    get_ooc_indices
)

def test_calculate_control_limits():
    values = [10.0, 10.5, 11.0, 9.5, 10.0]
    result = calculate_control_limits(values)
    
    assert result["mean"] == 10.2
    # standard deviation of [10.0, 10.5, 11.0, 9.5, 10.0] is roughly 0.5701
    assert result["sigma"] > 0
    assert result["ucl"] == round(result["mean"] + 3 * result["sigma"], 4)
    assert result["lcl"] == round(result["mean"] - 3 * result["sigma"], 4)

def test_calculate_control_limits_empty():
    assert calculate_control_limits([]) == {"mean": 0.0, "ucl": 0.0, "lcl": 0.0, "sigma": 0.0}
    assert calculate_control_limits([5.0]) == {"mean": 0.0, "ucl": 0.0, "lcl": 0.0, "sigma": 0.0}

def test_calculate_cpk():
    values = [10.0, 10.5, 11.0, 9.5, 10.0]
    # usl = 12.0, lsl = 8.0, mean = 10.2
    # sigma = 0.5700877...
    # cp = (12 - 8) / (6 * sigma) = 4 / 3.42 = 1.169
    # cpu = (12 - 10.2) / (3 * sigma) = 1.8 / 1.710 = 1.052
    # cpl = (10.2 - 8) / (3 * sigma) = 2.2 / 1.710 = 1.286
    result = calculate_cpk(values, 12.0, 8.0)
    
    assert result["cp"] > 0
    assert result["cpk"] > 0
    assert result["cpk"] == min(result["cpu"], result["cpl"])

def test_calculate_cpk_bad_limits():
    """Test when USL is less than or equal to LSL."""
    result = calculate_cpk([10.0, 11.0], 8.0, 12.0) # usl < lsl
    assert result["cpk"] == 0.0

def test_calculate_cpk_perfect_uniformity():
    """Test when standard deviation is zero."""
    result = calculate_cpk([10.0, 10.0, 10.0], 12.0, 8.0)
    assert result["cp"] == float('inf')
    assert result["cpk"] == float('inf')

def test_nelson_rule_1():
    values = [10.0, 10.0, 25.0, 10.0, -5.0]
    # mean is ~ 10, ucl=20, lcl = 0
    ucl = 20.0
    lcl = 0.0
    violations = nelson_rule_1(values, ucl, lcl)
    assert violations == [2, 4] # index 2 is 25.0 (>20), index 4 is -5 (<0)

def test_nelson_rule_2():
    # 9 points above mean
    values = [11.0, 11.0, 11.0, 11.0, 11.0, 11.0, 11.0, 11.0, 11.0, 9.0]
    mean = 10.0
    violations = nelson_rule_2(values, mean)
    assert violations == [0] # Run started at index 0

def test_nelson_rule_2_no_violation():
    # 8 points above mean, then drops below
    values = [11.0, 11.0, 11.0, 11.0, 11.0, 11.0, 11.0, 11.0, 9.0, 11.0]
    mean = 10.0
    violations = nelson_rule_2(values, mean)
    assert len(violations) == 0

def test_get_ooc_indices():
    values = [11.0]*9 + [25.0] # first 9 trigger rule 2, the 10th triggers rule 1
    ucl = 20.0
    lcl = 0.0
    mean = 10.0
    indices = get_ooc_indices(values, ucl, lcl, mean)
    assert 0 in indices # rule 2 start
    assert 9 in indices # rule 1 spike
