#!/usr/bin/env python3
"""
Advanced Weighted Scoring System for FM Scout Gem
Implements proper normalization and tactical-based weights.
"""

import pandas as pd
import numpy as np

def percentile_normalize(series, scale=100):
    """
    Normalize a series using percentile-based scoring.
    Converts raw values to 0-100 scale based on relative position in dataset.
    
    Args:
        series: pandas Series with raw values
        scale: Maximum value for output (default 100)
        
    Returns:
        pandas.Series: Normalized values between 0 and scale
    """
    if len(series) == 0 or series.nunique() <= 1:
        return pd.Series([50.0] * len(series), index=series.index)
    
    # Rank-based normalization (percentile)
    ranks = series.rank(pct=True)  # Percentile ranks (0 to 1)
    normalized = ranks * scale
    return normalized.fillna(50)


def calculate_cof_score_normalized(df):
    """
    Calculate normalized COF score with tactical weights.
    
    Creative weights (high importance for AM):
    - xA: 2.5 (primary creative metric)
    - Key Passes: 2.0 (direct chance creation)
    - Goal Contributions: 2.0 (end product)
    - Progressive Passes: 1.5 (build-up play)
    
    Finishing weights (moderate):
    - xG: 1.8 (expected goals)
    - NP-xG: 1.2 (non-penalty xG)
    - Shots on Target: 1.0
    - Dribbles: 1.4
    
    Defensive/pressing (low for AM):
    - Pressures: 0.3
    - Possession Won: 0.2
    """
    # Normalize each stat to 0-100 scale
    xa_norm = percentile_normalize(pd.to_numeric(df['xA per 90'], errors='coerce'))
    kp_norm = percentile_normalize(pd.to_numeric(df['Key Passes per 90'], errors='coerce'))
    gc_norm = percentile_normalize(pd.to_numeric(df['Goal Contributions per 90'], errors='coerce'))
    pp_norm = percentile_normalize(pd.to_numeric(df['Passaggi progressivi per 90'], errors='coerce'))
    xg_norm = percentile_normalize(pd.to_numeric(df['xG per 90'], errors='coerce'))
    npxg_norm = percentile_normalize(pd.to_numeric(df['NP-xG per 90'], errors='coerce'))
    sot_norm = percentile_normalize(pd.to_numeric(df['Shots on Target per 90'], errors='coerce'))
    drib_norm = percentile_normalize(pd.to_numeric(df['Dribbling completati per 90'], errors='coerce'))
    press_norm = percentile_normalize(pd.to_numeric(df['Pressures Attempted per 90'], errors='coerce'))
    poss_norm = percentile_normalize(pd.to_numeric(df['Possession Won per 90'], errors='coerce'))
    
    # Apply weights summing to ~10 for interpretability
    score = (
        xa_norm * 2.5 +
        kp_norm * 2.0 +
        gc_norm * 2.0 +
        pp_norm * 1.5 +
        xg_norm * 1.8 +
        npxg_norm * 1.2 +
        sot_norm * 1.0 +
        drib_norm * 1.4 +
        press_norm * 0.3 +
        poss_norm * 0.2
    ) / 13.0  # Normalize by sum of weights
    
    return score


def calculate_striker_score_normalized(df):
    """
    Calculate normalized Striker score.
    Focus on finishing and goal threat.
    """
    gc_norm = percentile_normalize(pd.to_numeric(df['Goal Contributions per 90'], errors='coerce'))
    xg_norm = percentile_normalize(pd.to_numeric(df['xG per 90'], errors='coerce'))
    npxg_norm = percentile_normalize(pd.to_numeric(df['NP-xG per 90'], errors='coerce'))
    sot_norm = percentile_normalize(pd.to_numeric(df['Shots on Target per 90'], errors='coerce'))
    shots_norm = percentile_normalize(pd.to_numeric(df['Shots per 90'], errors='coerce'))
    kp_norm = percentile_normalize(pd.to_numeric(df['Key Passes per 90'], errors='coerce'))
    xa_norm = percentile_normalize(pd.to_numeric(df['xA per 90'], errors='coerce'))
    press_norm = percentile_normalize(pd.to_numeric(df['Pressures Attempted per 90'], errors='coerce'))
    pass_norm = percentile_normalize(pd.to_numeric(df['Pass Completion %'], errors='coerce'))
    passaggi_norm = percentile_normalize(pd.to_numeric(df['Passaggi progressivi per 90'], errors='coerce'))
    poss_norm = percentile_normalize(pd.to_numeric(df['Possession Won per 90'], errors='coerce'))
    
    score = (
        gc_norm * 2.5 +
        xg_norm * 2.0 +
        npxg_norm * 1.5 +
        sot_norm * 1.5 +
        shots_norm * 1.0 +
        kp_norm * 1.0 +
        xa_norm * 1.0 +
        press_norm * 0.8 +
        pass_norm * 0.5 +
        passaggi_norm * 0.8 +
        poss_norm * 0.8
    ) / 12.4
    
    return score


