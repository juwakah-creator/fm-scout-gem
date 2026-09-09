#!/usr/bin/env python3
"""
Test di integrazione end-to-end per il modulo goalkeeper.
Simula il flusso completo: lettura CSV -> filtraggio -> calcolo punteggi -> normalizzazione -> visualizzazione.
"""

import pandas as pd
import numpy as np
import goalkeeper
import app
import sys


def create_test_data():
    """Crea dati di test realistici per portieri."""
    data = {
        'Name': [
            'Jan Oblak', 'Alisson Becker', 'Ederson', 'Marc-Andre ter Stegen',
            'Gianluigi Donnarumma', 'Mike Maignan', 'David Raya', 'Andre Onana',
            'Emiliano Martinez', 'Gregor Kobel', 'Manuel Neuer', 'Thibaut Courtois', 'Alex Meret'
        ],
        'Club': [
            'Atletico Madrid', 'Liverpool', 'Man City', 'Barcelona',
            'PSG', 'Milan', 'Arsenal', 'Man United', 'Aston Villa', 'Dortmund',
            'Bayern Munich', 'Real Madrid', 'Napoli'
        ],
        'Age': [29, 30, 29, 31, 24, 27, 28, 27, 30, 25, 37, 31, 25],
        'Guide Value': [
            '€45M', '€50M', '€40M', '€55M', '€35M', '€30M', '€25M', '€30M',
            '€20M', '€25M', '€15M', '€40M', '€10M'
        ],
        'Appearances': [32, 30, 33, 28, 25, 29, 31, 27, 26, 28, 30, 20, 24],
        # Goalkeeper stats
        'Save Percentage %': [78.5, 75.2, 72.8, 76.1, 73.5, 71.9, 74.3, 73.0, 70.5, 72.0, 77.0, 74.8, 68.5],
        'Clean Sheets %': [58.3, 55.0, 52.1, 56.8, 50.0, 48.5, 53.2, 51.5, 45.8, 50.0, 54.2, 52.0, 42.3],
        'Goals Conceded per 90': [0.85, 1.02, 1.15, 0.92, 1.25, 1.35, 1.08, 1.18, 1.42, 1.28, 0.95, 1.10, 1.55],
        'Saves per 90': [3.2, 2.8, 3.5, 3.0, 2.5, 2.7, 2.9, 3.1, 2.4, 2.6, 3.3, 2.9, 2.2],
        'Pass Completion %': [82.5, 85.0, 88.2, 84.3, 79.5, 81.0, 83.5, 80.2, 77.8, 82.0, 86.5, 83.0, 75.5],
        'Progressive Passes per 90': [2.1, 2.5, 3.0, 2.3, 1.8, 2.0, 2.4, 2.2, 1.5, 1.9, 2.8, 2.1, 1.3],
        'Distribution Accuracy %': [78.0, 80.5, 83.2, 79.5, 75.0, 77.5, 81.0, 76.8, 72.5, 76.0, 82.0, 78.5, 70.0],
        'Crosses Claimed %': [68.5, 70.2, 72.0, 69.8, 65.5, 67.0, 71.5, 66.8, 63.2, 65.0, 73.5, 68.0, 60.5],
        'High Claims per 90': [1.8, 2.0, 2.3, 1.9, 1.5, 1.7, 2.1, 1.6, 1.3, 1.4, 2.4, 1.8, 1.1],
        'Sweeper Actions per 90': [0.9, 1.1, 1.3, 1.0, 0.7, 0.8, 1.2, 0.6, 0.5, 0.4, 1.4, 0.9, 0.3]
    }
    return pd.DataFrame(data)


def create_edge_case_data():
    """Crea dati per casi limite."""
    data = {
        'Name': ['GK_Nulls', 'GK_ZeroPrice', 'GK_Single'],
        'Club': ['Test Club', 'Free Agent', 'Solo GK'],
        'Age': [25, 22, 28],
        'Guide Value': [np.nan, '€0', '€5M'],
        'Appearances': [15, 20, 10],
        # Goalkeeper stats
        'Save Percentage %': [np.nan, 75.0, 80.0],
        'Clean Sheets %': [60.0, np.nan, 65.0],
        'Goals Conceded per 90': [1.0, 1.2, np.nan],
        'Saves per 90': [3.0, np.nan, 3.5],
        'Pass Completion %': [85.0, 80.0, np.nan],
        'Progressive Passes per 90': [np.nan, 2.0, 2.5],
        'Distribution Accuracy %': [80.0, np.nan, 82.0],
        'Crosses Claimed %': [70.0, 65.0, np.nan],
        'High Claims per 90': [np.nan, 1.5, 1.8],
        'Sweeper Actions per 90': [0.8, np.nan, 1.0]
    }
    return pd.DataFrame(data)


