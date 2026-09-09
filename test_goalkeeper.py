#!/usr/bin/env python3
"""Test script for goalkeeper.py integration."""

import pandas as pd
import numpy as np
import pytest
import goalkeeper
import app


class TestParseGuideValue:
    """Test per la funzione parse_guide_value()."""
    
    def test_normal_number(self):
        """Test con valore numerico normale."""
        assert goalkeeper.parse_guide_value("500000") == 500000.0
    
    def test_with_euro_symbol(self):
        """Test con simbolo €."""
        assert goalkeeper.parse_guide_value("€500000") == 500000.0
    
    def test_k_suffix(self):
        """Test con suffisso K (migliaia)."""
        assert goalkeeper.parse_guide_value("25K") == 25000.0
        assert goalkeeper.parse_guide_value("€25K") == 25000.0
    
    def test_m_suffix(self):
        """Test con suffisso M (milioni)."""
        assert goalkeeper.parse_guide_value("3.5M") == 3500000.0
        assert goalkeeper.parse_guide_value("€3.5M") == 3500000.0
    
    def test_nan_input(self):
        """Test con input NaN."""
        assert pd.isna(goalkeeper.parse_guide_value(np.nan))
    
    def test_empty_string(self):
        """Test con stringa vuota."""
        assert pd.isna(goalkeeper.parse_guide_value(""))
    
    def test_none_input(self):
        """Test con input None."""
        assert pd.isna(goalkeeper.parse_guide_value(None))
    
    def test_invalid_format(self):
        """Test con formato non valido."""
        result = goalkeeper.parse_guide_value("abc")
        assert pd.isna(result)


class TestCalculateAgeFactor:
    """Test per la funzione calculate_age_factor()."""
    
    def test_young_player(self):
        """Test per giocatore giovane (<= 20 anni)."""
        assert goalkeeper.calculate_age_factor(18) == 2.0
        assert goalkeeper.calculate_age_factor(20) == 2.0
    
    def test_early_twenties(self):
        """Test per giocatori nei primi vent'anni (21-23)."""
        assert goalkeeper.calculate_age_factor(21) == 1.6
        assert goalkeeper.calculate_age_factor(23) == 1.6
    
    def test_mid_twenties(self):
        """Test per giocatori nella seconda metà dei vent'anni (24-26)."""
        assert goalkeeper.calculate_age_factor(24) == 1.3
        assert goalkeeper.calculate_age_factor(26) == 1.3
    
    def test_older_player(self):
        """Test per giocatore più anziano (> 26 anni)."""
        assert goalkeeper.calculate_age_factor(30) == 1.0
        assert goalkeeper.calculate_age_factor(35) == 1.0
    
    def test_nan_age(self):
        """Test con età NaN."""
        assert goalkeeper.calculate_age_factor(np.nan) == 1.0
    
    def test_negative_age(self):
        """Test con età negativa."""
        assert goalkeeper.calculate_age_factor(-5) == 1.0


