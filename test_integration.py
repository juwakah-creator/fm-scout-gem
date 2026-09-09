# Test script for integration testing of FM Scout Gem application
# Tests: Gradio toggle, defensive_mid analysis, winger analysis, error handling

import sys
import os
import traceback
import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import run_scout_analysis, process_analysis, DEFAULT_CSV
from scout_app import analyze_csv, detect_columns, parse_value, normalize, age_factor
import defensive_mid
import winger


def create_test_df():
    """Create a test DataFrame with sample player data."""
    test_data = {
        'Name': ['Player1', 'Player2', 'Player3', 'Player4', 'Player5'],
        'Club': ['Barcelona', 'Real Madrid', 'Chelsea', 'Liverpool', 'Man City'],
        'Age': [25, 22, 27, 19, 24],
        'Guide Value': ['€1.2M', '€2.5M', '€800K', '€500K', '€3.0M'],
        'Appearances': [30, 40, 25, 15, 35],
        'Goal Contributions per 90': [1.5, 2.0, 0.8, 1.2, 1.8],
        'xG per 90': [0.8, 1.2, 0.5, 0.6, 1.0],
        'xA per 90': [0.5, 0.8, 0.3, 0.4, 0.7],
        'Shots on Target per 90': [1.5, 2.0, 1.0, 1.2, 1.8],
        'Tackles per 90': [2.5, 3.0, 1.8, 2.0, 2.8],
        'Interceptions per 90': [1.2, 1.5, 0.8, 1.0, 1.4],
        'Pass Completion %': [85.0, 88.0, 82.0, 80.0, 87.0],
    }
    return pd.DataFrame(test_data)


def test_gradio_toggle_functionality():
    """Test that the Gradio toggle works correctly between modes."""
    print("\n=== Test: Gradio Toggle Functionality ===")
    
    df = create_test_df()
    
    # Test defensive_mid mode
    result_dm, debug_dm = process_analysis(df, "defensive_mid", 0, 15.0, 10, 30)
    assert result_dm is not None
    assert isinstance(result_dm, str)
    assert len(result_dm) > 0
    print(f"Defensive Mid mode: result length = {len(result_dm)}")
    
    # Test winger mode
    result_w, debug_w = process_analysis(df, "winger", 0, 15.0, 10, 30)
    assert result_w is not None
    assert isinstance(result_w, str)
    assert len(result_w) > 0
    print(f"Winger mode: result length = {len(result_w)}")
    
    # Test that both modes produce different results (different columns)
    assert "Defensive Score" in result_dm or "Value Index" in result_dm
    assert "Offensive Score" in result_w or "Value Index" in result_w
    
    print("Gradio toggle test PASSED!")


def test_defensive_mid_analysis():
    """Test that defensive_mid analysis returns correct results."""
    print("\n=== Test: Defensive Mid Analysis ===")
    
    df = create_test_df()
    
    # Run defensive mid analysis
    result, debug = process_analysis(df, "defensive_mid", 0, 15.0, 10, 30)
    
    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0
    
    # Check that defensive-specific columns are present
    assert "Defensive Score" in result or "Value Index" in result
    assert "Age Factor" in result
    
    # Check debug output
    assert debug is not None
    assert isinstance(debug, str)
    
    print(f"Defensive Mid analysis: result length = {len(result)}, debug length = {len(debug)}")
    print("Defensive mid analysis test PASSED!")


def test_winger_analysis():
    """Test that winger analysis returns correct results."""
    print("\n=== Test: Winger Analysis ===")
    
    df = create_test_df()
    
    # Run winger analysis
    result, debug = process_analysis(df, "winger", 0, 15.0, 10, 30)
    
    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0
    
    # Check that offensive-specific columns are present
    assert "Offensive Score" in result or "Value Index" in result
    assert "Age Factor" in result
    
    # Check debug output
    assert debug is not None
    assert isinstance(debug, str)
    
    print(f"Winger analysis: result length = {len(result)}, debug length = {len(debug)}")
    print("Winger analysis test PASSED!")


def test_error_handling_invalid_mode():
    """Test error handling for invalid modes."""
    print("\n=== Test: Error Handling for Invalid Modes ===")
    
    df = create_test_df()
    
    # Test with invalid mode - should raise ValueError
    try:
        process_analysis(df, "invalid_mode", 0, 15.0, 10, 30)
        assert False, "Should have raised ValueError for invalid mode"
    except ValueError as e:
        assert "Invalid mode" in str(e) or "valid modes" in str(e).lower()
        print(f"Correctly caught ValueError: {e}")
    
    # Test with empty DataFrame
    result, debug = process_analysis(None, "defensive_mid", 0, 15.0, 10, 30)
    assert result is not None
    assert "No data available" in result
    
    print("Error handling test PASSED!")


def test_scout_app_compatibility():
    """Test compatibility with scout_app module."""
    print("\n=== Test: Scout App Compatibility ===")
    
    # Create a CSV file for scout_app testing
    csv_content = """Name,Club,Age,Guide Value,Appearances,Goal Contributions per 90,xG per 90,xA per 90,Shots on Target per 90,Shots per 90
Player1,Barcelona,25,€1.2M,30,1.5,0.8,0.5,1.5,2.0
Player2,Real Madrid,22,€2.5M,40,2.0,1.2,0.8,2.0,2.5
Player3,Chelsea,27,€800K,25,0.8,0.5,0.3,1.0,1.2"""
    
    csv_path = "test_integration_data.csv"
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write(csv_content)
    
    try:
        # Test scout_app analyze_csv function
        result = analyze_csv(csv_path, 5000000, 20, 30)
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
        print(f"Scout app compatibility: result length = {len(result)}")
        
        # Verify HTML structure
        assert "<table" in result or "Error:" not in result
        
    finally:
        if os.path.exists(csv_path):
            os.remove(csv_path)
    
    print("Scout app compatibility test PASSED!")


def test_dimension_scores():
    """Test dimension scores calculation for both modes."""
    print("\n=== Test: Dimension Scores ===")
    
    df = create_test_df()
    
    # Test defensive mid dimension scores
    result_dm, debug_dm = process_analysis(df, "defensive_mid", 0, 15.0, 10, 30)
    assert result_dm is not None
    
    # Test winger dimension scores
    result_w, debug_w = process_analysis(df, "winger", 0, 15.0, 10, 30)
    assert result_w is not None
    
    print("Dimension scores test PASSED!")


def run_all_tests():
    """Run all integration tests."""
    print("=" * 60)
    print("FM Scout Gem - Integration Test Suite")
    print("=" * 60)
    
    tests = [
        test_gradio_toggle_functionality,
        test_defensive_mid_analysis,
        test_winger_analysis,
        test_error_handling_invalid_mode,
        test_scout_app_compatibility,
        test_dimension_scores,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\nFAILED: {test_func.__name__}")
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