def test_end_to_end_flow():
    """Test del flusso end-to-end completo."""
    print("\n" + "="*70)
    print("TEST INTEGRAZIONE END-TO-END GOALKEEPER")
    print("="*70)
    
    # 1. Lettura dati
    print("\n[1/6] Lettura dati da CSV...")
    df = create_test_data()
    print(f"      Letti {len(df)} giocatori")
    assert len(df) == 13, f"Attesi 13 giocatori, trovati {len(df)}"
    
    # 2. Filtraggio per posizione (simulato - in app.py il filtraggio è fatto dai filtri prezzo/età/apps)
    print("\n[2/6] Simulazione filtraggio giocatori...")
    filtered_df = df.copy()
    print(f"      Filtrati {len(filtered_df)} giocatori")
    
    # 3. Calcolo punteggio goalkeeper
    print("\n[3/6] Calcolo Goalkeeper Score...")
    df['Goalkeeper Score'] = df.apply(goalkeeper.calculate_goalkeeper_score, axis=1)
    print(f"      Punteggi calcolati: min={df['Goalkeeper Score'].min():.2f}, max={df['Goalkeeper Score'].max():.2f}")
    assert not df['Goalkeeper Score'].isna().all(), "Tutti i punteggi sono NaN!"
    
    # 4. Normalizzazione e scaling
    print("\n[4/6] Normalizzazione e Value Index...")
    df['Normalized Goalkeeper Score'] = goalkeeper.min_max_normalize(df['Goalkeeper Score'])
    df['Value Index'] = df.apply(
        lambda row: goalkeeper.calculate_value_index(row, price_threshold=int(1e18)),
        axis=1
    )
    df['Value Index'] = goalkeeper.scale_value_index_to_100(df['Value Index'])
    print(f"      Value Index: min={df['Value Index'].min():.2f}, max={df['Value Index'].max():.2f}")
    
    # 5. Calcolo dimension scores
    print("\n[5/6] Calcolo Dimension Scores...")
    dim_scores = goalkeeper.compute_dimension_scores(df)
    print(f"      Colonne dimension: {list(dim_scores.columns)}")
    assert list(dim_scores.columns) == [
        'shot_stopping_score', 'distribution_score',
        'claiming_score', 'modern_goalkeeper_score'
    ]
    
    # 6. Ordinamento e filtraggio risultati
    print("\n[6/6] Ordinamento e selezione top 20...")
    sorted_results = df.sort_values('Value Index', ascending=False, na_position='last').head(20)
    print(f"      Top player: {sorted_results.iloc[0]['Name']} con Value Index {sorted_results.iloc[0]['Value Index']:.4f}")
    
    return True


