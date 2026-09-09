#!/usr/bin/env python3
"""Comprehensive integration test for fullbacks module."""

import pandas as pd
import numpy as np
import app
import fullbacks

def test_fullback_with_complete_data():
    """Test fullback analysis with complete data including defensive stats."""
    print("=" * 60)
    print("TEST FULLBACK INTEGRATION WITH COMPLETE DATA")
    print("=" * 60)
    
    # Create a more complete dataset with all required columns
    data = {
        'Name': ['Test Fullback', 'Another FB'],
        'Club': ['Test Club', 'Another Club'],
        'Age': [24, 28],
        'Guide Value': ['€10M', '€5M'],
        'Appearances': [30, 25],
        'Defensive Actions per 90': [3.5, 2.8],
        'Possession Won per 90': [2.1, 1.5],
        'Blocks per 90': [1.2, 0.8],
        'Pressures Attempted per 90': [4.5, 3.2],
        'xA per 90': [0.6, 0.4],
        'Key Passes per 90': [2.5, 1.8],
        'Progressive Passes per 90': [3.0, 2.2],
        'Progressive Pass %': [45.0, 38.0],
        'Open Play Cross Completion %': [30.0, 25.0],
        'Clear Cut Chances Created': [1.5, 1.0],
        'Crosses Completed': [2.0, 1.5],
        'Dribbles per 90': [1.8, 1.2],
        'Goal Contributions per 90': [0.8, 0.5],
        'xG per 90': [0.3, 0.2],
        'xG Overperformance': [0.1, 0.0],
        'Header Win %': [55.0, 48.0],
        'Mistakes Leading to Goals': [0.2, 0.5]
    }
    
    df = pd.DataFrame(data)
    
    # Test calculate_fullback_score
    for _, row in df.iterrows():
        score = fullbacks.calculate_fullback_score(row)
        print(f'{row["Name"]}: Fullback Score = {score:.4f}')
    
    # Test the full pipeline
    df['Fullback Score'] = df.apply(fullbacks.calculate_fullback_score, axis=1)
    df['Normalized Fullback Score'] = fullbacks.min_max_normalize(df['Fullback Score'])
    df['Value Index'] = df.apply(lambda row: fullbacks.calculate_value_index(row, price_threshold=int(1e18)), axis=1)
    df['Value Index'] = fullbacks.scale_value_index_to_100(df['Value Index'])
    
    print(f'\nTop player by Value Index:')
    top_player = df.sort_values('Value Index', ascending=False).iloc[0]
    print(f'{top_player["Name"]}: VI={top_player["Value Index"]:.4f}, FS={top_player["Fullback Score"]:.4f}')
    
    # Test dimension scores
    dim_scores = fullbacks.compute_dimension_scores(df)
    print(f'\nDimension scores: {list(dim_scores.columns)}')
    
    print('\nAll integration tests passed!')

def test_app_fullback_mode():
    """Test app.py with fullback mode."""
    print("\n" + "=" * 60)
    print("TEST APP FULLBACK MODE")
    print("=" * 60)
    
    # Create complete dataset
    data = {
        'Name': ['Test Fullback', 'Another FB'],
        'Club': ['Test Club', 'Another Club'],
        'Age': [24, 28],
        'Guide Value': ['€10M', '€5M'],
        'Appearances': [30, 25],
        'Defensive Actions per 90': [3.5, 2.8],
        'Possession Won per 90': [2.1, 1.5],
        'Blocks per 90': [1.2, 0.8],
        'Pressures Attempted per 90': [4.5, 3.2],
        'xA per 90': [0.6, 0.4],
        'Key Passes per 90': [2.5, 1.8],
        'Progressive Passes per 90': [3.0, 2.2],
        'Progressive Pass %': [45.0, 38.0],
        'Open Play Cross Completion %': [30.0, 25.0],
        'Clear Cut Chances Created': [1.5, 1.0],
        'Crosses Completed': [2.0, 1.5],
        'Dribbles per 90': [1.8, 1.2],
        'Goal Contributions per 90': [0.8, 0.5],
        'xG per 90': [0.3, 0.2],
        'xG Overperformance': [0.1, 0.0],
        'Header Win %': [55.0, 48.0],
        'Mistakes Leading to Goals': [0.2, 0.5]
    }
    
    df = pd.DataFrame(data)
    
    # Test process_analysis with fullbacks mode
    result_html, debug_html = app.process_analysis(df, 'fullbacks', 0, 50, 10, 30, 17)
    print('Fullback mode analysis OK')
    print(f'Result HTML length: {len(result_html)} chars')
    print(f'Debug HTML length: {len(debug_html)} chars')
    
    # Verify the HTML contains expected elements
    assert 'Fullback Score' in result_html, "Fullback Score not found in HTML"
    assert 'Value Index' in result_html, "Value Index not found in HTML"
    print('HTML validation passed!')

if __name__ == '__main__':
    test_fullback_with_complete_data()
    test_app_fullback_mode()
    print("\n" + "=" * 60)
    print("ALL INTEGRATION TESTS PASSED!")
    print("=" * 60)
