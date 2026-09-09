#!/usr/bin/env python3
"""
Football Player Analysis Script for Identifying Best Value Goalkeeper Prospects

This script analyzes football player data to identify the best goalkeeper prospects 
to buy at low cost and flip for profit, with focus on shot-stopping ability and 
modern goalkeeping skills (distribution, claiming).

Features:
- Reads CSV files with football player statistics
- Handles special formatting in Guide Value column (€, K, M)
- Calculates composite goalkeeper scores with weighted metrics specific to GK role
- Computes value index comparing goalkeeping potential to price
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


def calculate_goalkeeper_score(row):
    """
    Calculate a composite score with weighted metrics for goalkeepers.
    
    Goalkeeper weights (shot-stopping, high impact, 1.5-3.0x):
    - Save Percentage % → 3.0x
    - Clean Sheets % → 2.5x
    - Goals Conceded per 90 → 2.0x (inverted: lower is better)
    - Saves per 90 → 1.5x
    
    Goalkeeper weights (distribution/build-up, medium impact, 1.0-1.5x):
    - Pass Completion % → 1.5x
    - Progressive Passes per 90 → 1.0x
    - Distribution Accuracy % → 1.0x
    
    Goalkeeper weights (claiming/defensive, low impact, 0.5-1.0x):
    - Crosses Claimed % → 0.6x (ridotto da 1.0 a 0.6 per bilanciamento)
    - High Claims per 90 → 0.8x
    - Sweeper Actions per 90 → 1.0x (aumentato da 0.5 a 1.0 per enfatizzare le uscite)
    
    Args:
        row: Pandas Series containing player data
        
    Returns:
        float: Composite goalkeeper score
    """
    
    # === SHOT-STOPPING METRICS (high impact) ===
    save_percentage = row.get('Save Percentage %', np.nan)
    clean_sheets_pct = row.get('Clean Sheets %', np.nan)
    goals_conceded_p90 = row.get('Goals Conceded per 90', np.nan)
    saves_per_90 = row.get('Saves per 90', np.nan)
    
    # === DISTRIBUTION METRICS (medium impact) ===
    pass_completion_pct = row.get('Pass Completion %', np.nan)
    progressive_passes_p90 = row.get('Progressive Passes per 90', np.nan)
    distribution_accuracy_pct = row.get('Distribution Accuracy %', np.nan)
    
    # === CLAIMING METRICS (low impact) ===
    crosses_claimed_pct = row.get('Crosses Claimed %', np.nan)
    high_claims_p90 = row.get('High Claims per 90', np.nan)
    sweeper_actions_p90 = row.get('Sweeper Actions per 90', np.nan)
    
    # Initialize score with a base value of 0
    goalkeeper_score = 0.0
    
    # === SHOT-STOPPING WEIGHTS (elevated) ===
    if not pd.isna(save_percentage):
        goalkeeper_score += save_percentage * 3.0
    if not pd.isna(clean_sheets_pct):
        goalkeeper_score += clean_sheets_pct * 2.5
    if not pd.isna(goals_conceded_p90):
        # Invert: lower goals conceded is better
        goalkeeper_score += (10 - goals_conceded_p90) * 2.0
    if not pd.isna(saves_per_90):
        goalkeeper_score += saves_per_90 * 1.5
    
    # === DISTRIBUTION WEIGHTS (medium) ===
    if not pd.isna(pass_completion_pct):
        goalkeeper_score += pass_completion_pct * 1.5
    if not pd.isna(progressive_passes_p90):
        goalkeeper_score += progressive_passes_p90 * 1.0
    if not pd.isna(distribution_accuracy_pct):
        goalkeeper_score += distribution_accuracy_pct * 1.0
    
    # === CLAIMING WEIGHTS (low) ===
    if not pd.isna(crosses_claimed_pct):
        goalkeeper_score += crosses_claimed_pct * 0.6  # Peso ridotto per bilanciamento
    if not pd.isna(high_claims_p90):
        goalkeeper_score += high_claims_p90 * 0.8
    if not pd.isna(sweeper_actions_p90):
        goalkeeper_score += sweeper_actions_p90 * 1.0  # Peso aumentato per enfatizzare le uscite
    
    return goalkeeper_score


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
    Calculate the value index comparing goalkeeping potential to price
    
    Value Index = (Goalkeeper Score * Age Factor) / Price
    
    Args:
        row: Pandas Series containing player data
        price_threshold: Maximum price threshold in Euros
        
    Returns:
        float: Value index for the player, or NaN if not valid
    """
    
    # Extract required values
    guide_value = row.get('Guide Value', np.nan)
    age = row.get('Age', np.nan)
    goalkeeper_score = row.get('Goalkeeper Score', np.nan) 
    
    # Check if we have enough data to calculate value index
    if pd.isna(guide_value) or pd.isna(age) or pd.isna(goalkeeper_score):
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
        value_index = (goalkeeper_score * age_factor) / parsed_price 
        return value_index
    except ZeroDivisionError:
        return np.nan


