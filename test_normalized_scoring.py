#!/usr/bin/env python3
"""
Test script to verify the new normalized scoring system works correctly.
"""

import pandas as pd
import numpy as np
import sys
sys.path.insert(0, '/home/jperrotta/coding/fm-scout-gem')

from scoring_system import (
    percentile_normalize,
    calculate_cof_score_normalized,
    calculate_striker_score_normalized,
    calculate_winger_score_normalized,
    calculate_defensive_mid_score_normalized,
    calculate_defender_score_normalized,
    calculate_fullback_score_normalized,
    calculate_goalkeeper_score_normalized,
    calculate_value_index_normalized,
    calculate_age_factor
)

def create_sample_data(n=50):
    """Create synthetic player data for testing."""
    np.random.seed(42)
    
    df = pd.DataFrame({
        'Name': [f'Player_{i}' for i in range(n)],
        'Club': ['Club_' + str(i % 10) for i in range(n)],
        'Age': np.random.randint(18, 32, n),
        'Guide Value': [f'€{np.random.uniform(0.5, 50, 1)[0]:.1f}M' for _ in range(n)],
        'xA per 90': np.random.uniform(0, 0.5, n),
        'Key Passes per 90': np.random.uniform(1, 6, n),
        'Goal Contributions per 90': np.random.uniform(0.2, 2.0, n),
        'Passaggi progressivi per 90': np.random.uniform(5, 25, n),
        'xG per 90': np.random.uniform(0.1, 1.5, n),
        'NP-xG per 90': np.random.uniform(0.1, 1.2, n),
        'Shots on Target per 90': np.random.uniform(0.5, 4, n),
        'Dribbling completati per 90': np.random.uniform(0.5, 3, n),
        'Pressures Attempted per 90': np.random.uniform(10, 40, n),
        'Possession Won per 90': np.random.uniform(2, 15, n),
        'Tackles per 90': np.random.uniform(1, 5, n),
        'Interceptions per 90': np.random.uniform(0.5, 3, n),
        'Pass Completion %': np.random.uniform(70, 95, n),
        'Progressive Passes per 90': np.random.uniform(3, 15, n),
        'Headers Won %': np.random.uniform(50, 80, n),
        'Saves per 90': np.random.uniform(2, 8, n),
        'Save Percentage %': np.random.uniform(60, 85, n),
        'Clean Sheets %': np.random.uniform(30, 70, n),
        'Goals Conceded per 90': np.random.uniform(0.5, 2.5, n),
        'Appearances': np.random.randint(5, 40, n)
    })
    
    # Parse price
    df['_price'] = df['Guide Value'].apply(lambda x: float(str(x).replace('€', '').replace('M', '')) * 1_000_000)
    df['_age'] = df['Age']
    
    return df

def test_normalization():
    """Test that percentile normalization works correctly."""
    print("=" * 60)
    print("TEST 1: Percentile Normalization")
    print("=" * 60)
    
    test_values = pd.Series([1, 2, 3, 4, 5])
    normalized = percentile_normalize(test_values, scale=100)
    
    print(f"Original: {list(test_values)}")
    print(f"Normalized: {list(normalized.round(2))}")
    print(f"Expected: [0, 25, 50, 75, 100] (percentile ranks)")
    assert abs(normalized[0] - 0) < 5, "First value should be ~0"
    assert abs(normalized[2] - 50) < 5, "Middle value should be ~50"
    assert abs(normalized[4] - 100) < 5, "Last value should be ~100"
    print("✓ PASSED\n")

def test_cof_scoring():
    """Test COF scoring with normalized stats."""
    print("=" * 60)
    print("TEST 2: COF Score Calculation")
    print("=" * 60)
    
    df = create_sample_data(30)
    
    # Calculate normalized COF score
    df['_cof_score'] = calculate_cof_score_normalized(df)
    
    print(f"COF Score range: {df['_cof_score'].min():.2f} - {df['_cof_score'].max():.2f}")
    print(f"Average COF Score: {df['_cof_score'].mean():.2f}")
    print(f"Score std deviation: {df['_cof_score'].std():.2f}")
    
    # Verify scores are in reasonable range
    assert df['_cof_score'].min() >= 0, "Scores should be >= 0"
    assert df['_cof_score'].max() <= 100, "Scores should be <= 100"
    assert not df['_cof_score'].isna().any(), "No NaN values expected"
    print("✓ PASSED\n")

