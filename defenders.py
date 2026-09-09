#!/usr/bin/env python3
"""
Football Player Analysis Script for Identifying Best Value Defender Prospects

This script analyzes football player data to identify the best defender prospects 
to buy at low cost and flip for profit, with focus on defensive ability and build-up play.

Features:
- Reads CSV files with football player statistics
- Handles special formatting in Guide Value column (€, K, M)
- Calculates composite defender scores with weighted metrics specific to defenders
- Computes value index comparing defensive potential to price
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




def calculate_defender_score(row):
    """
    Calculate a composite score with weighted metrics for defenders.
    
    Defender weights (high impact, 0.5-3.0x):
    - Defensive Actions per 90 → 3.0x
    - Tackles per 90 → 2.5x
    - Interceptions per 90 → 2.5x
    - Possession Won per 90 → 2.0x
    - Clearances per 90 → 1.5x
    - Blocks per 90 → 1.5x
    - Pressures Attempted per 90 → 1.5x (aumentato per enfatizzare il pressing)
    
    Build-up weights (medium impact, 1.0-2.5x):
    - Progressive Passes per 90 → 2.5x
    - Key Passes per 90 → 2.0x
    - Creative Actions per 90 → 2.0x
    - Pass Completion % → 1.5x
    - Progressive Pass % → 1.5x
    - Passes Completed per 90 → 1.0x
    
    Other weights (low impact, 0.5-2.0x):
    - Goal Contributions per 90 → 2.0x
    - Average Rating → 1.5x
    - Header Win % → 1.5x
    - Dribbles per 90 → 0.5x
    
    Args:
        row: Pandas Series containing player data
        
    Returns:
        float: Composite defender score
    """
    
    # === DEFENSIVE METRICS (pesi elevati) ===
    defensive_actions_p90 = pd.to_numeric(row.get('Defensive Actions per 90', np.nan), errors='coerce')
    tackles_p90 = pd.to_numeric(row.get('Tackles per 90', np.nan), errors='coerce')
    interceptions_p90 = pd.to_numeric(row.get('Interceptions per 90', np.nan), errors='coerce')
    possession_won_p90 = pd.to_numeric(row.get('Possession Won per 90', np.nan), errors='coerce')
    clearances_p90 = pd.to_numeric(row.get('Clearances per 90', np.nan), errors='coerce')
    blocks_p90 = pd.to_numeric(row.get('Blocks per 90', np.nan), errors='coerce')
    pressures_attempted_p90 = pd.to_numeric(row.get('Pressures Attempted per 90', np.nan), errors='coerce')
    
    # === BUILD-UP METRICS (peso medio) ===
    progressive_passes_p90 = pd.to_numeric(row.get('Progressive Passes per 90', np.nan), errors='coerce')
    key_passes_p90 = pd.to_numeric(row.get('Key Passes per 90', np.nan), errors='coerce')
    creative_actions_p90 = pd.to_numeric(row.get('Creative Actions per 90', np.nan), errors='coerce')
    pass_completion_pct = pd.to_numeric(row.get('Pass Completion %', np.nan), errors='coerce')
    progressive_pass_pct = pd.to_numeric(row.get('Progressive Pass %', np.nan), errors='coerce')
    passes_completed_p90 = pd.to_numeric(row.get('Passes Completed per 90', np.nan), errors='coerce')
    
    # === OTHER METRICS (peso basso) ===
    goal_contributions_p90 = pd.to_numeric(row.get('Goal Contributions per 90', np.nan), errors='coerce')
    average_rating = pd.to_numeric(row.get('Average Rating', np.nan), errors='coerce')
    header_win_pct = pd.to_numeric(row.get('Header Win %', np.nan), errors='coerce')
    dribbles_p90 = pd.to_numeric(row.get('Dribbles per 90', np.nan), errors='coerce')
    
    # Initialize score with a base value of 0
    defender_score = 0.0
    
    # === DEFENSIVE WEIGHTS (elevati) ===
    if not pd.isna(defensive_actions_p90):
        defender_score += defensive_actions_p90 * 3.0
    if not pd.isna(tackles_p90):
        defender_score += tackles_p90 * 2.5
    if not pd.isna(interceptions_p90):
        defender_score += interceptions_p90 * 2.5
    if not pd.isna(possession_won_p90):
        defender_score += possession_won_p90 * 2.0
    if not pd.isna(clearances_p90):
        defender_score += clearances_p90 * 1.5
    if not pd.isna(blocks_p90):
        defender_score += blocks_p90 * 1.5
    if not pd.isna(pressures_attempted_p90):
        defender_score += pressures_attempted_p90 * 1.5  # Peso aumentato per enfatizzare il pressing difensivo
    
    # === BUILD-UP WEIGHTS (medio) ===
    if not pd.isna(progressive_passes_p90):
        defender_score += progressive_passes_p90 * 2.5
    if not pd.isna(key_passes_p90):
        defender_score += key_passes_p90 * 2.0
    if not pd.isna(creative_actions_p90):
        defender_score += creative_actions_p90 * 2.0
    if not pd.isna(pass_completion_pct):
        defender_score += pass_completion_pct * 1.5
    if not pd.isna(progressive_pass_pct):
        defender_score += progressive_pass_pct * 1.5
    if not pd.isna(passes_completed_p90):
        defender_score += passes_completed_p90 * 1.0
    
    # === OTHER WEIGHTS (basso) ===
    if not pd.isna(goal_contributions_p90):
        defender_score += goal_contributions_p90 * 2.0
    if not pd.isna(average_rating):
        defender_score += average_rating * 1.5
    # Header Win %: usato una sola volta per evitare duplicazione (peso uniforme)
    if not pd.isna(header_win_pct):
        defender_score += header_win_pct * 1.5
    
    if not pd.isna(dribbles_p90):
        defender_score += dribbles_p90 * 0.5
        
    return defender_score


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
    Calculate the value index comparing defender potential to price
    
    Value Index = (Defender Score * Age Factor) / Price
    
    Args:
        row: Pandas Series containing player data
        price_threshold: Maximum price threshold in Euros
        
    Returns:
        float: Value index for the player, or NaN if not valid
    """
    
    # Extract required values
    guide_value = row.get('Guide Value', np.nan)
    age = pd.to_numeric(row.get('Age', np.nan), errors='coerce')
    defender_score = row.get('Defender Score', np.nan)
    
    # Check if we have enough data to calculate value index
    if pd.isna(guide_value) or pd.isna(age) or pd.isna(defender_score):
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
        value_index = (defender_score * age_factor) / parsed_price 
        return value_index
    except ZeroDivisionError:
        return np.nan


