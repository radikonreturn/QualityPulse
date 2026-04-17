import pytest
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.insights import generate_quality_insights
from db.database import insert_defect, get_defects, init_db

def test_insights_engine_logic():
    """Test that the insights engine generates meaningful strings."""
    sample_defects = [
        {"defect_type": "Porosity", "quantity": 10, "line": "Line-1", "shift": "Shift 1", "date": "2026-04-17"},
        {"defect_type": "Porosity", "quantity": 5, "line": "Line-1", "shift": "Shift 1", "date": "2026-04-17"},
        {"defect_type": "Flash", "quantity": 2, "line": "Line-2", "shift": "Shift 2", "date": "2026-04-17"},
    ]
    
    insights = generate_quality_insights(sample_defects)
    
    assert len(insights) > 0
    assert any("Porosity" in i for i in insights)
    assert any("Line-1" in i for i in insights)
    print("\n[PASS] Insights engine generated correct context-aware summaries.")

def test_defect_photo_persistence():
    """Test that defect records can save and retrieve photo paths."""
    init_db()
    test_path = "uploads/test_photo.jpg"
    
    insert_defect(
        date="2026-04-17",
        shift="Shift 1 (08-16)",
        defect_type="Surface Defect",
        quantity=5,
        total_produced=100,
        line="Line-1",
        operator="TestBot",
        photo_path=test_path
    )
    
    defects = get_defects()
    latest = defects[0]
    
    assert latest["photo_path"] == test_path
    print(f"\n[PASS] Photo path persistence verified: {latest['photo_path']}")

if __name__ == "__main__":
    test_insights_engine_logic()
    test_defect_photo_persistence()
