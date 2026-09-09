#!/usr/bin/env python3
"""
Fullbacks Analysis Module

This module provides functions for analyzing fullback players using weighted statistics.
It calculates a comprehensive score based on defensive, creative, and attacking metrics.
"""

import pandas as pd
import numpy as np


# Fullback-specific weights dictionary
FULLBACK_WEIGHTS = {
    "Defensive Actions per 90": 2.8,  # Aumentato da 2.5 a 2.8 per enfatizzare l'azione difensiva
    "Possession Won per 90": 2.2,  # Aumentato da 2.0 a 2.2 per valorizzare il recupero possesso
    "Blocks per 90": 1.8,
    "Pressures Attempted per 90": 1.5,
    "xA per 90": 2.5,
    "Key Passes per 90": 2.5,  # Ridotto da 3.0 a 2.5 per bilanciamento
    "Progressive Passes per 90": 2.0,
    "Progressive Pass %": 2.5,
    "Open Play Cross Completion %": 1.8,
    "Clear Cut Chances Created": 2.0,
    "Crosses Completed": 2.5,
    "Dribbles per 90": 1.5,
    "Goal Contributions per 90": 1.5,
    "xG per 90": 1.0,
    "xG Overperformance": 0.5,
    "Header Win %": 2.0,  # Aumentato da 1.5 a 2.0 per enfatizzare il gioco aereo
    "Mistakes Leading to Goals": -2.0
}


def calculate_fullback_score(row):
    """Calculate a comprehensive fullback score based on weighted statistics.
    
    Args:
        row: DataFrame row containing player statistics
        
    Returns:
        float: Fullback score (weighted sum of normalized stats)
    """
    score = 0.0
    
    # Defensive metrics - use .get() to safely access columns that may not exist
    defensive_stats = {
        "Defensive Actions per 90": 2.8,  # Uniformato con FULLBACK_WEIGHTS
        "Possession Won per 90": 2.2,  # Uniformato con FULLBACK_WEIGHTS
        "Blocks per 90": 1.8,
        "Pressures Attempted per 90": 1.5
    }
    
    for stat_name, weight in defensive_stats.items():
        value = row.get(stat_name)
        if value is not None and pd.notna(value):
            try:
                score += float(value) * weight
            except (ValueError, TypeError):
                pass
    
    # Creative metrics
    creative_stats = {
        "xA per 90": 2.5,
        "Key Passes per 90": 2.5,  # Uniformato con FULLBACK_WEIGHTS (ridotto da 3.0)
        "Progressive Passes per 90": 2.0,
        "Progressive Pass %": 2.5,
        "Open Play Cross Completion %": 1.8,
        "Clear Cut Chances Created": 2.0,
        "Crosses Completed": 2.5
    }
    
    for stat_name, weight in creative_stats.items():
        value = row.get(stat_name)
        if value is not None and pd.notna(value):
            try:
                score += float(value) * weight
            except (ValueError, TypeError):
                pass
    
    # Attacking metrics
    attacking_stats = {
        "Dribbles per 90": 1.5,
        "Goal Contributions per 90": 1.5,
        "xG per 90": 1.0,
        "xG Overperformance": 0.5,
        "Header Win %": 2.0  # Uniformato con FULLBACK_WEIGHTS (aumentato da 1.5)
    }
    
    for stat_name, weight in attacking_stats.items():
        value = row.get(stat_name)
        if value is not None and pd.notna(value):
            try:
                score += float(value) * weight
            except (ValueError, TypeError):
                pass
    
    # Negative metric (penalty for mistakes)
    value = row.get("Mistakes Leading to Goals")
    if value is not None and pd.notna(value):
        try:
            mistakes = float(value)
            score += mistakes * FULLBACK_WEIGHTS["Mistakes Leading to Goals"]
        except (ValueError, TypeError):
            pass
    
    return score


def min_max_normalize(series):
    """Normalize a series using min-max scaling.
    
    Args:
        series: Input pandas Series
        
    Returns:
        pandas Series: Normalized values in range [0, 1]
    """
    if len(series) == 0:
        return pd.Series([0.0])
    
    min_val = series.min()
    max_val = series.max()
    
    # Correzione: se min==max, restituire [0.0] * len per evitare divisione per zero
    if max_val - min_val == 0:
        return pd.Series([0.0] * len(series))
    
    normalized = (series - min_val) / (max_val - min_val)
    return normalized


