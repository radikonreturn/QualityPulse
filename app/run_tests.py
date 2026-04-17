import subprocess
import sys
import os

def run_tests():
    """Run all unit tests using pytest."""
    print("--- [QualityPulse] Running Automated Tests ---")
    app_dir = os.path.dirname(os.path.abspath(__file__))
    
    try:
        import pytest
    except ImportError:
        print("ERROR: pytest not found. Please install it with 'pip install pytest'.")
        sys.exit(1)

    # Run pytest from the app directory
    result = subprocess.call([sys.executable, "-m", "pytest", "tests/"], cwd=app_dir)
    
    if result == 0:
        print("\nSUCCESS: All tests passed!")
    else:
        print("\nFAILURE: Some tests failed. Please review the output above.")
    
    sys.exit(result)

if __name__ == "__main__":
    run_tests()
