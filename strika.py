#!/usr/bin/env python3
"""
Football Player Analysis Script for Identifying Best Value Striker Prospects

This script analyzes football player data to identify the best striker prospects 
to buy at low cost and flip for profit, with focus on finishing ability and goal threat.

Features:
- Reads CSV files with football player statistics
- Handles special formatting in Guide Value column (€, K, M)
- Calculates composite striker scores with weighted metrics specific to strikers
- Computes value index comparing attacking potential to price
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
from scoring_v2_integration import calculate_score_percentile, calculate_value_index, parse_guide_value


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
    Calculate age factor to reward younger players more heavily
    
    Args:
        age: Player's age
        
    Returns:
        float: Age multiplier (higher for younger players)
    """
    if pd.isna(age) or age < 0:
        return 1.0
    
    # Apply different factors based on age groups
    if age <= 20:
        return 2.0  # Youngest players get highest reward
    elif 20 < age <= 23:
        return 1.6  # Early 20s get high reward
    elif 24 <= age <= 26:
        return 1.3  # Mid-20s get moderate reward  
    else:
        return 1.0  # Older players get no bonus


def calculate_striker_score(df):
    """
    Calculate percentile-based striker score using scoring_v2_integration.
    
    Args:
        df: DataFrame con stats dei giocatori
    
    Returns:
        pandas.Series: Punteggio striker normalizzato 0-100
    """
    score = calculate_score_percentile(df, role='striker')
    return score


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
    Calculate value index using scoring_v2_integration.
    
    Args:
        row: Pandas Series containing player data
        price_threshold: Maximum price threshold in Euros
    
    Returns:
        float: Value index per the player, or NaN if not valid
    """
    guide_value = row.get('Guide Value', np.nan)
    age = pd.to_numeric(row.get('Age', np.nan), errors='coerce')
    striker_score = row.get('Striker Score', np.nan)
    
    if pd.isna(guide_value) or pd.isna(age) or pd.isna(striker_score):
        return np.nan
    
    parsed_price = parse_guide_value(guide_value)
    
    if pd.isna(parsed_price) or parsed_price > price_threshold:
        return np.nan
    
    if parsed_price <= 0:
        return np.nan
    
    age_factor = calculate_age_factor(age)
    
    try:
        value_index = (striker_score * age_factor) / parsed_price 
        return value_index
    except ZeroDivisionError:
        return np.nan


def calculate_additional_metrics(row):
    """
    Calculate additional helpful metrics for striker analysis
    
    Args:
        row: Pandas Series containing player data
        
    Returns:
        dict with calculated metrics
    """
    
    # Initialize dictionary to hold results  
    metrics = {}
    
    # Finishing Efficiency = (Goal Contributions per 90) / (Shots per 90)
    goal_contributions_p90 = pd.to_numeric(row.get('Goal Contributions per 90', np.nan), errors='coerce')
    shots_p90 = pd.to_numeric(row.get('Shots per 90', np.nan), errors='coerce')
    
    if not pd.isna(goal_contributions_p90) and not pd.isna(shots_p90) and shots_p90 != 0:
        metrics['Finishing Efficiency'] = goal_contributions_p90 / shots_p90
    else:  
        metrics['Finishing Efficiency'] = np.nan
        
    # xG Overperformance - player may be lucky with high xG but low overperformance 
    xg_p90 = pd.to_numeric(row.get('xG per 90', np.nan), errors='coerce')
    xg_overperformance = pd.to_numeric(row.get('xG Overperformance', np.nan), errors='coerce')
    
    if not pd.isna(xg_p90) and not pd.isna(xg_overperformance):
        # If player has high expected goals but negative overperformance, 
        # they might be underperforming due to luck
        metrics['Growth Potential'] = xg_p90 if (xg_p90 > 0 and xg_overperformance < 0) else 0.0  
    else:
        metrics['Growth Potential'] = np.nan
        
    return metrics


def process_football_data(input_file='strika.csv', output_file='best_striker_prospects.csv'):
    """
    Main function to process striker player data
    
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
            
        # Check for striker stats columns specific to the role
        striker_stats = [
            'Goal Contributions per 90',
            'NP-xG per 90',
            'xG per 90',
            'Key Passes per 90',
            'xA per 90',
            'Shots on Target per 90',
            'Shots per 90',
            'Pressures Attempted per 90',
            'Pass Completion %',
            'xG Overperformance'
        ]
        
        # Add more stats that might be present
        all_stats = [
            'Appearances'
        ] + striker_stats
        
        missing_cols = [col for col in all_stats if col not in df.columns]
        print(f"Missing striker stats columns: {missing_cols}")
        
        # Create a copy to avoid modifying the original
        df_processed = df.copy()
        
        # Convert Guide Value column to numeric 
        print("Processing Guide Value column...")
        df_processed['Guide Value Numeric'] = df_processed['Guide Value'].apply(parse_guide_value)
        
        # Calculate striker score for each player using percentiler method
        print("Calculating striker scores...")
        df_processed['Striker Score'] = calculate_striker_score(df_processed)
        
        # Normalize the striker scores using min-max scaling  
        print("Normalizing striker scores...")
        df_processed['Normalized Striker Score'] = min_max_normalize(df_processed['Striker Score'])
        
        # Calculate value index for each player
        print("Calculating value indices...")
        df_processed['Value Index'] = df_processed.apply(calculate_value_index, axis=1)
        
        # Apply additional metrics 
        print("Computing additional metrics...")
        additional_metrics = df_processed.apply(calculate_additional_metrics, axis=1)
        
        # Add calculated metrics back to dataframe
        for col in ['Finishing Efficiency', 'Growth Potential']:
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
            'Striker Score', 'Value Index',
            'Goal Contributions per 90', 'NP-xG per 90', 'xG per 90',
            'Key Passes per 90', 'xA per 90', 'Shots on Target per 90',
            'Shots per 90', 'Pressures Attempted per 90', 'Pass Completion %'
        ]
        
        # Add any additional columns that might be present
        available_cols = [col for col in output_cols if col in top_20_prospects.columns]
        
        print("\nTop 20 Striker Prospects:")
        print("-" * 60) 
        for index, row in top_20_prospects.iterrows():
            print(f"{row['Name']} ({row['Club']})")
            print(f"Age: {row.get('Age', 'N/A')}")
            print(f"Price: {row.get('Guide Value', 'N/A')}")
            print(f"Striker Score: {row.get('Striker Score', 'N/A'):.2f}")  
            print(f"Value Index: {row.get('Value Index', 'N/A'):.4f}")
            
            # Print striker stats if available
            striker_stats_to_show = ['Goal Contributions per 90', 'NP-xG per 90', 'xG per 90',
                                     'Key Passes per 90', 'xA per 90', 'Shots on Target per 90',
                                     'Shots per 90', 'Pressures Attempted per 90', 'Pass Completion %']
            for stat in striker_stats_to_show:
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
    Compute dimension scores for strikers based on percentile rankings.
    
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
    
    # Define dimensions with their metrics and weights (striker-specific)
    dimensions = {
        'finalizzazione': {
            'metrics': [
                ('Goal Contributions per 90', 2.0),
                ('NP-xG per 90', 1.7),  # Part of xG_Adjusted formula
                ('Shots on Target per 90', 1.2),
                ('xG Overperformance', 0.5)
            ]
        },
        'creazione': {
            'metrics': [
                ('xA per 90', 1.5),
                ('Key Passes per 90', 1.5),
                ('Passaggi progressivi per 90', 1.0)
            ]
        },
        'pressing': {
            'metrics': [
                ('Pressures Attempted per 90', 0.8),
                ('Possession Won per 90', 0.6)
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
        python strika.py
        
    - Process a different file:
        python strika.py input_file.csv output_file.csv
    """
    
    # Default filenames  
    input_filename = "strika.csv" 
    output_filename = "best_striker_prospects.csv"
    
    # Check if command line arguments are provided
    if len(sys.argv) > 1:
        input_filename = sys.argv[1] 
        
    if len(sys.argv) > 2:  
        output_filename = sys.argv[2]
        
    print(f"Starting striker player analysis...")
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
