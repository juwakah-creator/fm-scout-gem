#!/usr/bin/env python3
"""Test di integrazione COFF con app.py - Versione aggiornata dopo rimozione PlayerProfileGenerator"""

import pandas as pd
import numpy as np
import sys
sys.path.insert(0, '.')

from cof import calculate_cof_score, calculate_value_index, scale_value_index_to_100, compute_dimension_scores


def test_calculate_cof_score():
    """Test calcolo punteggio COF con statistiche pesate"""
    print("\n=== TEST 1: Calculate COF Score ===")
    
    row = pd.Series({
        'xA per 90': 0.3,
        'Key Passes per 90': 0.8,
        'Goal Contributions per 90': 0.4,
        'Passaggi progressivi per 90': 1.2,
        'xG per 90': 0.2,
        'NP-xG per 90': 0.1,
        'Shots on Target per 90': 0.6,
        'Dribbling completati per 90': 0.5,
        'Pressures Attempted per 90': 2.0,
        'Possession Won per 90': 1.5,
        'Header Win %': 45.0,
    })
    
    cof_score = calculate_cof_score(row)
    print(f"COF Score: {cof_score:.2f}")
    
    # Validazione
    assert cof_score > 0, "COF Score should be positive"
    print("[OK] COF Score test PASSED")


def test_calculate_value_index():
    """Test calcolo Value Index"""
    print("\n=== TEST 2: Calculate Value Index ===")
    
    row = pd.Series({
        'Guide Value': '€2.5M',
        'Age': 21,
        'xA per 90': 1.2,
        'Key Passes per 90': 2.5,
        'Goal Contributions per 90': 1.3,
        'Passaggi progressivi per 90': 2.8,
        'xG per 90': 0.7,
        'NP-xG per 90': 0.6,
        'Shots on Target per 90': 1.5,
        'Dribbling completati per 90': 1.8,
        'Pressures Attempted per 90': 4.0,
        'Possession Won per 90': 3.2,
        'Header Win %': 55.0,
    })
    
    value_index = calculate_value_index(row, price_threshold=int(1e18))
    print(f"Value Index (raw): {value_index:.6f}")
    
    # Validazione
    assert value_index > 0, "Value Index should be positive"
    print("[OK] Value Index test PASSED")


def test_scale_value_index_to_100():
    """Test scaling Value Index a 0-100"""
    print("\n=== TEST 3: Scale Value Index to 100 ===")
    
    # Creare serie di value index
    raw_values = pd.Series([0.0001, 0.0005, 0.001, 0.002, 0.005])
    scaled = scale_value_index_to_100(raw_values)
    
    print(f"Raw values: {raw_values.values}")
    print(f"Scaled values: {scaled.values}")
    
    # Validazione
    assert scaled.min() >= 0, "Scaled min should be >= 0"
    assert scaled.max() <= 100, "Scaled max should be <= 100"
    print("[OK] Scale Value Index test PASSED")


def test_compute_dimension_scores():
    """Test calcolo dimension scores"""
    print("\n=== TEST 4: Compute Dimension Scores ===")
    
    df = pd.DataFrame({
        'Goal Contributions per 90': [1.5, 2.0, 1.0, 2.5],
        'xG per 90': [0.8, 1.2, 0.5, 1.8],
        'Shots on Target per 90': [3.0, 4.0, 2.0, 5.0],
        'xA per 90': [0.5, 0.8, 0.3, 1.0],
        'Key Passes per 90': [2.0, 3.0, 1.5, 4.0],
        'Passaggi progressivi per 90': [1.0, 2.0, 0.5, 3.0],
        'Dribbling completati per 90': [0.8, 1.2, 0.6, 1.5],
        'Pressures Attempted per 90': [10.0, 15.0, 8.0, 20.0],
        'Possession Won per 90': [5.0, 8.0, 3.0, 12.0],
    })
    
    dim_scores = compute_dimension_scores(df)
    print(f"Dimension scores:\n{dim_scores}")
    print(f"Colonne: {list(dim_scores.columns)}")
    
    # Validazione
    expected_cols = ['finalizzazione_score', 'creazione_score', 'dribbling_score', 
                     'pressing_score', 'attacco_score']
    assert list(dim_scores.columns) == expected_cols, f"Expected columns {expected_cols}"
    assert len(dim_scores) == 4, f"Expected 4 rows, got {len(dim_scores)}"
    print("[OK] Dimension Scores test PASSED")


def test_empty_dataframe():
    """Test con DataFrame vuoto"""
    print("\n=== TEST 5: Empty DataFrame ===")
    
    df_empty = pd.DataFrame()
    result_empty = compute_dimension_scores(df_empty)
    print(f"Colonne risultato: {list(result_empty.columns)}")
    print(f"Numero righe: {len(result_empty)}")
    
    assert list(result_empty.columns) == [
        'finalizzazione_score', 'creazione_score', 
        'dribbling_score', 'pressing_score', 'attacco_score'
    ]
    assert len(result_empty) == 0
    print("[OK] Empty DataFrame test PASSED")


def test_value_index_scaling():
    """Test che Value Index sia scalato correttamente tra 0 e 100"""
    print("\n=== TEST 6: Value Index Scaling Range ===")
    
    # Creare dati di test con diversi value index
    df_test = pd.DataFrame({
        'Guide Value': ['€1M', '€2M', '€5M', '€10M'],
        'Age': [19, 22, 25, 28],
        'xA per 90': [0.5, 1.0, 1.5, 2.0],
        'Key Passes per 90': [1.0, 2.0, 3.0, 4.0],
    })
    
    # Calcola value index per ogni riga
    df_test['Value Index'] = df_test.apply(
        lambda row: calculate_value_index(row, price_threshold=int(1e18)), axis=1
    )
    
    # Scala a 0-100
    df_test['Scaled Value Index'] = scale_value_index_to_100(df_test['Value Index'])
    
    print(f"Raw Value Index: {df_test['Value Index'].values}")
    print(f"Scaled Value Index: {df_test['Scaled Value Index'].values}")
    
    # Validazione
    assert df_test['Scaled Value Index'].min() >= 0, "Min should be >= 0"
    assert df_test['Scaled Value Index'].max() <= 100, "Max should be <= 100"
    print("[OK] Value Index Scaling Range test PASSED")


if __name__ == "__main__":
    test_calculate_cof_score()
    test_calculate_value_index()
    test_scale_value_index_to_100()
    test_compute_dimension_scores()
    test_empty_dataframe()
    test_value_index_scaling()
    print("\n[TUTTI I TEST COFF SONO PASSATI CON SUCCESSO!]")