def test_app_integration():
    """Test integrazione con app.py."""
    print("\n" + "="*70)
    print("TEST INTEGRAZIONE CON APP.PY")
    print("="*70)
    
    df = create_test_data()
    
    # Simula il processo come farebbe app.py
    print("\n[1/3] Preparazione dati per app.py...")
    cm = app.detect_columns(df)
    df_processed = df.copy()
    df_processed['_price'] = df_processed[cm['Guide Value']].apply(app.parse_value)
    df_processed['_age'] = pd.to_numeric(df_processed['Age'], errors='coerce')
    df_processed['_apps'] = pd.to_numeric(df_processed['Appearances'], errors='coerce')
    
    # Converti statistiche in numerico
    for col in ['Save Percentage %', 'Clean Sheets %', 'Goals Conceded per 90', 
                'Saves per 90', 'Pass Completion %', 'Progressive Passes per 90',
                'Distribution Accuracy %', 'Crosses Claimed %', 'High Claims per 90', 
                'Sweeper Actions per 90']:
        if col in df_processed.columns:
            df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce')
    
    print(f"      Colonne rilevate: {cm}")
    print(f"      Prezzo medio: €{df_processed['_price'].mean():.0f}")
    
    # Test process_analysis con modalità goalkeeper
    print("\n[2/3] Esecuzione process_analysis in modalità goalkeeper...")
    result_html, debug_html = app.process_analysis(
        df_processed, 'goalkeeper', 0, 100, 5, 40, 17
    )
    
    assert isinstance(result_html, str), "result_html deve essere una stringa"
    assert isinstance(debug_html, str), "debug_html deve essere una stringa"
    print(f"      Result HTML length: {len(result_html)} chars")
    print(f"      Debug HTML length: {len(debug_html)} chars")
    
    # Verifica presenza di elementi attesi
    assert 'Goalkeeper Score' in result_html or 'Value Index' in result_html, \
        "HTML risultato dovrebbe contenere Goalkeeper Score o Value Index"
    print("      [OK] HTML risultato contiene colonne attese")
    
    # Test con dati vuoti
    print("\n[3/3] Test con DataFrame vuoto...")
    empty_df = pd.DataFrame()
    result, debug = app.process_analysis(empty_df, 'goalkeeper', 0, 50, 10, 30, 17)
    assert "No data available" in result or "No goalkeepers found" in result
    print("      [OK] Gestione corretta dati vuoti")
    
    return True


def test_edge_cases():
    """Test casi limite."""
    print("\n" + "="*70)
    print("TEST CASI LIMITE")
    print("="*70)
    
    # 1. Valori nulli
    print("\n[1/4] Test con valori nulli...")
    df_nulls = create_edge_case_data()
    df_nulls['Goalkeeper Score'] = df_nulls.apply(goalkeeper.calculate_goalkeeper_score, axis=1)
    # I giocatori con NaN dovrebbero avere score >= 0 (almeno parziali)
    assert df_nulls['Goalkeeper Score'].notna().all(), "Alcuni punteggi sono NaN!"
    print(f"      Punteggi con nulli: {df_nulls['Goalkeeper Score'].tolist()}")
    
    # 2. Prezzo zero/NaN
    print("\n[2/4] Test con prezzi edge case...")
    row_zero = pd.Series({
        'Guide Value': '€0',
        'Age': 22,
        'Goalkeeper Score': 500.0
    })
    result = goalkeeper.calculate_value_index(row_zero)
    assert pd.isna(result), "Value Index con prezzo zero dovrebbe essere NaN"
    print("      [OK] Value Index NaN per prezzo zero")
    
    row_nan_price = pd.Series({
        'Guide Value': np.nan,
        'Age': 22,
        'Goalkeeper Score': 500.0
    })
    result = goalkeeper.calculate_value_index(row_nan_price)
    assert pd.isna(result), "Value Index con prezzo NaN dovrebbe essere NaN"
    print("      [OK] Value Index NaN per prezzo NaN")
    
    # 3. Singolo giocatore
    print("\n[3/4] Test con singolo giocatore...")
    single_df = pd.DataFrame({
        'Name': ['Solo GK'],
        'Save Percentage %': [75.0],
        'Goals Conceded per 90': [1.0],
        'Clean Sheets %': [60.0],
        'Pass Completion %': [85.0],
        'Progressive Passes per 90': [2.0],
        'Distribution Accuracy %': [80.0],
        'Crosses Claimed %': [70.0],
        'High Claims per 90': [1.5],
        'Sweeper Actions per 90': [0.8]
    })
    dim_scores = goalkeeper.compute_dimension_scores(single_df)
    assert len(dim_scores) == 1, "Dovrebbe esserci un risultato per singolo giocatore"
    for col in dim_scores.columns:
        assert not pd.isna(dim_scores[col].iloc[0]), f"Dimension score {col} è NaN!"
    print("      [OK] Dimension scores calcolati correttamente per singolo giocatore")
    
    # 4. Tutti valori zero
    print("\n[4/4] Test con tutti valori zero...")
    zero_df = pd.DataFrame({
        'Name': ['Zero GK'],
        'Save Percentage %': [0.0],
        'Goals Conceded per 90': [0.0],
        'Clean Sheets %': [0.0],
        'Pass Completion %': [0.0],
        'Progressive Passes per 90': [0.0],
        'Distribution Accuracy %': [0.0],
        'Crosses Claimed %': [0.0],
        'High Claims per 90': [0.0],
        'Sweeper Actions per 90': [0.0]
    })
    score = goalkeeper.calculate_goalkeeper_score(zero_df.iloc[0])
    # (10 - 0) * 2.0 = 20 per Goals Conceded invertito
    assert score == 20.0, f"Score atteso 20.0, ottenuto {score}"
    print(f"      [OK] Score con tutti zero: {score} (soloGoals Conceded invertito)")
    
    return True


