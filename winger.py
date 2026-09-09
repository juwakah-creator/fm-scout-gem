#!/usr/bin/env python3
"""
Football Player Analysis Script for Identifying Best Value Prospects

This script analyzes football player data to identify the best prospects to buy at low cost 
and flip for profit, with focus on offensive performance.

Features:
- Reads CSV files with football player statistics
- Handles special formatting in Guide Value column (€, K, M)
- Calculates composite offensive scores with weighted metrics
- Computes value index comparing offensive potential to price
- Filters players based on criteria (price, appearances, age)
- Outputs top prospects sorted by value index

Author: [Your Name]
Date: [Current Date]
"""

import pandas as pd
import numpy as np
from typing import Optional
import os
import sys


def parse_guide_value(value):
    """
    Parse the Guide Value column which may contain '€', 'K' (thousands), or 'M' (millions)
    
    Args:
        value: String containing guide value
        
    Returns:
        float: Numeric representation of the value, or NaN if invalid
    """
    if pd.isna(value) or value == '' or value is None:
        return np.nan
    
    # Remove € symbol and spaces
    cleaned_value = str(value).strip().replace('€', '').replace(' ', '')
    
    try:
        # Handle 'K' for thousands (e.g., 25K becomes 25000)
        if cleaned_value.endswith('K'):
            return float(cleaned_value[:-1]) * 1000
        # Handle 'M' for millions (e.g., 3.5M becomes 3500000)  
        elif cleaned_value.endswith('M'):
            return float(cleaned_value[:-1]) * 1000000
        # Handle direct numeric values
        else:
            return float(cleaned_value)
    except ValueError:
        print(f"Warning: Could not parse Guide Value '{value}'")
        return np.nan


def calculate_age_factor(age):
    """
    Calculate age factor - younger players get MUCH higher value
    Players under 23 get maximum bonus (2.0x), then gradually decreases until 27
    This strongly favors young players with good stats and low value
    
    Args:
        age: Player's age
        
    Returns:
        float: Age factor (1.0-2.0, much higher for younger players)
    """
    if pd.isna(age):
        return 1.0
    
    age = float(age)
    
    # Players under 23 get maximum bonus (2.0x) - STRONG YOUTH BONUS
    if age < 23:
        return 2.0
    # Players 23-27 get gradual decrease from 2.0 to 1.0
    elif age < 27:
        return 2.0 - ((age - 23) / 4) * 1.0
    # Players 27+ get standard factor (1.0)
    else:
        return 1.0




