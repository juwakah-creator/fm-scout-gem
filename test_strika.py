#!/usr/bin/env python3
"""Test script for strika.py integration."""

import pandas as pd
import numpy as np
import strika
import app

def test_strika_module():
    """Test the strika module functions."""
    print("=" * 60)
    print("TEST STRIKA MODULE")
    print("=" * 60)
    
    # Load sample data
    df = pd.read_csv('sample_players.csv')
    print(f'Loaded {len(df)} players')
    
    # Test calculate_striker_score on first few rows
    for i, row in df.head(3).iterrows():
        score = strika.calculate_striker_score(row)
        print(f'{row["Name"]}: Striker Score = {score:.4f}')
    
    # Test full pipeline
    df['Striker Score'] = df.apply(strika.calculate_striker_score, axis=1)
    df['Normalized Striker Score'] = strika.min_max_normalize(df['Striker Score'])
    df['Value Index'] = df.apply(lambda row: strika.calculate_value_index(row, price_threshold=int(1e18)), axis=1)
    df['Value Index'] = strika.scale_value_index_to_100(df['Value Index'])
    
    print(f'\nTop 5 by Value Index:')
    top5 = df.sort_values('Value Index', ascending=False).head(5)
    for _, row in top5.iterrows():
        print(f'{row["Name"]}: VI={row["Value Index"]:.4f}, SS={row["Striker Score"]:.4f}')
    
    # Test dimension scores
    dim_scores = strika.compute_dimension_scores(df)
    print(f'\nDimension scores columns: {list(dim_scores.columns)}')
    print('All tests passed!')

def test_app_integration():
    """Test the app.py integration with strika mode."""
    print("\n" + "=" * 60)
    print("TEST APP INTEGRATION")
    print("=" * 60)
    
    # Test process_analysis with strika mode
    df = pd.read_csv('sample_players.csv')
    result_html, debug_html = app.process_analysis(df, 'strika', 0, 50, 10, 30, 17)
    print('Strika mode analysis OK')
    print(f'Result HTML length: {len(result_html)} chars')
    print(f'Debug HTML length: {len(debug_html)} chars')
    
    # Verify the HTML contains expected elements
    assert 'Striker Score' in result_html, "Striker Score not found in HTML"
    assert 'Value Index' in result_html, "Value Index not found in HTML"
    print('HTML validation passed!')

if __name__ == '__main__':
    test_strika_module()
    test_app_integration()
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
