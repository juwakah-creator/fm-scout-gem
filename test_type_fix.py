# Test script to verify the TypeError fix for string vs int comparisons
import sys
import os
import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import process_analysis
from scout_app import detect_columns, parse_value

def test_string_stats_column():
    """Test that the fix handles string columns correctly."""
    print("\n=== Test: String Stats Column Handling ===")
    
    # Create a DataFrame with string values in statistical columns
    test_data = {
        'Name': ['Player1', 'Player2'],
        'Club': ['Barcelona', 'Real Madrid'],
        'Age': [25, 22],
        'Guide Value': ['€1.2M', '€2.5M'],
        'Appearances': [30, 40],
        'Goal Contributions per 90': ['1.5', '2.0'],  # String values!
        'xG per 90': ['0.8', '1.2'],  # String values!
        'xA per 90': ['0.5', '0.8'],  # String values!
        'Shots on Target per 90': ['1.5', '2.0'],  # String values!
    }
    
    df = pd.DataFrame(test_data)
    
    # Verify that columns are strings before processing
    assert df['Goal Contributions per 90'].dtype == object, "Expected string column"
    print(f"Column dtype before processing: {df['Goal Contributions per 90'].dtype}")
    
    # Process with winger mode - this should NOT raise TypeError anymore
    try:
        result, debug = process_analysis(df, "winger", 0, 15.0, 10, 30)
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
        print(f"Winger mode with string stats: SUCCESS (result length = {len(result)})")
    except TypeError as e:
        if "'>' not supported between instances of 'str' and 'int'" in str(e):
            print(f"FAILED: TypeError still occurs - {e}")
            raise
        else:
            print(f"Different error: {e}")
            raise
    
    # Also test defensive_mid mode
    try:
        result_dm, debug_dm = process_analysis(df, "defensive_mid", 0, 15.0, 10, 30)
        assert result_dm is not None
        assert isinstance(result_dm, str)
        print(f"Defensive Mid mode with string stats: SUCCESS (result length = {len(result_dm)})")
    except TypeError as e:
        if "'>' not supported between instances of 'str' and 'int'" in str(e):
            print(f"FAILED: TypeError still occurs - {e}")
            raise
        else:
            print(f"Different error: {e}")
            raise
    
    print("String stats column handling test PASSED!")


def test_mixed_type_columns():
    """Test with mixed types (some numeric, some string)."""
    print("\n=== Test: Mixed Type Columns ===")
    
    test_data = {
        'Name': ['Player1', 'Player2'],
        'Club': ['Barcelona', 'Real Madrid'],
        'Age': [25, 22],
        'Guide Value': ['€1.2M', '€2.5M'],
        'Appearances': [30, 40],
        'Goal Contributions per 90': [1.5, '2.0'],  # Mixed types!
        'xG per 90': ['0.8', 1.2],  # Mixed types!
    }
    
    df = pd.DataFrame(test_data)
    
    try:
        result, debug = process_analysis(df, "winger", 0, 15.0, 10, 30)
        assert result is not None
        print(f"Mixed type columns: SUCCESS (result length = {len(result)})")
    except TypeError as e:
        if "'>' not supported between instances of 'str' and 'int'" in str(e):
            print(f"FAILED: TypeError still occurs - {e}")
            raise
        else:
            print(f"Different error: {e}")
            raise
    
    print("Mixed type columns test PASSED!")


def test_nan_in_string_columns():
    """Test with NaN values in string columns."""
    print("\n=== Test: NaN in String Columns ===")
    
    test_data = {
        'Name': ['Player1', 'Player2', 'Player3'],
        'Club': ['Barcelona', 'Real Madrid', 'Chelsea'],
        'Age': [25, 22, 27],
        'Guide Value': ['€1.2M', '€2.5M', '€800K'],
        'Appearances': [30, 40, 25],
        'Goal Contributions per 90': ['1.5', np.nan, '0.8'],  # NaN in string column
        'xG per 90': ['0.8', np.nan, '0.5'],  # NaN in string column
    }
    
    df = pd.DataFrame(test_data)
    
    try:
        result, debug = process_analysis(df, "winger", 0, 15.0, 10, 30)
        assert result is not None
        print(f"NaN in string columns: SUCCESS (result length = {len(result)})")
    except TypeError as e:
        if "'>' not supported between instances of 'str' and 'int'" in str(e):
            print(f"FAILED: TypeError still occurs - {e}")
            raise
        else:
            print(f"Different error: {e}")
            raise
    
    print("NaN in string columns test PASSED!")


if __name__ == "__main__":
    print("=" * 60)
    print("FM Scout Gem - TypeError Fix Verification")
    print("=" * 60)
    
    tests = [
        test_string_stats_column,
        test_mixed_type_columns,
        test_nan_in_string_columns,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"Test {test.__name__} FAILED: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed > 0:
        sys.exit(1)
