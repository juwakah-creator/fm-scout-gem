# Test script for Gradio app and scouting analysis

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import run_scout_analysis, DEFAULT_CSV

def test_gradio_analysis_backend():
    print("Testing Gradio backend analysis function...")
    # Test with default sample CSV
    html_output, debug_output = run_scout_analysis(None, 0, 15.0, 10, 30)
    assert html_output is not None
    assert isinstance(html_output, str)
    assert len(html_output) > 0
    assert "table" in html_output or "Error" not in html_output
    assert debug_output is not None
    assert isinstance(debug_output, str)
    print("Gradio backend analysis test passed successfully!")

if __name__ == "__main__":
    test_gradio_analysis_backend()
    print("\nAll Gradio tests passed!")