def calculate_offensive_score(row):
    """
    Calculate a composite score with weighted metrics for both offense and defense.
    
    Offensive weights (high impact, 0.5-2.0x):
    - Goal Contributions / 90 → 2.0x
    - xG / 90 → 2.0x (uniformato tra le funzioni)
    - xA / 90 → 2.0x
    - NP-xG / 90 → 1.5x
    - Dribbling completati / 90 → 1.6x [AUMENTATO da 1.2 a 1.6]
    - Shots on Target / 90 → 1.0x
    - Key Passes / 90 → 1.5x [UNIFORMATO e AUMENTATO da 1.0 a 1.5]
    - Attacking Actions / 90 → 1.0x
    - Passaggi progressivi / 90 → 1.0x [NUOVA]
    - Cross riusciti / 90 → 1.8x [AUMENTATO da 1.0 a 1.8]
    - xG Overperformance → 0.5x (ridotto da 2.0 a 0.5)
    
    Defensive weights (moderate/low impact, 0.1-0.4x):
    - Pressures Attempted / 90 → 0.4x [NUOVA]
    - Possession Won / 90 → 0.3x [NUOVA]
    - Pressing Efficiency → 0.2x [NUOVA]
    - Header Win % → 0.1x
    
    Args:
        row: Pandas Series containing player data
        
    Returns:
        float: Composite score (offensive + defensive)
    """
    
    # === OFFENSIVE METRICS (pesi elevati) ===
    goal_contributions_p90 = row.get('Goal Contributions per 90', np.nan)
    xg_p90 = row.get('xG per 90', np.nan)
    xa_p90 = row.get('xA per 90', np.nan)
    np_xg_p90 = row.get('NP-xG per 90', np.nan)
    dribbling_p90 = row.get('Dribbling completati per 90', np.nan)
    shots_targeted_p90 = row.get('Shots on Target per 90', np.nan)
    key_passes_p90 = row.get('Key Passes per 90', np.nan)
    attacking_actions_p90 = row.get('Attacking Actions per 90', np.nan)
    passaggi_progressivi_p90 = row.get('Passaggi progressivi per 90', np.nan)
    cross_riusciti_p90 = row.get('Cross riusciti per 90', np.nan)
    xg_overperformance = row.get('xG Overperformance', np.nan)
    
    # === DEFENSIVE METRICS (pesi moderati/bassi) ===
    pressures_attempted_p90 = row.get('Pressures Attempted per 90', np.nan)
    possession_won_p90 = row.get('Possession Won per 90', np.nan)
    pressing_efficiency = row.get('Pressing Efficiency', np.nan)
    header_win_pct = row.get('Header Win %', np.nan)
    
    # Initialize score with a base value of 0
    offensive_score = 0.0
    
    # === OFFENSIVE WEIGHTS (elevati) ===
    if not pd.isna(goal_contributions_p90):
        offensive_score += goal_contributions_p90 * 2.0
    if not pd.isna(xg_p90):
        offensive_score += xg_p90 * 2.0
    if not pd.isna(xa_p90):
        offensive_score += xa_p90 * 2.0
    if not pd.isna(np_xg_p90):
        offensive_score += np_xg_p90 * 1.5
    
    # Metriche con peso aumentato (1.6x per dribbling, 1.5x per key passes)
    if not pd.isna(dribbling_p90):
        offensive_score += dribbling_p90 * 1.6  # Aumentato da 1.2 a 1.6
    if not pd.isna(shots_targeted_p90):
        offensive_score += shots_targeted_p90 * 1.0
    if not pd.isna(key_passes_p90):
        offensive_score += key_passes_p90 * 1.5  # Uniformato e aumentato da 1.0 a 1.5
    if not pd.isna(attacking_actions_p90):
        offensive_score += attacking_actions_p90 * 1.0
    if not pd.isna(passaggi_progressivi_p90):
        offensive_score += passaggi_progressivi_p90 * 1.0  # [NUOVA]
    if not pd.isna(cross_riusciti_p90):
        offensive_score += cross_riusciti_p90 * 1.8  # Aumentato da 1.0 a 1.8 per enfatizzare i cross
    
    # xG Overperformance: ridotto da 2.0 a 0.5 per evitare rumore statistico
    if not pd.isna(xg_overperformance) and xg_overperformance > 0:
        offensive_score += xg_overperformance * 0.5  # Aggiornato da 2.0 a 0.5
    
    # === DEFENSIVE WEIGHTS (moderati/bassi) ===
    if not pd.isna(pressures_attempted_p90):
        offensive_score += pressures_attempted_p90 * 0.4  # [NUOVA]
    if not pd.isna(possession_won_p90):
        offensive_score += possession_won_p90 * 0.3  # [NUOVA]
    if not pd.isna(pressing_efficiency):
        offensive_score += pressing_efficiency * 0.2  # [NUOVA]
    if not pd.isna(header_win_pct):
        offensive_score += header_win_pct * 0.1  # Esistente (nuova categoria)
        
    return offensive_score


def min_max_normalize(series):
    """
    Normalize a series using min-max scaling (0-1 range)
    
    Args:
        series: Pandas Series to normalize
        
    Returns:
        pandas.Series: Normalized values between 0 and 1
    """
    # Handle edge cases where all values are the same or series is empty 
    if len(series) == 0 or series.min() == series.max():
        return pd.Series([0.0] * len(series), index=series.index)
    
    normalized = (series - series.min()) / (series.max() - series.min())
    # Ensure any NaN values remain as NaN
    return normalized.fillna(0)


def scale_value_index_to_100(series):
    """
    Scale Value Index values from their raw range to a 0-100 scale.
    
    This function preserves relative differences between players while
    mapping the distribution uniformly across the 0-100 range.
    
    Args:
        series: Pandas Series containing raw Value Index values
        
    Returns:
        pandas.Series: Scaled values between 0 and 100
    """
    # Handle edge cases where all values are the same or series is empty
    if len(series) == 0 or series.min() == series.max():
        return pd.Series([50.0] * len(series), index=series.index)
    
    # Min-max normalize to 0-1 range, then scale to 0-100
    normalized = (series - series.min()) / (series.max() - series.min())
    scaled = normalized * 100
    # Ensure any NaN values remain as NaN
    return scaled.fillna(0)