class TestCalculateGoalkeeperScore:
    """Test per la funzione calculate_goalkeeper_score()."""
    
    def test_all_metrics_present(self):
        """Test con tutti i metriche presenti."""
        row = pd.Series({
            'Save Percentage %': 75.0,
            'Clean Sheets %': 60.0,
            'Goals Conceded per 90': 1.0,
            'Saves per 90': 3.5,
            'Pass Completion %': 85.0,
            'Progressive Passes per 90': 2.0,
            'Distribution Accuracy %': 80.0,
            'Crosses Claimed %': 70.0,
            'High Claims per 90': 1.5,
            'Sweeper Actions per 90': 0.8
        })
        score = goalkeeper.calculate_goalkeeper_score(row)
        # Calcolo manuale:
        # Save% * 3.0 = 75 * 3.0 = 225.0
        # CleanSheets% * 2.5 = 60 * 2.5 = 150.0
        # (10 - GoalsConceded) * 2.0 = (10 - 1) * 2.0 = 18.0
        # Saves * 1.5 = 3.5 * 1.5 = 5.25
        # PassCompletion% * 1.5 = 85 * 1.5 = 127.5
        # ProgressivePasses * 1.0 = 2.0 * 1.0 = 2.0
        # DistributionAccuracy% * 1.0 = 80 * 1.0 = 80.0
        # CrossesClaimed% * 1.0 = 70 * 1.0 = 70.0
        # HighClaims * 0.8 = 1.5 * 0.8 = 1.2
        # SweeperActions * 0.5 = 0.8 * 0.5 = 0.4
        expected = 225.0 + 150.0 + 18.0 + 5.25 + 127.5 + 2.0 + 80.0 + 70.0 + 1.2 + 0.4
        assert score == pytest.approx(expected, abs=0.01)
    
    def test_all_nan(self):
        """Test con tutte le metriche NaN."""
        row = pd.Series({
            'Save Percentage %': np.nan,
            'Clean Sheets %': np.nan,
            'Goals Conceded per 90': np.nan,
            'Saves per 90': np.nan,
            'Pass Completion %': np.nan,
            'Progressive Passes per 90': np.nan,
            'Distribution Accuracy %': np.nan,
            'Crosses Claimed %': np.nan,
            'High Claims per 90': np.nan,
            'Sweeper Actions per 90': np.nan
        })
        score = goalkeeper.calculate_goalkeeper_score(row)
        assert score == 0.0
    
    def test_partial_metrics(self):
        """Test con solo alcune metriche presenti."""
        row = pd.Series({
            'Save Percentage %': 80.0,
            'Clean Sheets %': np.nan,
            'Goals Conceded per 90': np.nan,
            'Saves per 90': np.nan,
            'Pass Completion %': np.nan,
            'Progressive Passes per 90': np.nan,
            'Distribution Accuracy %': np.nan,
            'Crosses Claimed %': np.nan,
            'High Claims per 90': np.nan,
            'Sweeper Actions per 90': np.nan
        })
        score = goalkeeper.calculate_goalkeeper_score(row)
        assert score == pytest.approx(80.0 * 3.0, abs=0.01)
    
    def test_missing_columns(self):
        """Test con colonne mancanti."""
        row = pd.Series({'Name': 'Test'})
        score = goalkeeper.calculate_goalkeeper_score(row)
        assert score == 0.0


class TestMinMaxNormalize:
    """Test per la funzione min_max_normalize()."""
    
    def test_normal_series(self):
        """Test con serie normale."""
        series = pd.Series([10, 20, 30, 40, 50])
        result = goalkeeper.min_max_normalize(series)
        expected = pd.Series([0.0, 0.25, 0.5, 0.75, 1.0])
        pd.testing.assert_series_equal(result, expected)
    
    def test_all_same_values(self):
        """Test con tutti valori uguali."""
        series = pd.Series([5, 5, 5, 5])
        result = goalkeeper.min_max_normalize(series)
        expected = pd.Series([0.0, 0.0, 0.0, 0.0])
        pd.testing.assert_series_equal(result, expected)
    
    def test_empty_series(self):
        """Test con serie vuota."""
        series = pd.Series([], dtype=float)
        result = goalkeeper.min_max_normalize(series)
        assert len(result) == 0
    
    def test_with_nan(self):
        """Test con valori NaN."""
        series = pd.Series([10, np.nan, 30, 40])
        result = goalkeeper.min_max_normalize(series)
        # I NaN dovrebbero rimanere NaN o essere riempiti con 0
        assert pd.isna(result.iloc[1]) or result.iloc[1] == 0


class TestScaleValueIndexTo100:
    """Test per la funzione scale_value_index_to_100()."""
    
    def test_normal_series(self):
        """Test con serie normale."""
        series = pd.Series([1, 2, 3, 4, 5])
        result = goalkeeper.scale_value_index_to_100(series)
        expected = pd.Series([0.0, 25.0, 50.0, 75.0, 100.0])
        pd.testing.assert_series_equal(result, expected)
    
    def test_all_same_values(self):
        """Test con tutti valori uguali."""
        series = pd.Series([5, 5, 5, 5])
        result = goalkeeper.scale_value_index_to_100(series)
        expected = pd.Series([50.0, 50.0, 50.0, 50.0])
        pd.testing.assert_series_equal(result, expected)
    
    def test_empty_series(self):
        """Test con serie vuota."""
        series = pd.Series([], dtype=float)
        result = goalkeeper.scale_value_index_to_100(series)
        assert len(result) == 0