def calculate_additional_metrics(row):
    """
    Calculate additional helpful metrics for defender analysis
    
    Args:
        row: Pandas Series containing player data
        
    Returns:
        dict with calculated metrics
    """
    
    # Initialize dictionary to hold results  
    metrics = {}
    
    # Defensive Efficiency = (Defensive Actions per 90) / (Tackles + Interceptions per 90)
    defensive_actions_p90 = pd.to_numeric(row.get('Defensive Actions per 90', np.nan), errors='coerce')
    tackles_p90 = pd.to_numeric(row.get('Tackles per 90', np.nan), errors='coerce')
    interceptions_p90 = pd.to_numeric(row.get('Interceptions per 90', np.nan), errors='coerce')
    
    if not pd.isna(defensive_actions_p90) and not pd.isna(tackles_p90) and not pd.isna(interceptions_p90):
        total_defensive = tackles_p90 + interceptions_p90
        if total_defensive != 0:
            metrics['Defensive Efficiency'] = defensive_actions_p90 / total_defensive
        else:
            metrics['Defensive Efficiency'] = np.nan
    else:  
        metrics['Defensive Efficiency'] = np.nan
        
    # Build-up Quality = (Progressive Passes per 90) / (Pass Completion %)
    progressive_passes_p90 = pd.to_numeric(row.get('Progressive Passes per 90', np.nan), errors='coerce')
    pass_completion_pct = pd.to_numeric(row.get('Pass Completion %', np.nan), errors='coerce')
    
    if not pd.isna(progressive_passes_p90) and not pd.isna(pass_completion_pct) and pass_completion_pct != 0:
        metrics['Build-up Quality'] = progressive_passes_p90 / (pass_completion_pct / 100)
    else:  
        metrics['Build-up Quality'] = np.nan
        
    return metrics