def calculate_value_index(row, price_threshold=5000000):
    """
    Calculate the value index comparing offensive potential to price
    
    Value Index = (Offensive Score * Age Factor) / Price
    
    Args:
        row: Pandas Series containing player data
        price_threshold: Maximum price threshold in Euros
        
    Returns:
        float: Value index for the player, or NaN if not valid
    """
    
    # Extract required values
    guide_value = row.get('Guide Value', np.nan)
    age = row.get('Age', np.nan)
    offensive_score = row.get('Offensive Score', np.nan) 
    
    # Check if we have enough data to calculate value index
    if pd.isna(guide_value) or pd.isna(age) or pd.isna(offensive_score):
        return np.nan
        
    # Convert guide value to numeric and validate price threshold  
    parsed_price = parse_guide_value(guide_value)
    
    # Check if player meets price criteria (below threshold)
    if pd.isna(parsed_price) or parsed_price > price_threshold:
        return np.nan
    
    # Calculate age factor
    age_factor = calculate_age_factor(age)
    
    # Avoid division by zero
    if parsed_price <= 0:
        return np.nan
        
    # Calculate value index: higher is better (better performance per unit cost)
    try:
        value_index = (offensive_score * age_factor) / parsed_price 
        return value_index
    except ZeroDivisionError:
        return np.nan


def calculate_additional_metrics(row):
    """
    Calculate additional helpful metrics for player analysis
    
    Args:
        row: Pandas Series containing player data
        
    Returns:
        dict with calculated metrics
    """
    
    # Initialize dictionary to hold results  
    metrics = {}
    
    # Offensive Efficiency = (Goal Contributions per 90) / (Shots per 90)
    goal_contributions_p90 = row.get('Goal Contributions per 90', np.nan)
    shots_p90 = row.get('Shots per 90', np.nan)
    
    if not pd.isna(goal_contributions_p90) and not pd.isna(shots_p90) and shots_p90 != 0:
        metrics['Offensive Efficiency'] = goal_contributions_p90 / shots_p90
    else:  
        metrics['Offensive Efficiency'] = np.nan
        
    # Growth Potential - player may be lucky with high xG but low overperformance 
    xg_p90 = row.get('xG per 90', np.nan)
    xg_overperformance = row.get('xG Overperformance', np.nan)
    
    if not pd.isna(xg_p90) and not pd.isna(xg_overperformance):
        # If player has high expected goals but negative overperformance, 
        # they might be underperforming due to luck
        metrics['Growth Potential'] = xg_p90 if (xg_p90 > 0 and xg_overperformance < 0) else 0.0  
    else:
        metrics['Growth Potential'] = np.nan
        
    return metrics