def calculate_additional_metrics(row):
    """
    Calculate additional helpful metrics for goalkeeper analysis
    
    Args:
        row: Pandas Series containing player data
        
    Returns:
        dict with calculated metrics
    """
    
    # Initialize dictionary to hold results  
    metrics = {}
    
    # Shot Stopping Efficiency = (Save Percentage * 10) / (Goals Conceded per 90 + 1)
    save_percentage = row.get('Save Percentage %', np.nan)
    goals_conceded_p90 = row.get('Goals Conceded per 90', np.nan)
    
    if not pd.isna(save_percentage) and not pd.isna(goals_conceded_p90):
        metrics['Shot Stopping Efficiency'] = (save_percentage * 10) / (goals_conceded_p90 + 1)
    else:  
        metrics['Shot Stopping Efficiency'] = np.nan
        
    # Distribution Quality - ratio of progressive passes to total passes
    progressive_passes_p90 = row.get('Progressive Passes per 90', np.nan)
    pass_completion_pct = row.get('Pass Completion %', np.nan)
    
    if not pd.isna(progressive_passes_p90) and not pd.isna(pass_completion_pct):
        # Higher progressive passes with good completion = better distribution
        metrics['Distribution Quality'] = progressive_passes_p90 * (pass_completion_pct / 100)
    else:
        metrics['Distribution Quality'] = np.nan
        
    # Claiming Ability - combination of crosses claimed and high claims
    crosses_claimed_pct = row.get('Crosses Claimed %', np.nan)
    high_claims_p90 = row.get('High Claims per 90', np.nan)
    
    if not pd.isna(crosses_claimed_pct) and not pd.isna(high_claims_p90):
        metrics['Claiming Ability'] = (crosses_claimed_pct + high_claims_p90 * 10) / 2
    else:
        metrics['Claiming Ability'] = np.nan
        
    return metrics


