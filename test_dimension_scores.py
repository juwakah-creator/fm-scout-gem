#!/usr/bin/env python3
"""Test script for compute_dimension_scores function"""

import pandas as pd
import numpy as np
import sys
sys.path.insert(0, '.')

from winger import compute_dimension_scores

# Test 1: DataFrame vuoto
print("=== Test 1: DataFrame vuoto ===")
df_empty = pd.DataFrame()
result_empty = compute_dimension_scores(df_empty)
print(f"Colonne risultato: {list(result_empty.columns)}")
print(f"Numero righe: {len(result_empty)}")
assert list(result_empty.columns) == [
    'finalizzazione_score', 'creazione_score', 
    'pressing_score', 'difesa_aerea_score', 'attacco_score'
]
assert len(result_empty) == 0
print("PASS\n")

# Test 2: DataFrame con dati completi
print("=== Test 2: DataFrame con dati completi ===")
df_complete = pd.DataFrame({
    'Goal Contributions per 90': [1.5, 2.0, 1.0, 2.5],
    'xG per 90': [0.8, 1.2, 0.5, 1.8],
    'Shots on Target per 90': [3.0, 4.0, 2.0, 5.0],
    'xG Overperformance': [0.1, 0.3, -0.1, 0.5],
    'xA per 90': [0.5, 0.8, 0.3, 1.0],
    'Key Passes per 90': [2.0, 3.0, 1.5, 4.0],
    'Passaggi progressivi per 90': [1.0, 2.0, 0.5, 3.0],
    'Pressures Attempted per 90': [10.0, 15.0, 8.0, 20.0],
    'Possession Won per 90': [5.0, 8.0, 3.0, 12.0],
    'Header Win %': [60.0, 70.0, 50.0, 80.0]
})

result_complete = compute_dimension_scores(df_complete)
print(result_complete)
print(f"Colonne: {list(result_complete.columns)}")
assert list(result_complete.columns) == [
    'finalizzazione_score', 'creazione_score', 
    'pressing_score', 'difesa_aerea_score', 'attacco_score'
]
assert len(result_complete) == 4
print("PASS\n")

# Test 3: DataFrame con metriche mancanti
print("=== Test 3: DataFrame con metriche mancanti ===")
df_partial = pd.DataFrame({
    'Goal Contributions per 90': [1.5, 2.0],
    'xG per 90': [0.8, np.nan],
    # Mancano Shots on Target e xG Overperformance
    'xA per 90': [0.5, 0.8],
    # Mancano Key Passes e Passaggi progressivi
    'Pressures Attempted per 90': [10.0, 15.0],
    # Mancano Possession Won
    'Header Win %': [60.0, 70.0]
})

result_partial = compute_dimension_scores(df_partial)
print(result_partial)
assert list(result_partial.columns) == [
    'finalizzazione_score', 'creazione_score', 
    'pressing_score', 'difesa_aerea_score', 'attacco_score'
]
# finalizzazione deve avere valori (almeno 2 metriche presenti)
# creazione deve avere valore (1 metrica presente)
# pressing deve avere valore (1 metrica presente)
# difesa_aerea deve avere valore
print("PASS\n")

# Test 4: DataFrame con tutte le metriche mancanti per una dimensione
print("=== Test 4: Tutte le metriche mancanti ===")
df_no_metrics = pd.DataFrame({
    'Name': ['Player1', 'Player2'],
    'Age': [25, 28]
})

result_no_metrics = compute_dimension_scores(df_no_metrics)
print(result_no_metrics)
assert list(result_no_metrics.columns) == [
    'finalizzazione_score', 'creazione_score', 
    'pressing_score', 'difesa_aerea_score', 'attacco_score'
]
# Tutte le colonne devono essere NaN
assert result_no_metrics['finalizzazione_score'].isna().all()
assert result_no_metrics['creazione_score'].isna().all()
assert result_no_metrics['pressing_score'].isna().all()
assert result_no_metrics['difesa_aerea_score'].isna().all()
assert result_no_metrics['attacco_score'].isna().all()
print("PASS\n")

# Test 5: Header Win % mancante (default 50)
print("=== Test 5: Header Win % mancante ===")
df_no_header = pd.DataFrame({
    'Goal Contributions per 90': [1.5, 2.0],
    'xG per 90': [0.8, 1.2],
    'Shots on Target per 90': [3.0, 4.0],
    'xG Overperformance': [0.1, 0.3],
    'xA per 90': [0.5, 0.8],
    'Key Passes per 90': [2.0, 3.0],
    'Passaggi progressivi per 90': [1.0, 2.0],
    'Pressures Attempted per 90': [10.0, 15.0],
    'Possession Won per 90': [5.0, 8.0]
    # Header Win % non presente
})

result_no_header = compute_dimension_scores(df_no_header)
print(result_no_header)
# difesa_aerea_score dovrebbe essere 50.0 (default) per entrambi i giocatori
assert result_no_header['difesa_aerea_score'].notna().all()
assert all(result_no_header['difesa_aerea_score'] == 50.0)
print("PASS\n")

print("=== Tutti i test passati! ===")