def process_football_data(input_file='strika.csv', output_file='best_prospects.csv'):
    """
    Main function to process football player data
    
    Args:
        input_file: Path to the CSV file with player data
        output_file: Path where results will be saved  
        
    Returns:
        pandas.DataFrame: Processed and filtered best prospects
    """ 
    
    try:
        # Read the CSV file
        print(f"Reading data from {input_file}...")
        df = pd.read_csv(input_file)
        print(f"Successfully read {len(df)} rows of player data")
        
        # Check if required columns are present
        expected_columns = ['Name', 'Club', 'Age', 'Guide Value']
        missing_cols = [col for col in expected_columns if col not in df.columns]
        
        if missing_cols:
            print(f"Warning: Missing expected columns: {missing_cols}")
            return None
            
        # Check for offensive stats columns
        offensive_stats = [
            'Goal Contributions per 90',
            'xG per 90',
            'xA per 90',
            'Shots on Target per 90',
            'Key Passes per 90',
            'Attacking Actions per 90',
            'NP-xG per 90',
            'xG Overperformance',
            'Dribbling completati per 90',      # [NUOVA]
            'Passaggi progressivi per 90',      # [NUOVA]
            'Cross riusciti per 90'             # [NUOVA]
        ]
        
        # Defensive stats columns (nuovo sistema di pesi)
        defensive_stats = [
            'Pressures Attempted per 90',       # [NUOVA]
            'Possession Won per 90',            # [NUOVA]
            'Pressing Efficiency',              # [NUOVA]
            'Header Win %'                      # Esistente (nuova categoria)
        ]
        
        # Add more stats that might be present
        all_stats = [
            'Appearances',
            'Shots per 90'
        ] + offensive_stats + defensive_stats
        
        missing_offensive_cols = [col for col in all_stats if col not in df.columns]
        print(f"Missing offensive stats columns: {missing_offensive_cols}")
        
        # Create a copy to avoid modifying the original
        df_processed = df.copy()
        
        # Convert Guide Value column to numeric 
        print("Processing Guide Value column...")
        df_processed['Guide Value Numeric'] = df_processed['Guide Value'].apply(parse_guide_value)
        
        # Calculate offensive score for each player
        print("Calculating offensive scores...")
        df_processed['Offensive Score'] = df_processed.apply(calculate_offensive_score, axis=1)
        
        # Normalize the offensive scores using min-max scaling  
        print("Normalizing offensive scores...")
        df_processed['Normalized Offensive Score'] = min_max_normalize(df_processed['Offensive Score'])
        
        # Calculate value index for each player
        print("Calculating value indices...")
        df_processed['Value Index'] = df_processed.apply(calculate_value_index, axis=1)
        
        # Apply additional metrics 
        print("Computing additional metrics...")
        additional_metrics = df_processed.apply(calculate_additional_metrics, axis=1)
        
        # Add calculated metrics back to dataframe
        for col in ['Offensive Efficiency', 'Growth Potential']:
            if col in additional_metrics.iloc[0]:  # Check if metric was computed 
                df_processed[col] = [m.get(col, np.nan) for m in additional_metrics]
                
        # Filter players based on criteria:
        # - Price below €5M (or customizable threshold)
        # - At least 10 appearances  
        # - Age under 30 years
        
        price_threshold = 5000000  # €5 million
        min_appearence = 10 
        max_age = 30
        
        print(f"Filtering players with:")
        print(f"- Price below {price_threshold:,} Euros")
        print(f"- At least {min_appearence} appearances")
        print(f"- Age under {max_age} years")
        
        # Apply filters
        filtered_df = df_processed.copy()
        
        # Filter by price (if we have parsed values)
        if 'Guide Value Numeric' in filtered_df.columns:
            price_mask = ~pd.isna(filtered_df['Guide Value Numeric']) & \
                         (filtered_df['Guide Value Numeric'] <= price_threshold)  
            filtered_df = filtered_df[price_mask] 
            
        # Filter by appearances
        if 'Appearances' in filtered_df.columns:
            appearance_mask = (~pd.isna(filtered_df['Appearances'])) & (filtered_df['Appearances'] >= min_appearence)
            filtered_df = filtered_df[appearance_mask]
        
        # Filter by age
        if 'Age' in filtered_df.columns:
            age_mask = (~pd.isna(filtered_df['Age'])) & (filtered_df['Age'] < max_age)
            filtered_df = filtered_df[age_mask]
        
        print(f"Found {len(filtered_df)} players meeting criteria")
        
        # Sort by value index descending
        sorted_df = filtered_df.sort_values(by='Value Index', ascending=False, na_position='last')
        
        # Select top 20 prospects  
        top_20_prospects = sorted_df.head(20)
        
        if len(top_20_prospects) == 0:
            print("Warning: No players meet all criteria")
            return None
        
        # Prepare output columns
        output_cols = [
            'Name', 'Club', 'Age', 'Guide Value',
            'Offensive Score', 'Value Index',
            'Goal Contributions per 90', 'xG per 90', 'xA per 90', 'Shots on Target per 90',
            'Dribbling completati per 90',      # [NUOVA]
            'Passaggi progressivi per 90',      # [NUOVA]
            'Cross riusciti per 90'             # [NUOVA]
        ]
        
        # Add defensive columns if present
        defensive_output_cols = [
            'Pressures Attempted per 90',       # [NUOVA]
            'Possession Won per 90',            # [NUOVA]
            'Pressing Efficiency',              # [NUOVA]
            'Header Win %'                      # Esistente (nuova categoria)
        ]
        
        # Add any additional columns that might be present
        available_cols = [col for col in output_cols if col in top_20_prospects.columns]
        
        print("\nTop 20 Prospects:")
        print("-" * 60) 
        for index, row in top_20_prospects.iterrows():
            print(f"{row['Name']} ({row['Club']})")
            print(f"Age: {row.get('Age', 'N/A')}")
            print(f"Price: {row.get('Guide Value', 'N/A')}")
            print(f"Offensive Score: {row.get('Offensive Score', 'N/A'):.2f}")  
            print(f"Value Index: {row.get('Value Index', 'N/A'):.4f}")
            
            # Print additional stats if available
            offensive_stats_to_show = ['Goal Contributions per 90', 'xG per 90',
                                     'xA per 90', 'Shots on Target per 90',
                                     'Dribbling completati per 90',      # [NUOVA]
                                     'Passaggi progressivi per 90',      # [NUOVA]
                                     'Cross riusciti per 90']            # [NUOVA]
            for stat in offensive_stats_to_show:
                value = row.get(stat, 'N/A')
                if not isinstance(value, str) and pd.notna(value):
                    print(f"{stat}: {value:.2f}")
                elif isinstance(value, str) and value != 'N/A':
                    print(f"{stat}: {value}")
            # Print defensive stats if available
            defensive_stats_to_show = ['Pressures Attempted per 90',      # [NUOVA]
                                       'Possession Won per 90',           # [NUOVA]
                                       'Pressing Efficiency',             # [NUOVA]
                                       'Header Win %']                    # Esistente (nuova categoria)
            for stat in defensive_stats_to_show:
                value = row.get(stat, 'N/A')
                if not isinstance(value, str) and pd.notna(value):
                    print(f"{stat}: {value:.2f}")
                elif isinstance(value, str) and value != 'N/A':
                    print(f"{stat}: {value}")
            print("-" * 30)
        
        # Save to CSV
        output_cols_to_save = [col for col in output_cols if col in top_20_prospects.columns]
        final_df = top_20_prospects[output_cols_to_save]
        
        try:
            final_df.to_csv(output_file, index=False)  
            print(f"\nResults saved to {output_file}")
        except Exception as e:
            print(f"Warning: Could not save results to CSV: {e}")
            
        return top_20_prospects
        
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
        return None
    except pd.errors.EmptyDataError:
        print("Error: CSV file is empty") 
        return None  
    except Exception as e:
        print(f"Unexpected error processing data: {e}")
        return None