def calculate_value_index(row, price_threshold=1e18):
    """Calculate value index for a player.
    
    Value Index = (Score * Age Factor) / Price
    
    Args:
        row: DataFrame row containing player data
        price_threshold: Maximum price threshold to avoid division by zero
        
    Returns:
        float: Value index score
    """
    # Get score and age factor
    if "Defender Score" in row.index:
        score = row["Defender Score"]
    elif "Fullback Score" in row.index:
        score = row["Fullback Score"]
    else:
        score = 0
    
    # Calculate age factor (uniformato con altri moduli)
    age = row.get("_age", 25)
    if pd.isna(age):
        age_factor = 1.0
    elif age <= 23:
        age_factor = 1.2  # ≤23 anni
    elif age <= 27:
        age_factor = 1.0  # 24-27 anni
    elif age <= 30:
        age_factor = 0.8  # 28-30 anni
    else:
        age_factor = 0.6  # >30 anni
    
    # Get price (handle different column names)
    price_col = None
    for col in ["_price", "Guide Value", "Price"]:
        if col in row.index and pd.notna(row[col]):
            try:
                price = float(row[col])
                if price > 0:
                    price_col = col
                    break
            except (ValueError, TypeError):
                continue
    
    if price_col is None:
        return 0.0
    
    # Avoid division by zero
    price = min(float(row[price_col]), price_threshold)
    
    # Calculate value index
    if price > 0:
        return (score * age_factor) / price
    return 0.0


def scale_value_index_to_100(value_index_series):
    """Scale value index to 0-100 range preserving relative differences.
    
    Args:
        value_index_series: pandas Series of raw value indices
        
    Returns:
        pandas Series: Scaled values in range [0, 100]
    """
    if len(value_index_series) == 0:
        return pd.Series([0.0])
    
    # Find max for scaling
    max_val = value_index_series.max()
    if max_val <= 0:
        return pd.Series([0.0] * len(value_index_series))
    
    # Scale to 0-100
    scaled = (value_index_series / max_val) * 100
    return scaled


def compute_dimension_scores(df):
    """Compute tactical dimension scores for fullbacks.
    
    Args:
        df: DataFrame with player data
        
    Returns:
        DataFrame with dimension scores
    """
    dim_scores = pd.DataFrame()
    
    # Defensive dimension (tackles, interceptions, clearances)
    defensive_cols = ["Defensive Actions per 90", "Blocks per 90", "Pressures Attempted per 90"]
    available_def = {}
    for col in defensive_cols:
        if col in df.columns:
            available_def[col] = col
    
    if len(available_def) > 0:
        dim_scores["difensiva_score"] = df[list(available_def.keys())].mean(axis=1) * 10
    
    # Build-up dimension (progressive passes, xA, key passes)
    buildup_cols = ["xA per 90", "Key Passes per 90", "Progressive Passes per 90", "Progressive Pass %"]
    available_buildup = {}
    for col in buildup_cols:
        if col in df.columns:
            available_buildup[col] = col
    
    if len(available_buildup) > 0:
        dim_scores["costruzione_score"] = df[list(available_buildup.keys())].mean(axis=1) * 8
    
    # Pressing dimension (pressures, possession won)
    pressing_cols = ["Pressures Attempted per 90", "Possession Won per 90"]
    available_pressing = {}
    for col in pressing_cols:
        if col in df.columns:
            available_pressing[col] = col
    
    if len(available_pressing) > 0:
        dim_scores["pressing_score"] = df[list(available_pressing.keys())].mean(axis=1) * 10
    
    # Aerial dimension (header win %)
    aerial_cols = ["Header Win %"]
    available_aerial = {}
    for col in aerial_cols:
        if col in df.columns:
            available_aerial[col] = col
    
    if len(available_aerial) > 0:
        dim_scores["aerea_score"] = df[list(available_aerial.keys())].mean(axis=1) * 10
    
    # Attacking dimension (crosses, dribbles, goal contributions)
    attacking_cols = ["Crosses Completed", "Dribbles per 90", "Goal Contributions per 90", "xG per 90"]
    available_attacking = {}
    for col in attacking_cols:
        if col in df.columns:
            available_attacking[col] = col
    
    if len(available_attacking) > 0:
        dim_scores["attacco_score"] = df[list(available_attacking.keys())].mean(axis=1) * 8
    
    return dim_scores


def get_fullback_stats_mapping():
    """Return mapping of standard stat names to actual column names.
    
    Returns:
        dict: Mapping of standard names to actual column names
    """
    return {
        "Defensive Actions per 90": "Defensive Actions per 90",
        "Possession Won per 90": "Possession Won per 90",
        "Blocks per 90": "Blocks per 90",
        "Pressures Attempted per 90": "Pressures Attempted per 90",
        "xA per 90": "xA per 90",
        "Key Passes per 90": "Key Passes per 90",
        "Progressive Passes per 90": "Progressive Passes per 90",
        "Progressive Pass %": "Progressive Pass %",
        "Open Play Cross Completion %": "Open Play Cross Completion %",
        "Clear Cut Chances Created": "Clear Cut Chances Created",
        "Crosses Completed": "Crosses Completed",
        "Dribbles per 90": "Dribbles per 90",
        "Goal Contributions per 90": "Goal Contributions per 90",
        "xG per 90": "xG per 90",
        "xG Overperformance": "xG Overperformance",
        "Header Win %": "Header Win %",
        "Mistakes Leading to Goals": "Mistakes Leading to Goals"
    }