class TestCalculateValueIndex:
    """Test per la funzione calculate_value_index()."""
    
    def test_valid_player(self):
        """Test con giocatore valido."""
        row = pd.Series({
            'Guide Value': '€1000000',
            'Age': 22,
            'Goalkeeper Score': 500.0
        })
        result = goalkeeper.calculate_value_index(row, price_threshold=int(1e18))
        # Age factor per 22 anni = 1.6
        # Value Index = (500 * 1.6) / 1000000 = 0.0008
        expected = (500.0 * 1.6) / 1000000
        assert result == pytest.approx(expected, abs=0.0001)
    
    def test_nan_guide_value(self):
        """Test con Guide Value NaN."""
        row = pd.Series({
            'Guide Value': np.nan,
            'Age': 22,
            'Goalkeeper Score': 500.0
        })
        result = goalkeeper.calculate_value_index(row)
        assert pd.isna(result)
    
    def test_nan_age(self):
        """Test con età NaN."""
        row = pd.Series({
            'Guide Value': '€1000000',
            'Age': np.nan,
            'Goalkeeper Score': 500.0
        })
        result = goalkeeper.calculate_value_index(row)
        assert pd.isna(result)
    
    def test_nan_goalkeeper_score(self):
        """Test con Goalkeeper Score NaN."""
        row = pd.Series({
            'Guide Value': '€1000000',
            'Age': 22,
            'Goalkeeper Score': np.nan
        })
        result = goalkeeper.calculate_value_index(row)
        assert pd.isna(result)
    
    def test_price_above_threshold(self):
        """Test con prezzo sopra la soglia."""
        row = pd.Series({
            'Guide Value': '€10M',
            'Age': 22,
            'Goalkeeper Score': 500.0
        })
        result = goalkeeper.calculate_value_index(row, price_threshold=5000000)
        assert pd.isna(result)


class TestCalculateAdditionalMetrics:
    """Test per la funzione calculate_additional_metrics()."""
    
    def test_all_metrics_present(self):
        """Test con tutte le metriche presenti."""
        row = pd.Series({
            'Save Percentage %': 75.0,
            'Goals Conceded per 90': 1.0,
            'Progressive Passes per 90': 2.0,
            'Pass Completion %': 85.0,
            'Crosses Claimed %': 70.0,
            'High Claims per 90': 1.5
        })
        metrics = goalkeeper.calculate_additional_metrics(row)
        
        # Shot Stopping Efficiency = (75 * 10) / (1 + 1) = 375
        assert metrics['Shot Stopping Efficiency'] == pytest.approx(375.0, abs=0.01)
        # Distribution Quality = 2.0 * (85 / 100) = 1.7
        assert metrics['Distribution Quality'] == pytest.approx(1.7, abs=0.01)
        # Claiming Ability = (70 + 1.5 * 10) / 2 = 42.5
        assert metrics['Claiming Ability'] == pytest.approx(42.5, abs=0.01)
    
    def test_partial_metrics(self):
        """Test con solo alcune metriche."""
        row = pd.Series({
            'Save Percentage %': 75.0,
            'Goals Conceded per 90': np.nan
        })
        metrics = goalkeeper.calculate_additional_metrics(row)
        assert pd.isna(metrics['Shot Stopping Efficiency'])
        assert pd.isna(metrics['Distribution Quality'])
        assert pd.isna(metrics['Claiming Ability'])