def compute_dimension_scores(df):
    """
    Compute dimension scores for wingers based on percentile rankings.
    
    Creates 5 new columns classifying playing style:
    - finalizzazione_score: Finishing ability
    - creazione_score: Creative/playmaking ability
    - pressing_score: Pressing intensity
    - difesa_aerea_score: Aerial defense ability
    - attacco_score: Overall attacking score
    
    Args:
        df: pandas.DataFrame with player statistics
        
    Returns:
        pandas.DataFrame: DataFrame with only the 5 dimension score columns
    """
    # Edge case: empty DataFrame
    if len(df) == 0:
        return pd.DataFrame(columns=[
            'finalizzazione_score', 'creazione_score',
            'pressing_score', 'difesa_aerea_score', 'attacco_score'
        ])
    
    # Define dimensions with their metrics and weights
    dimensions = {
        'finalizzazione': {
            'metrics': [
                ('Goal Contributions per 90', 2.0),
                ('xG per 90', 1.5),
                ('Shots on Target per 90', 1.0),
                ('xG Overperformance', 0.5)
            ]
        },
        'creazione': {
            'metrics': [
                ('xA per 90', 2.0),
                ('Key Passes per 90', 1.5),
                ('Passaggi progressivi per 90', 1.0)
            ]
        },
        'pressing': {
            'metrics': [
                ('Pressures Attempted per 90', 1.0),
                ('Possession Won per 90', 1.0)
            ]
        },
        'difesa_aerea': {
            'metrics': [
                ('Header Win %', 1.0)
            ],
            'default_value': 50.0
        }
    }
    
    # Collect all metric columns that exist in the DataFrame
    all_metric_cols = set()
    for dim_config in dimensions.values():
        for metric_name, _ in dim_config['metrics']:
            if metric_name in df.columns:
                all_metric_cols.add(metric_name)
    
    # If no metrics at all, return NaN for all scores
    if not all_metric_cols:
        result_data = {}
        for dim_name in ['finalizzazione', 'creazione', 'pressing', 'difesa_aerea', 'attacco']:
            result_data[dim_name + '_score'] = pd.Series(np.nan, index=df.index)
        return pd.DataFrame(result_data)
    
    # Calculate percentiles for all metrics across the population
    percentile_cols = {}
    for dim_name, dim_config in dimensions.items():
        for metric_name, _ in dim_config['metrics']:
            if metric_name in df.columns:
                col_data = df[metric_name].copy()
                # Exclude NaN values for ranking
                valid_mask = col_data.notna()
                # Calculate percentile using rank(pct=True) * 100
                percentiles = pd.Series(np.nan, index=df.index)
                if valid_mask.any():
                    ranked = col_data[valid_mask].rank(pct=True) * 100
                    percentiles[valid_mask] = ranked
                percentile_cols[metric_name] = percentiles
    
    # Compute scores for each dimension
    result_data = {}
    
    for dim_name in ['finalizzazione', 'creazione', 'pressing', 'difesa_aerea']:
        dim_config = dimensions[dim_name]
        metrics = dim_config['metrics']
        
        # Collect valid percentiles and their original weights
        valid_percentiles = []
        valid_weights = []
        
        for metric_name, weight in metrics:
            if metric_name in percentile_cols:
                pct = percentile_cols[metric_name].copy()
                valid_percentiles.append(pct)
                valid_weights.append(weight)
        
        # Special handling for difesa_aerea (Header Win %)
        if dim_name == 'difesa_aerea':
            header_col = 'Header Win %'
            if header_col in df.columns:
                header_data = df[header_col].fillna(50.0)
                valid_mask = header_data.notna()
                if valid_mask.any():
                    percentiles_header = header_data.rank(pct=True) * 100
                    result_data[dim_name + '_score'] = percentiles_header.round(2)
                else:
                    # All values are NaN, use default 50 for all rows
                    result_data[dim_name + '_score'] = pd.Series(50.0, index=df.index).round(2)
            else:
                # Column doesn't exist but other metrics do - use default 50 for all rows
                result_data[dim_name + '_score'] = pd.Series(50.0, index=df.index).round(2)
            continue
        
        # Check if any metrics are available
        if not valid_percentiles:
            result_data[dim_name + '_score'] = pd.Series(np.nan, index=df.index)
            continue
        
        # Normalize weights so they sum to 1
        total_weight = sum(valid_weights)
        normalized_weights = [w / total_weight for w in valid_weights]
        
        # Calculate weighted score
        score = pd.Series(0.0, index=df.index)
        for pct, nw in zip(valid_percentiles, normalized_weights):
            score += pct * nw
        
        result_data[dim_name + '_score'] = score.round(2)
    
    # Calculate attacco_score as average of the other four
    attack_components = [
        result_data.get('finalizzazione_score'),
        result_data.get('creazione_score'),
        result_data.get('pressing_score'),
        result_data.get('difesa_aerea_score')
    ]
    
    # Filter out None values and calculate mean
    valid_scores = [s for s in attack_components if s is not None]
    if valid_scores:
        attacco_score = pd.concat(valid_scores, axis=1).mean(axis=1)
        result_data['attacco_score'] = attacco_score.round(2)
    else:
        # All scores are NaN (no metrics available), create a Series of NaN values
        result_data['attacco_score'] = pd.Series(np.nan, index=df.index)
    
    # Create result DataFrame with only the 5 score columns
    result_df = pd.DataFrame({
        'finalizzazione_score': result_data.get('finalizzazione_score'),
        'creazione_score': result_data.get('creazione_score'),
        'pressing_score': result_data.get('pressing_score'),
        'difesa_aerea_score': result_data.get('difesa_aerea_score'),
        'attacco_score': result_data.get('attacco_score')
    })
    
    return result_df


# Entry point for the script
if __name__ == "__main__":
    """
    Main entry point of the script.
    
    Usage examples:
    - Run with default filenames:
        python winger.py
        
    - Process a different file:
        python winger.py input_file.csv output_file.csv
    """
    
    # Default filenames  
    input_filename = "strika.csv" 
    output_filename = "best_prospects.csv"
    
    # Check if command line arguments are provided
    if len(sys.argv) > 1:
        input_filename = sys.argv[1] 
        
    if len(sys.argv) > 2:  
        output_filename = sys.argv[2]
        
    print(f"Starting football player analysis...")
    print(f"Input file: {input_filename}")
    print(f"Output file: {output_filename}") 
    
    # Process the data
    result_df = process_football_data(input_file=input_filename, 
                                       output_file=output_filename)
    
    if result_df is not None:
        print("\nAnalysis complete!")
        
    else:
        print("\nError occurred during analysis.")
        sys.exit(1) 