def calculate_winger_score_normalized(df):
    """
    Calculate normalized Winger score.
    Balance of attacking and defensive contributions.
    """
    gc_norm = percentile_normalize(pd.to_numeric(df['Goal Contributions per 90'], errors='coerce'))
    xg_norm = percentile_normalize(pd.to_numeric(df['xG per 90'], errors='coerce'))
    xa_norm = percentile_normalize(pd.to_numeric(df['xA per 90'], errors='coerce'))
    npxg_norm = percentile_normalize(pd.to_numeric(df['NP-xG per 90'], errors='coerce'))
    drib_norm = percentile_normalize(pd.to_numeric(df['Dribbling completati per 90'], errors='coerce'))
    sot_norm = percentile_normalize(pd.to_numeric(df['Shots on Target per 90'], errors='coerce'))
    kp_norm = percentile_normalize(pd.to_numeric(df['Key Passes per 90'], errors='coerce'))
    actions_norm = percentile_normalize(pd.to_numeric(df['Attacking Actions per 90'], errors='coerce'))
    passaggi_norm = percentile_normalize(pd.to_numeric(df['Passaggi progressivi per 90'], errors='coerce'))
    cross_norm = percentile_normalize(pd.to_numeric(df['Cross riusciti per 90'], errors='coerce'))
    
    # Defensive contributions (lower weights)
    press_norm = percentile_normalize(pd.to_numeric(df['Pressures Attempted per 90'], errors='coerce'))
    poss_norm = percentile_normalize(pd.to_numeric(df['Possession Won per 90'], errors='coerce'))
    header_norm = percentile_normalize(pd.to_numeric(df['Header Win %'], errors='coerce'))
    
    score = (
        gc_norm * 2.0 +
        xg_norm * 2.0 +
        xa_norm * 2.0 +
        npxg_norm * 1.5 +
        drib_norm * 1.6 +
        sot_norm * 1.0 +
        kp_norm * 1.5 +
        actions_norm * 1.0 +
        passaggi_norm * 1.0 +
        cross_norm * 1.8 +
        press_norm * 0.4 +
        poss_norm * 0.3 +
        header_norm * 0.1
    ) / 15.2
    
    return score


def calculate_defensive_mid_score_normalized(df):
    """
    Calculate normalized Defensive Mid score.
    Focus on defensive actions and ball progression.
    """
    tackles_norm = percentile_normalize(pd.to_numeric(df['Tackles per 90'], errors='coerce'))
    interceptions_norm = percentile_normalize(pd.to_numeric(df['Interceptions per 90'], errors='coerce'))
    pass_norm = percentile_normalize(pd.to_numeric(df['Pass Completion %'], errors='coerce'))
    pp_norm = percentile_normalize(pd.to_numeric(df['Progressive Passes per 90'], errors='coerce'))
    press_norm = percentile_normalize(pd.to_numeric(df['Pressures Attempted per 90'], errors='coerce'))
    poss_norm = percentile_normalize(pd.to_numeric(df['Possession Won per 90'], errors='coerce'))
    header_norm = percentile_normalize(pd.to_numeric(df['Header Win %'], errors='coerce'))
    rating_norm = percentile_normalize(pd.to_numeric(df['Average Rating'], errors='coerce'))
    kp_norm = percentile_normalize(pd.to_numeric(df['Key Passes per 90'], errors='coerce'))
    blocked_norm = percentile_normalize(pd.to_numeric(df['Shots Blocked per 90'], errors='coerce'))
    mistakes_norm = percentile_normalize(pd.to_numeric(df['Mistakes Leading to Goals'], errors='coerce'))
    gc_norm = percentile_normalize(pd.to_numeric(df['Goal Contributions per 90'], errors='coerce'))
    
    # Mistakes are penalized (inverted)
    score = (
        tackles_norm * 2.0 +
        interceptions_norm * 1.8 +
        pass_norm * 1.2 +
        pp_norm * 1.0 +
        press_norm * 1.0 +
        poss_norm * 0.9 +
        header_norm * 1.0 +
        rating_norm * 0.8 +
        kp_norm * 0.2 +
        blocked_norm * 0.5 -
        mistakes_norm * 1.0 +
        gc_norm * 0.1
    ) / 10.0
    
    return score