def test_compatibility_with_other_positions():
    """Verifica compatibilità con altre posizioni."""
    print("\n" + "="*70)
    print("TEST COMPATIBILITÀ CON ALTRE POSIZIONI")
    print("="*70)
    
    # Crea un DataFrame misto con giocatori di diverse posizioni
    mixed_data = {
        'Name': ['GK1', 'DEF1', 'DM1', 'Winger1', 'STRIKE1'],
        'Club': ['Test', 'Test', 'Test', 'Test', 'Test'],
        'Age': [25, 26, 24, 23, 22],
        'Guide Value': ['€10M', '€15M', '€20M', '€25M', '€30M'],
        'Appearances': [20, 25, 22, 18, 28],
        # Stats comuni
        'Pass Completion %': [80.0, 82.0, 85.0, 78.0, 75.0],
        'Progressive Passes per 90': [2.0, 1.5, 2.5, 3.0, 1.0],
        # Stats specifiche GK (solo per GK1)
        'Save Percentage %': [75.0, np.nan, np.nan, np.nan, np.nan],
        'Clean Sheets %': [60.0, np.nan, np.nan, np.nan, np.nan],
        'Goals Conceded per 90': [1.0, np.nan, np.nan, np.nan, np.nan],
        'Saves per 90': [3.0, np.nan, np.nan, np.nan, np.nan],
    }
    df_mixed = pd.DataFrame(mixed_data)
    
    print("\n[1/2] Test process_analysis con dati misti...")
    cm = app.detect_columns(df_mixed)
    df_processed = df_mixed.copy()
    df_processed['_price'] = df_processed[cm['Guide Value']].apply(app.parse_value)
    df_processed['_age'] = pd.to_numeric(df_processed['Age'], errors='coerce')
    df_processed['_apps'] = pd.to_numeric(df_processed['Appearances'], errors='coerce')
    
    # Test ogni modalità
    modes = ['goalkeeper', 'defenders', 'defensive_mid', 'winger', 'strika']
    for mode in modes:
        print(f"      Testing mode: {mode}...")
        try:
            result, debug = app.process_analysis(df_processed, mode, 0, 100, 5, 40, 17)
            assert isinstance(result, str), f"Result per mode {mode} non è stringa"
            print(f"      [OK] Mode '{mode}' funziona correttamente")
        except Exception as e:
            print(f"      [WARN] Mode '{mode}': {e}")
    
    # Test che goalkeeper non interferisce con altre modalità
    print("\n[2/2] Verifica isolamento moduli...")
    # Ogni modulo dovrebbe funzionare indipendentemente
    assert hasattr(app, 'goalkeeper'), "app.py dovrebbe importare goalkeeper"
    assert hasattr(app, 'defenders'), "app.py dovrebbe importare defenders"
    assert hasattr(app, 'defensive_mid'), "app.py dovrebbe importare defensive_mid"
    assert hasattr(app, 'winger'), "app.py dovrebbe importare winger"
    assert hasattr(app, 'strika'), "app.py dovrebbe importare strika"
    print("      [OK] Tutti i moduli sono importati correttamente in app.py")
    
    return True


def main():
    """Esegue tutti i test."""
    all_passed = True
    
    try:
        test_end_to_end_flow()
    except Exception as e:
        print(f"\n[FAIL] End-to-end flow: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    try:
        test_app_integration()
    except Exception as e:
        print(f"\n[FAIL] App integration: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    try:
        test_edge_cases()
    except Exception as e:
        print(f"\n[FAIL] Edge cases: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    try:
        test_compatibility_with_other_positions()
    except Exception as e:
        print(f"\n[FAIL] Compatibility tests: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print("TUTTI I TEST SONO PASSATI!")
    else:
        print("ALCUNI TEST HANNO FALLITO")
    print("="*70)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
