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


def calculate_defender_score(df):
    """
   Calculate percentile-based defender score using scoring_v2_integration.
    
    Args:
        df: DataFrame con stats dei giocatori
        
    Returns:
        pandas.Series: Punteggio defender normalizzato 0-100
    """
    return calculate_score_percentile(df, role='defender')


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
    Calculate the value index comparing defensive potential to price
    
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
    
    # Defensive Efficiency = (Tackles + Interceptions) per 90 / (Clearances + Blocks per 90)
    tackles_p90 = pd.to_numeric(row.get('Tackles per 90', np.nan), errors='coerce')
    interceptions_p90 = pd.to_numeric(row.get('Interceptions per 90', np.nan), errors='coerce')
    clearances_p90 = pd.to_numeric(row.get('Clearances per 90', np.nan), errors='coerce')
    blocks_p90 = pd.to_numeric(row.get('Blocks per 90', np.nan), errors='coerce')
    
    if not pd.isna(tackles_p90) and not pd.isna(interceptions_p90):
        total_defensive_actions = tackles_p90 + interceptions_p90
        total_clearances_blocks = clearances_p90 + blocks_p90 if not (pd.isna(clearances_p90) or pd.isna(blocks_p90)) else 0
        metrics['Defensive Efficiency'] = total_defensive_actions / (total_clearances_blocks if total_clearances_blocks > 0 else 1)
    else:
        metrics['Defensive Efficiency'] = np.nan
        
    # Build-up Quality - player may be good at passing but low in progressive actions
    progressive_passes_p90 = pd.to_numeric(row.get('Progressive Passes per 90', np.nan), errors='coerce')
    key_passes_p90 = pd.to_numeric(row.get('Key Passes per 90', np.nan), errors='coerce')
    
    if not pd.isna(progressive_passes_p90):
        metrics['Build-up Quality'] = progressive_passes_p90 if progressive_passes_p90 > 0 else 0.0
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
            
        # Check for defender stats columns
        defender_stats = [
            'Tackles per 90',
            'Interceptions per 90',
            'Clearances per 90',
            'Blocks per 90',
            'Header Win %',
            'Progressive Passes per 90',
            'Pass Completion %',
            'Pressures Attempted per 90',
            'Aerial Duels Won %',
            'Dribbled Past per 90',
            'Dispossessed per 90',
            'Fouls per 90',
            'Yellow Cards',
            'Red Cards',
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
        
        # Calculate defender score for each player using percentile method
        print("Calculating defender scores...")
        df_processed['Defender Score'] = calculate_defender_score(df_processed)
        
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
            'Tackles per 90', 'Interceptions per 90', 'Clearances per 90',
            'Blocks per 90', 'Header Win %', 'Progressive Passes per 90',
            'Pass Completion %', 'Pressures Attempted per 90', 'Aerial Duels Won %'
        ]
        
        # Add additional columns that might be present
        additional_output_cols = [
            'Dribbled Past per 90',
            'Dispossessed per 90',
            'Fouls per 90',
            'Yellow Cards',
            'Red Cards',
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
            defender_stats_to_show = ['Tackles per 90', 'Interceptions per 90',
                                       'Clearances per 90', 'Blocks per 90',
                                       'Header Win %', 'Progressive Passes per 90',
                                       'Pass Completion %', 'Pressures Attempted per 90',
                                       'Aerial Duels Won %']
            for stat in defender_stats_to_show:
                value = row.get(stat, 'N/A')
                if not isinstance(value, str) and pd.notna(value):
                    print(f"{stat}: {value:.2f}")
                elif isinstance(value, str) and value != 'N/A':
                    print(f"{stat}: {value}")
            
            # Print additional stats if available
            additional_stats_to_show = ['Dribbled Past per 90', 'Dispossessed per 90',
                                        'Fouls per 90', 'Yellow Cards', 'Red Cards']
            for stat in additional_stats_to_show:
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
            #print(f"\nResults saved to {output_file}")
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