def calculate_defender_score_normalized(df):
    """
    Calculate normalized Defender score.
    Balanced defensive and build-up contributions.
    """
    defensive_actions_norm = percentile_normalize(pd.to_numeric(df['Defensive Actions per 90'], errors='coerce'))
    tackles_norm = percentile_normalize(pd.to_numeric(df['Tackles per 90'], errors='coerce'))
    interceptions_norm = percentile_normalize(pd.to_numeric(df['Interceptions per 90'], errors='coerce'))
    poss_norm = percentile_normalize(pd.to_numeric(df['Possession Won per 90'], errors='coerce'))
    clearances_norm = percentile_normalize(pd.to_numeric(df['Clearances per 90'], errors='coerce'))
    blocks_norm = percentile_normalize(pd.to_numeric(df['Blocks per 90'], errors='coerce'))
    press_norm = percentile_normalize(pd.to_numeric(df['Pressures Attempted per 90'], errors='coerce'))
    pp_norm = percentile_normalize(pd.to_numeric(df['Progressive Passes per 90'], errors='coerce'))
    kp_norm = percentile_normalize(pd.to_numeric(df['Key Passes per 90'], errors='coerce'))
    creative_norm = percentile_normalize(pd.to_numeric(df['Creative Actions per 90'], errors='coerce'))
    pass_norm = percentile_normalize(pd.to_numeric(df['Pass Completion %'], errors='coerce'))
    prog_pass_norm = percentile_normalize(pd.to_numeric(df['Progressive Pass %'], errors='coerce'))
    passes_done_norm = percentile_normalize(pd.to_numeric(df['Passes Completed per 90'], errors='coerce'))
    gc_norm = percentile_normalize(pd.to_numeric(df['Goal Contributions per 90'], errors='coerce'))
    rating_norm = percentile_normalize(pd.to_numeric(df['Average Rating'], errors='coerce'))
    header_norm = percentile_normalize(pd.to_numeric(df['Header Win %'], errors='coerce'))
    drib_norm = percentile_normalize(pd.to_numeric(df['Dribbles per 90'], errors='coerce'))
    
    score = (
        defensive_actions_norm * 3.0 +
        tackles_norm * 2.5 +
        interceptions_norm * 2.5 +
        poss_norm * 2.0 +
        clearances_norm * 1.5 +
        blocks_norm * 1.5 +
        press_norm * 1.5 +
        pp_norm * 2.5 +
        kp_norm * 2.0 +
        creative_norm * 2.0 +
        pass_norm * 1.5 +
        prog_pass_norm * 1.5 +
        passes_done_norm * 1.0 +
        gc_norm * 2.0 +
        rating_norm * 1.5 +
        header_norm * 1.5 +
        drib_norm * 0.5
    ) / 30.0
    
    return score


def calculate_fullback_score_normalized(df):
    """
    Calculate normalized Fullback score.
    Balance of defensive solidity and attacking threat.
    """
    defensive_actions_norm = percentile_normalize(pd.to_numeric(df['Defensive Actions per 90'], errors='coerce'))
    poss_norm = percentile_normalize(pd.to_numeric(df['Possession Won per 90'], errors='coerce'))
    blocks_norm = percentile_normalize(pd.to_numeric(df['Blocks per 90'], errors='coerce'))
    press_norm = percentile_normalize(pd.to_numeric(df['Pressures Attempted per 90'], errors='coerce'))
    xa_norm = percentile_normalize(pd.to_numeric(df['xA per 90'], errors='coerce'))
    kp_norm = percentile_normalize(pd.to_numeric(df['Key Passes per 90'], errors='coerce'))
    pp_norm = percentile_normalize(pd.to_numeric(df['Progressive Passes per 90'], errors='coerce'))
    prog_pass_pct_norm = percentile_normalize(pd.to_numeric(df['Progressive Pass %'], errors='coerce'))
    cross_comp_norm = percentile_normalize(pd.to_numeric(df['Open Play Cross Completion %'], errors='coerce'))
    ccc_norm = percentile_normalize(pd.to_numeric(df['Clear Cut Chances Created'], errors='coerce'))
    crosses_norm = percentile_normalize(pd.to_numeric(df['Crosses Completed'], errors='coerce'))
    drib_norm = percentile_normalize(pd.to_numeric(df['Dribbles per 90'], errors='coerce'))
    gc_norm = percentile_normalize(pd.to_numeric(df['Goal Contributions per 90'], errors='coerce'))
    xg_norm = percentile_normalize(pd.to_numeric(df['xG per 90'], errors='coerce'))
    xg_over_norm = percentile_normalize(pd.to_numeric(df['xG Overperformance'], errors='coerce'))
    header_norm = percentile_normalize(pd.to_numeric(df['Header Win %'], errors='coerce'))
    mistakes_norm = percentile_normalize(pd.to_numeric(df['Mistakes Leading to Goals'], errors='coerce'))
    
    score = (
        defensive_actions_norm * 2.8 +
        poss_norm * 2.2 +
        blocks_norm * 1.8 +
        press_norm * 1.5 +
        xa_norm * 2.5 +
        kp_norm * 2.5 +
        pp_norm * 2.0 +
        prog_pass_pct_norm * 2.5 +
        cross_comp_norm * 1.8 +
        ccc_norm * 2.0 +
        crosses_norm * 2.5 +
        drib_norm * 1.5 +
        gc_norm * 1.5 +
        xg_norm * 1.0 +
        xg_over_norm * 0.5 +
        header_norm * 2.0 -
        mistakes_norm * 2.0
    ) / 30.6
    
    return score