def process_football_data(input_file='goalkeeper.csv', output_file='best_gk_prospects.csv'):
    """
    Main function to process football player data for goalkeepers
    
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
            
        # Check for goalkeeper stats columns
        goalkeeper_stats = [
            'Save Percentage %',
            'Clean Sheets %',
            'Goals Conceded per 90',
            'Saves per 90',
            'Pass Completion %',
            'Progressive Passes per 90',
            'Distribution Accuracy %',
            'Crosses Claimed %',
            'High Claims per 90',
            'Sweeper Actions per 90'
        ]
        
        # Add more stats that might be present
        all_stats = goalkeeper_stats + [
            'Appearances',
            'Shots per 90'
        ]
        
        missing_cols = [col for col in all_stats if col not in df.columns]
        print(f"Missing goalkeeper stats columns: {missing_cols}")
        
        # Create a copy to avoid modifying the original
        df_processed = df.copy()
        
        # Convert Guide Value column to numeric 
        print("Processing Guide Value column...")
        df_processed['Guide Value Numeric'] = df_processed['Guide Value'].apply(parse_guide_value)
        
        # Calculate goalkeeper score for each player
        print("Calculating goalkeeper scores...")
        df_processed['Goalkeeper Score'] = df_processed.apply(calculate_goalkeeper_score, axis=1)
        
        # Normalize the goalkeeper scores using min-max scaling  
        print("Normalizing goalkeeper scores...")
        df_processed['Normalized Goalkeeper Score'] = min_max_normalize(df_processed['Goalkeeper Score'])
        
        # Calculate value index for each player
        print("Calculating value indices...")
        df_processed['Value Index'] = df_processed.apply(calculate_value_index, axis=1)
        
        # Apply additional metrics 
        print("Computing additional metrics...")
        additional_metrics = df_processed.apply(calculate_additional_metrics, axis=1)
        
        # Add calculated metrics back to dataframe
        for col in ['Shot Stopping Efficiency', 'Distribution Quality', 'Claiming Ability']:
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
            'Goalkeeper Score', 'Value Index',
            'Save Percentage %', 'Clean Sheets %', 'Goals Conceded per 90', 'Saves per 90',
            'Pass Completion %', 'Progressive Passes per 90'
        ]
        
        # Add claiming columns if present
        claiming_output_cols = [
            'Crosses Claimed %',
            'High Claims per 90',
            'Sweeper Actions per 90'
        ]
        
        # Add any additional columns that might be present
        available_cols = [col for col in output_cols if col in top_20_prospects.columns]
        
        print("\nTop 20 Goalkeeper Prospects:")
        print("-" * 60) 
        for index, row in top_20_prospects.iterrows():
            print(f"{row['Name']} ({row['Club']})")
            print(f"Age: {row.get('Age', 'N/A')}")
            print(f"Price: {row.get('Guide Value', 'N/A')}")
            print(f"Goalkeeper Score: {row.get('Goalkeeper Score', 'N/A'):.2f}")  
            print(f"Value Index: {row.get('Value Index', 'N/A'):.4f}")
            
            # Print additional stats if available
            gk_stats_to_show = ['Save Percentage %', 'Clean Sheets %',
                               'Goals Conceded per 90', 'Saves per 90',
                               'Pass Completion %', 'Progressive Passes per 90']
            for stat in gk_stats_to_show:
                value = row.get(stat, 'N/A')
                if not isinstance(value, str) and pd.notna(value):
                    print(f"{stat}: {value:.2f}")
                elif isinstance(value, str) and value != 'N/A':
                    print(f"{stat}: {value}")
            # Print claiming stats if available
            claiming_stats_to_show = ['Crosses Claimed %', 'High Claims per 90', 'Sweeper Actions per 90']
            for stat in claiming_stats_to_show:
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
    Compute dimension scores for goalkeepers based on percentile rankings.
    
    Creates 4 new columns classifying playing style:
    - shot_stopping_score: Shot-stopping ability (Save %, Goals Conceded)
    - distribution_score: Distribution/build-up ability (Pass Completion, Progressive Passes)
    - claiming_score: Claiming/defensive ability (Crosses Claimed, High Claims)
    - modern_goalkeeper_score: Overall modern goalkeeper score (average of 3 dimensions)
    
    Args:
        df: pandas.DataFrame with player statistics
        
    Returns:
        pandas.DataFrame: DataFrame with only the 4 dimension score columns
    """
    # Edge case: empty DataFrame
    if len(df) == 0:
        return pd.DataFrame(columns=[
            'shot_stopping_score', 'distribution_score',
            'claiming_score', 'modern_goalkeeper_score'
        ])
    
    # Define dimensions with their metrics and weights
    dimensions = {
        'shot_stopping': {
            'metrics': [
                ('Save Percentage %', 3.0),
                ('Goals Conceded per 90', 2.0),  # Inverted: lower is better
                ('Clean Sheets %', 2.5)
            ]
        },
        'distribution': {
            'metrics': [
                ('Pass Completion %', 1.5),
                ('Progressive Passes per 90', 1.0),
                ('Distribution Accuracy %', 1.0)
            ]
        },
        'claiming': {
            'metrics': [
                ('Crosses Claimed %', 1.0),
                ('High Claims per 90', 0.8),
                ('Sweeper Actions per 90', 0.5)
            ]
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
        for dim_name in ['shot_stopping', 'distribution', 'claiming', 'modern_goalkeeper']:
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
    
    for dim_name in ['shot_stopping', 'distribution', 'claiming']:
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
    
    # Calculate modern_goalkeeper_score as average of the other three
    gk_components = [
        result_data.get('shot_stopping_score'),
        result_data.get('distribution_score'),
        result_data.get('claiming_score')
    ]
    
    # Filter out None values and calculate mean
    valid_scores = [s for s in gk_components if s is not None]
    if valid_scores:
        modern_goalkeeper_score = pd.concat(valid_scores, axis=1).mean(axis=1)
        result_data['modern_goalkeeper_score'] = modern_goalkeeper_score.round(2)
    else:
        # All scores are NaN (no metrics available), create a Series of NaN values
        result_data['modern_goalkeeper_score'] = pd.Series(np.nan, index=df.index)
    
    # Create result DataFrame with only the 4 score columns
    result_df = pd.DataFrame({
        'shot_stopping_score': result_data.get('shot_stopping_score'),
        'distribution_score': result_data.get('distribution_score'),
        'claiming_score': result_data.get('claiming_score'),
        'modern_goalkeeper_score': result_data.get('modern_goalkeeper_score')
    })
    
    return result_df


# Entry point for the script
if __name__ == "__main__":
    """
    Main entry point of the script.
    
    Usage examples:
    - Run with default filenames:
        python goalkeeper.py
        
    - Process a different file:
        python goalkeeper.py input_file.csv output_file.csv
    """
    
    # Default filenames  
    input_filename = "goalkeeper.csv" 
    output_filename = "best_gk_prospects.csv"
    
    # Check if command line arguments are provided
    if len(sys.argv) > 1:
        input_filename = sys.argv[1] 
        
    if len(sys.argv) > 2:  
        output_filename = sys.argv[2]
        
    print(f"Starting goalkeeper analysis...")
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
