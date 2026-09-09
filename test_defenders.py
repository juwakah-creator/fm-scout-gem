#!/usr/bin/env python3
"""Test script for defenders.py integration."""

import pandas as pd
import numpy as np
import defenders
import app

def test_defenders_module():
    """Test the defenders module functions."""
    print("=" * 60)
    print("TEST DEFENDERS MODULE")
    print("=" * 60)
    
    # Load sample data
    df = pd.read_csv('sample_players.csv')
    print(f'Loaded {len(df)} players')
    
    # Test calculate_defender_score on first few rows
    for i, row in df.head(3).iterrows():
        score = defenders.calculate_defender_score(row)
        print(f'{row["Name"]}: Defender Score = {score:.4f}')
    
    # Test full pipeline
    df['Defender Score'] = df.apply(defenders.calculate_defender_score, axis=1)
    df['Normalized Defender Score'] = defenders.min_max_normalize(df['Defender Score'])
    df['Value Index'] = df.apply(lambda row: defenders.calculate_value_index(row, price_threshold=int(1e18)), axis=1)
    df['Value Index'] = defenders.scale_value_index_to_100(df['Value Index'])
    
    print(f'\nTop 5 by Value Index:')
    top5 = df.sort_values('Value Index', ascending=False).head(5)
    for _, row in top5.iterrows():
        print(f'{row["Name"]}: VI={row["Value Index"]:.4f}, DS={row["Defender Score"]:.4f}')
    
    # Test dimension scores
    dim_scores = defenders.compute_dimension_scores(df)
    print(f'\nDimension scores columns: {list(dim_scores.columns)}')
    print('All tests passed!')

def test_app_integration():
    """Test the app.py integration with defenders mode."""
    print("\n" + "=" * 60)
    print("TEST APP INTEGRATION")
    print("=" * 60)
    
    # Test process_analysis with defenders mode
    df = pd.read_csv('sample_players.csv')
    result_html, debug_html = app.process_analysis(df, 'defenders', 0, 50, 10, 30, 17)
    print('Defenders mode analysis OK')
    print(f'Result HTML length: {len(result_html)} chars')
    print(f'Debug HTML length: {len(debug_html)} chars')
    
    # Verify the HTML contains expected elements
    assert 'Defender Score' in result_html, "Defender Score not found in HTML"
    assert 'Value Index' in result_html, "Value Index not found in HTML"
    print('HTML validation passed!')

if __name__ == '__main__':
    test_defenders_module()
    test_app_integration()
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