def calculate_goalkeeper_score_normalized(df):
    """
    Calculate normalized Goalkeeper score.
    Shot-stopping + distribution + claiming.
    """
    save_norm = percentile_normalize(pd.to_numeric(df['Save Percentage %'], errors='coerce'))
    clean_norm = percentile_normalize(pd.to_numeric(df['Clean Sheets %'], errors='coerce'))
    # Goals conceded inverted (lower is better)
    gc_norm = 100 - percentile_normalize(pd.to_numeric(df['Goals Conceded per 90'], errors='coerce'))
    saves_norm = percentile_normalize(pd.to_numeric(df['Saves per 90'], errors='coerce'))
    pass_norm = percentile_normalize(pd.to_numeric(df['Pass Completion %'], errors='coerce'))
    pp_norm = percentile_normalize(pd.to_numeric(df['Progressive Passes per 90'], errors='coerce'))
    dist_norm = percentile_normalize(pd.to_numeric(df['Distribution Accuracy %'], errors='coerce'))
    crosses_norm = percentile_normalize(pd.to_numeric(df['Crosses Claimed %'], errors='coerce'))
    high_norm = percentile_normalize(pd.to_numeric(df['High Claims per 90'], errors='coerce'))
    sweeper_norm = percentile_normalize(pd.to_numeric(df['Sweeper Actions per 90'], errors='coerce'))
    
    score = (
        save_norm * 3.0 +
        clean_norm * 2.5 +
        gc_norm * 2.0 +
        saves_norm * 1.5 +
        pass_norm * 1.5 +
        pp_norm * 1.0 +
        dist_norm * 1.0 +
        crosses_norm * 0.6 +
        high_norm * 0.8 +
        sweeper_norm * 1.0
    ) / 15.9
    
    return score


def calculate_age_factor(age):
    """Calculate age factor to reward younger players."""
    if pd.isna(age) or age < 0:
        return 1.0
    if age <= 20:
        return 2.0
    elif age <= 23:
        return 1.6
    elif age <= 26:
        return 1.3
    else:
        return 1.0


def calculate_value_index_normalized(df, role_score_col, price_col='_price', age_col='_age'):
    """
    Calculate Value Index using normalized scores.
    Value Index = (Score * Age Factor) / Price
    """
    age_factor = df[age_col].apply(calculate_age_factor)
    price = pd.to_numeric(df[price_col], errors='coerce')
    price = price.replace(0, float('inf'))  # Avoid division by zero
    
    # Calculate raw value index
    value_index = (df[role_score_col] * age_factor) / (price / 1_000_000)
    
    # Normalize to 0-100 scale
    value_index = percentile_normalize(value_index, scale=100)
    
    return value_index


# Test the system
if __name__ == '__main__':
    # Create sample data for testing
    np.random.seed(42)
    n = 100
    
    test_df = pd.DataFrame({
        'Name': [f'Player_{i}' for i in range(n)],
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
        'Age': np.random.randint(18, 32, n),
        '_price': np.random.uniform(1_000_000, 50_000_000, n)
    })
    
    # Apply normalized scoring
    test_df['_cof_score'] = calculate_cof_score_normalized(test_df)
    test_df['_value_index'] = calculate_value_index_normalized(test_df, '_cof_score')
    
    print("Top 5 players by Value Index:")
    print(test_df.nlargest(5, '_value_index')[['Name', 'xA per 90', 'Key Passes per 90', 'Goal Contributions per 90', '_cof_score', '_value_index']])
    print(f"\nScore range: {test_df['_cof_score'].min():.2f} - {test_df['_cof_score'].max():.2f}")
    print(f"VI range: {test_df['_value_index'].min():.2f} - {test_df['_value_index'].max():.2f}")