class TestComputeDimensionScores:
    """Test per la funzione compute_dimension_scores()."""
    
    def test_empty_dataframe(self):
        """Test con DataFrame vuoto."""
        df = pd.DataFrame()
        result = goalkeeper.compute_dimension_scores(df)
        assert list(result.columns) == [
            'shot_stopping_score', 'distribution_score',
            'claiming_score', 'modern_goalkeeper_score'
        ]
        assert len(result) == 0
    
    def test_with_metrics(self):
        """Test con metriche presenti."""
        df = pd.DataFrame({
            'Name': ['GK1', 'GK2', 'GK3'],
            'Save Percentage %': [75.0, 80.0, 70.0],
            'Goals Conceded per 90': [1.0, 0.8, 1.2],
            'Clean Sheets %': [60.0, 65.0, 55.0],
            'Pass Completion %': [85.0, 90.0, 80.0],
            'Progressive Passes per 90': [2.0, 2.5, 1.5],
            'Distribution Accuracy %': [80.0, 85.0, 75.0],
            'Crosses Claimed %': [70.0, 75.0, 65.0],
            'High Claims per 90': [1.5, 2.0, 1.0],
            'Sweeper Actions per 90': [0.8, 1.0, 0.6]
        })
        result = goalkeeper.compute_dimension_scores(df)
        
        assert list(result.columns) == [
            'shot_stopping_score', 'distribution_score',
            'claiming_score', 'modern_goalkeeper_score'
        ]
        assert len(result) == 3
        # I punteggi dovrebbero essere tra 0 e 100 (percentili ponderati)
        for col in result.columns:
            assert result[col].notna().all()
    
    def test_missing_metrics(self):
        """Test con alcune metriche mancanti."""
        df = pd.DataFrame({
            'Name': ['GK1', 'GK2'],
            'Save Percentage %': [75.0, 80.0],
            # Mancano altre metriche
        })
        result = goalkeeper.compute_dimension_scores(df)
        
        assert list(result.columns) == [
            'shot_stopping_score', 'distribution_score',
            'claiming_score', 'modern_goalkeeper_score'
        ]


class TestAppIntegration:
    """Test per l'integrazione con app.py."""
    
    def test_import_goalkeeper(self):
        """Test che goalkeeper possa essere importato in app.py."""
        assert hasattr(app, 'goalkeeper')
    
    def test_process_analysis_goalkeeper_mode(self):
        """Test process_analysis con modalità goalkeeper."""
        df = pd.read_csv('sample_players.csv')
        result_html, debug_html = app.process_analysis(df, 'goalkeeper', 0, 50, 10, 30, 17)
        
        assert isinstance(result_html, str)
        assert isinstance(debug_html, str)
        # Verifica che l'HTML contenga gli elementi attesi
        assert 'Goalkeeper Score' in result_html or 'No goalkeepers found' in result_html
    
    def test_process_analysis_invalid_mode(self):
        """Test con modalità non valida."""
        df = pd.read_csv('sample_players.csv')
        with pytest.raises(ValueError):
            app.process_analysis(df, 'invalid_mode', 0, 50, 10, 30, 17)


class TestEdgeCases:
    """Test per casi limite e edge cases."""
    
    def test_goalkeeper_score_with_zero_values(self):
        """Test con valori zero."""
        row = pd.Series({
            'Save Percentage %': 0.0,
            'Clean Sheets %': 0.0,
            'Goals Conceded per 90': 0.0,
            'Saves per 90': 0.0,
            'Pass Completion %': 0.0,
            'Progressive Passes per 90': 0.0,
            'Distribution Accuracy %': 0.0,
            'Crosses Claimed %': 0.0,
            'High Claims per 90': 0.0,
            'Sweeper Actions per 90': 0.0
        })
        score = goalkeeper.calculate_goalkeeper_score(row)
        # (10 - 0) * 2.0 = 20 per Goals Conceded invertito
        assert score == pytest.approx(20.0, abs=0.01)
    
    def test_value_index_with_zero_price(self):
        """Test con prezzo zero."""
        row = pd.Series({
            'Guide Value': '€0',
            'Age': 22,
            'Goalkeeper Score': 500.0
        })
        result = goalkeeper.calculate_value_index(row)
        assert pd.isna(result)
    
    def test_dimension_scores_single_player(self):
        """Test con un solo giocatore."""
        df = pd.DataFrame({
            'Name': ['GK1'],
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
        result = goalkeeper.compute_dimension_scores(df)
        assert len(result) == 1
        for col in result.columns:
            assert not pd.isna(result[col].iloc[0])


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
