#!/usr/bin/env python3
"""
Scoring System V2 - Football Player Analysis
"""
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')


def calculate_score_percentile(df: pd.DataFrame, role: str = 'coff') -> pd.Series:
    """Calculate percentile score for role."""
    
    WEIGHTS = {
        'coff': [
            ('xA per 90', 2.5),
            ('Key Passes per 90', 2.0),
            ('Goal Contributions per 90', 2.0),
            ('Passaggi progressivi per 90', 1.5),
            ('xG per 90', 1.5),
            ('Shots on Target per 90', 1.0),
            ('NP-xG per 90', 1.2),
            ('Dribbling completati per 90', 1.0),
        ],
        'striker': [
            ('Goal Contributions per 90', 3.0),
            ('NP-xG per 90', 2.5),
            ('xG per 90', 2.0),
            ('Shots on Target per 90', 1.5),
            ('xG Overperformance', 0.8),
            ('xA per 90', 1.0),
            ('Key Passes per 90', 1.0),
        ],
        'winger': [
            ('Dribbling completati per 90', 2.5),
            ('xA per 90', 2.0),
            ('Key Passes per 90', 1.5),
            ('Goal Contributions per 90', 2.0),
            ('Cross riusciti per 90', 1.5),
            ('Passaggi progressivi per 90', 1.0),
        ],
        'defensive_mid': [
            ('Tackles per 90', 2.5),
            ('Interceptions per 90', 2.0),
            ('Dribbling completati per 90', 1.5),
            ('Passaggi completi per 90', 1.5),
            ('Pass Completion %', 2.0),
            ('Pressures Attempted per 90', 0.5),
            ('Possession Won per 90', 0.5),
        ],
        'defender': [
            ('Tackles per 90', 2.5),
            ('Interceptions per 90', 2.0),
            ('Clearances per 90', 1.5),
            ('Header Win %', 1.5),
            ('Blocks per 90', 1.5),
            ('Pass Completion %', 1.0),
        ],
        'fullback': [
            ('Dribbling completati per 90', 2.0),
            ('xA per 90', 2.0),
            ('Key Passes per 90', 2.0),
            ('Cross riusciti per 90', 1.5),
            ('Defensive Actions per 90', 1.5),
            ('Tackles per 90', 1.5),
        ],
        'goalkeeper': [
            ('Save %', 3.0),
            ('Clean Sheets %', 2.5),
            ('Goals Conceded per 90', 2.0),
            ('Pass Completion %', 1.0),
        ],
    }
    
    if role not in WEIGHTS:
        raise ValueError(f"Unknown role: {role}")
    
    stats_weights = WEIGHTS[role]
    total_weight = sum(w for _, w in stats_weights)
    
    score = pd.Series(0.0, index=df.index)
    
    for stat_name, weight in stats_weights:
        if stat_name not in df.columns:
            continue
        col = df[stat_name].fillna(50.0)
        pct = col.rank(pct=True) * 100
        score = score + pct * weight
    
    return score / total_weight


def calculate_value_index(row: pd.Series, score: float = 50.0) -> float:
    """Calculate Value Index = (Score * AgeFactor) / Price."""
    guide_value = row.get('Guide Value', np.nan)
    age = pd.to_numeric(row.get('Age', np.nan), errors='coerce')
    
    if pd.isna(guide_value) or pd.isna(age) or pd.isna(score):
        return np.nan
    
    # Parse price
    price = 0
    try:
        parsed = str(guide_value).strip().replace('€', '').replace(' ', '')
        if parsed.endswith('K'):
            price = float(parsed[:-1]) * 1000
        elif parsed.endswith('M'):
            price = float(parsed[:-1]) * 1000000
        else:
            price = float(parsed)
    except ValueError:
        return np.nan
    
    if price <= 0:
        return np.nan
    
    # Age factor
    if pd.isna(age) or age < 0:
        age_factor = 1.0
    elif age <= 20:
        age_factor = 2.0
    elif age <= 23:
        age_factor = 1.6
    elif age <= 26:
        age_factor = 1.3
    else:
        age_factor = 1.0
    
    return (score * age_factor) / price


def parse_guide_value(value) -> float:
    """Parse Guide Value with €, K, M."""
    if pd.isna(value) or value == '' or value is None:
        return np.nan
    cleaned = str(value).strip().replace('€', '').replace(' ', '')
    try:
        if cleaned.endswith('K'):
            return float(cleaned[:-1]) * 1000
        elif cleaned.endswith('M'):
            return float(cleaned[:-1]) * 1000000
        else:
            return float(cleaned)
    except ValueError:
        return np.nan