def process_football_data(input_file='defenders.csv', output_file='best_defender_prospects.csv'):
    """
    Main function to process defender player data
    
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
            
        # Check for defender stats columns specific to the role
        defender_stats = [
            'Defensive Actions per 90',
            'Tackles per 90',
            'Interceptions per 90',
            'Possession Won per 90',
            'Clearances per 90',
            'Blocks per 90',
            'Pressures Attempted per 90',
            'Progressive Passes per 90',
            'Key Passes per 90',
            'Creative Actions per 90',
            'Pass Completion %',
            'Progressive Pass %',
            'Passes Completed per 90',
            'Goal Contributions per 90',
            'Average Rating',
            'Header Win %',
            'Dribbles per 90'
        ]
        
        # Add more stats that might be present
        all_stats = [
            'Appearances'
        ] + defender_stats
        
        missing_cols = [col for col in all_stats if col not in df.columns]
        print(f"Missing defender stats columns: {missing_cols}")
        
        # Create a copy to avoid modifying the original
        df_processed = df.copy()
        
        # Convert Guide Value column to numeric 
        print("Processing Guide Value column...")
        df_processed['Guide Value Numeric'] = df_processed['Guide Value'].apply(parse_guide_value)
        
        # Calculate defender score for each player
        print("Calculating defender scores...")
        df_processed['Defender Score'] = df_processed.apply(calculate_defender_score, axis=1)
        
        # Normalize the defender scores using min-max scaling  
        print("Normalizing defender scores...")
        df_processed['Normalized Defender Score'] = min_max_normalize(df_processed['Defender Score'])
        
        # Calculate value index for each player
        print("Calculating value indices...")
        df_processed['Value Index'] = df_processed.apply(calculate_value_index, axis=1)
        
        # Apply additional metrics 
        print("Computing additional metrics...")
        additional_metrics = df_processed.apply(calculate_additional_metrics, axis=1)
        
        # Add calculated metrics back to dataframe
        for col in ['Defensive Efficiency', 'Build-up Quality']:
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
            'Defender Score', 'Value Index',
            'Defensive Actions per 90', 'Tackles per 90', 'Interceptions per 90',
            'Possession Won per 90', 'Clearances per 90', 'Blocks per 90',
            'Pressures Attempted per 90', 'Progressive Passes per 90', 'Key Passes per 90',
            'Creative Actions per 90', 'Pass Completion %', 'Progressive Pass %'
        ]
        
        # Add any additional columns that might be present
        available_cols = [col for col in output_cols if col in top_20_prospects.columns]
        
        print("\nTop 20 Defender Prospects:")
        print("-" * 60) 
        for index, row in top_20_prospects.iterrows():
            print(f"{row['Name']} ({row['Club']})")
            print(f"Age: {row.get('Age', 'N/A')}")
            print(f"Price: {row.get('Guide Value', 'N/A')}")
            print(f"Defender Score: {row.get('Defender Score', 'N/A'):.2f}")  
            print(f"Value Index: {row.get('Value Index', 'N/A'):.4f}")
            
            # Print defender stats if available
            defender_stats_to_show = ['Defensive Actions per 90', 'Tackles per 90', 'Interceptions per 90',
                                     'Possession Won per 90', 'Clearances per 90', 'Blocks per 90',
                                     'Pressures Attempted per 90', 'Progressive Passes per 90', 'Key Passes per 90',
                                     'Creative Actions per 90', 'Pass Completion %', 'Progressive Pass %']
            for stat in defender_stats_to_show:
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
    Compute dimension scores for defenders based on percentile rankings.
    
    Creates 5 new columns classifying playing style:
    - difensiva_score: Defensive ability
    - costruzione_score: Build-up/playmaking ability
    - pressing_score: Pressing intensity
    - aerea_score: Aerial ability
    - attacco_score: Overall attacking score
    
    Args:
        df: pandas.DataFrame with player statistics
        
    Returns:
        pandas.DataFrame: DataFrame with only the 5 dimension score columns
    """
    # Edge case: empty DataFrame
    if len(df) == 0:
        return pd.DataFrame(columns=[
            'difensiva_score', 'costruzione_score',
            'pressing_score', 'aerea_score', 'attacco_score'
        ])
    
    # Define dimensions with their metrics and weights (defender-specific)
    dimensions = {
        'difensiva': {
            'metrics': [
                ('Defensive Actions per 90', 3.0),
                ('Tackles per 90', 2.5),
                ('Interceptions per 90', 2.5),
                ('Possession Won per 90', 2.0),
                ('Clearances per 90', 1.5),
                ('Blocks per 90', 1.5)
            ]
        },
        'costruzione': {
            'metrics': [
                ('Progressive Passes per 90', 2.5),
                ('Key Passes per 90', 2.0),
                ('Creative Actions per 90', 2.0),
                ('Pass Completion %', 1.5),
                ('Progressive Pass %', 1.5),
                ('Passes Completed per 90', 1.0)
            ]
        },
        'pressing': {
            'metrics': [
                ('Pressures Attempted per 90', 1.0),
                ('Possession Won per 90', 0.6)
            ]
        },
        'aerea': {
            'metrics': [
                ('Header Win %', 1.5)
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
        for dim_name in ['difensiva', 'costruzione', 'pressing', 'aerea', 'attacco']:
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
    
    for dim_name in ['difensiva', 'costruzione', 'pressing', 'aerea']:
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
        
        # Special handling for aerea (Header Win %)
        if dim_name == 'aerea':
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
        result_data.get('difensiva_score'),
        result_data.get('costruzione_score'),
        result_data.get('pressing_score'),
        result_data.get('aerea_score')
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
        'difensiva_score': result_data.get('difensiva_score'),
        'costruzione_score': result_data.get('costruzione_score'),
        'pressing_score': result_data.get('pressing_score'),
        'aerea_score': result_data.get('aerea_score'),
        'attacco_score': result_data.get('attacco_score')
    })
    
    return result_df


# Entry point for the script
if __name__ == "__main__":
    """
    Main entry point of the script.
    
    Usage examples:
    - Run with default filenames:
        python defenders.py
        
    - Process a different file:
        python defenders.py input_file.csv output_file.csv
    """
    
    # Default filenames  
    input_filename = "defenders.csv" 
    output_filename = "best_defender_prospects.csv"
    
    # Check if command line arguments are provided
    if len(sys.argv) > 1:
        input_filename = sys.argv[1] 
        
    if len(sys.argv) > 2:  
        output_filename = sys.argv[2]
        
    print(f"Starting defender player analysis...")
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