def test_age_factor():
    """Test age factor calculation."""
    print("=" * 60)
    print("TEST 3: Age Factor")
    print("=" * 60)
    
    ages = [19, 21, 25, 28, 31]
    expected = [2.0, 1.6, 1.3, 1.0, 1.0]
    
    for age, exp in zip(ages, expected):
        result = calculate_age_factor(age)
        print(f"Age {age}: Factor = {result} (expected {exp})")
        assert abs(result - exp) < 0.01, f"Age {age} factor incorrect"
    
    print("✓ PASSED\n")

def test_value_index():
    """Test Value Index calculation."""
    print("=" * 60)
    print("TEST 4: Value Index (Normalized)")
    print("=" * 60)
    
    df = create_sample_data(50)
    df['_cof_score'] = calculate_cof_score_normalized(df)
    df['_value_index'] = calculate_value_index_normalized(df, '_cof_score')
    
    print(f"Value Index range: {df['_value_index'].min():.2f} - {df['_value_index'].max():.2f}")
    print(f"Top 3 players:")
    print(df.nlargest(3, '_value_index')[['Name', '_cof_score', '_value_index', '_price']])
    
    # Verify normalization to 0-100
    assert df['_value_index'].min() >= 0, "VI should be >= 0"
    assert df['_value_index'].max() <= 100, "VI should be <= 100"
    print("✓ PASSED\n")

def test_all_roles():
    """Test all role-specific scores."""
    print("=" * 60)
    print("TEST 5: All Role Scoring Functions")
    print("=" * 60)
    
    df = create_sample_data(50)
    
    # Test each role
    roles = {
        'COF': calculate_cof_score_normalized,
        'Striker': calculate_striker_score_normalized,
        'Winger': calculate_winger_score_normalized,
        'Defensive Mid': calculate_defensive_mid_score_normalized,
        'Defender': calculate_defender_score_normalized,
        'Fullback': calculate_fullback_score_normalized,
        'Goalkeeper': calculate_goalkeeper_score_normalized
    }
    
    for role_name, scorer in roles.items():
        df[f'_{role_name.lower()}_score'] = scorer(df)
        print(f"{role_name}: Range {df[f'_{role_name.lower()}_score'].min():.2f} - {df[f'_{role_name.lower()}_score'].max():.2f}")
        assert not df[f'_{role_name.lower()}_score'].isna().any(), f"{role_name} has NaN values"
    
    print("✓ All roles tested successfully\n")

def compare_old_new():
    """Compare old vs new scoring."""
    print("=" * 60)
    print("TEST 6: Old vs New Scoring Comparison")
    print("=" * 60)
    
    # Create sample data
    df = create_sample_data(100)
    
    # Old scoring (arbitrary weights)
    df['_old_cof'] = (
        df['xA per 90'].fillna(0) * 2.0 +
        df['Key Passes per 90'].fillna(0) * 1.8 +
        df['Goal Contributions per 90'].fillna(0) * 2.0 +
        df['xG per 90'].fillna(0) * 1.8 +
        df['NP-xG per 90'].fillna(0) * 1.2
    )
    
    # New scoring (normalized)
    df['_new_cof'] = calculate_cof_score_normalized(df)
    
    print("Old scoring (raw weighted):")
    print(f"  Range: {df['_old_cof'].min():.2f} - {df['_old_cof'].max():.2f}")
    print(f"  Mean: {df['_old_cof'].mean():.2f}")
    print(f"  Std: {df['_old_cof'].std():.2f}")
    
    print("\nNew scoring (normalized):")
    print(f"  Range: {df['_new_cof'].min():.2f} - {df['_new_cof'].max():.2f}")
    print(f"  Mean: {df['_new_cof'].mean():.2f}")
    print(f"  Std: {df['_new_cof'].std():.2f}")
    
    print("\nKey difference:")
    print("- Old: Pass Completion % (70-95) dominates over xA (0-0.5)")
    print("- New: Percentile ranking ensures all stats contribute equitably")
    print("✓ COMPARISON COMPLETE\n")

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("FM SCOUT GEM - NORMALIZED SCORING SYSTEM TESTS")
    print("=" * 60 + "\n")
    
    test_normalization()
    test_cof_scoring()
    test_age_factor()
    test_value_index()
    test_all_roles()
    compare_old_new()
    
    print("=" * 60)
    print("ALL TESTS PASSED ✓")
    print("=" * 60)
