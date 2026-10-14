#!/usr/bin/env python3
"""
Football Player Analysis Script for Identifying Best Value Goalkeeper Prospects

This script analyzes football player data to identify the best goalkeeper prospects 
to buy at low cost and flip for profit, with focus on shot-stopping and distribution.
"""

import pandas as pd
import numpy as np
from typing import Optional
import os
import sys
from scoring_v2_integration import calculate_score_percentile, calculate_value_index, parse_guide_value


def parse_guide_value(value):
    if pd.isna(value) or value == '' or value is None:
        return np.nan
    cleaned_value = str(value).strip().replace('€', '').replace(' ', '')
    try:
        if cleaned_value.endswith('K'):
            return float(cleaned_value[:-1]) * 1000
        elif cleaned_value.endswith('M'):
            return float(cleaned_value[:-1]) * 1000000
        else:
            return float(cleaned_value)
    except ValueError:
        print(f"Warning: Could not parse Guide Value '{value}'")
        return np.nan


def calculate_age_factor(age):
    if pd.isna(age) or age < 0:
        return 1.0
    if age <= 20:
        return 2.0
    elif 20 < age <= 23:
        return 1.6
    elif 24 <= age <= 26:
        return 1.3
    else:
        return 1.0


def calculate_goalkeeper_score(row):
    df = pd.DataFrame([row])
    return calculate_score_percentile(df, role='goalkeeper').iloc[0]


def min_max_normalize(series):
    if len(series) == 0 or series.min() == series.max():
        return pd.Series([0.0] * len(series), index=series.index)
    normalized = (series - series.min()) / (series.max() - series.min())
    return normalized.fillna(0)


def calculate_value_index(row, price_threshold=5000000):
    guide_value = row.get('Guide Value', np.nan)
    age = pd.to_numeric(row.get('Age', np.nan), errors='coerce')
    goalkeeper_score = row.get('Goalkeeper Score', np.nan)
    
    if pd.isna(guide_value) or pd.isna(age) or pd.isna(goalkeeper_score):
        return np.nan
    
    parsed_price = parse_guide_value(guide_value)
    if pd.isna(parsed_price) or parsed_price > price_threshold:
        return np.nan
    
    age_factor = calculate_age_factor(age)
    if parsed_price <= 0:
        return np.nan
        
    try:
        value_index = (goalkeeper_score * age_factor) / parsed_price 
        return value_index
    except ZeroDivisionError:
        return np.nan


def calculate_additional_metrics(row):
    metrics = {}
    sweeper_actions_p90 = pd.to_numeric(row.get('Sweeper Actions per 90', np.nan), errors='coerce')
    sweeper_p90 = pd.to_numeric(row.get('Sweeper', np.nan), errors='coerce')
    
    if not pd.isna(sweeper_actions_p90) or not pd.isna(sweeper_p90):
        total_sweeper_actions = sweeper_p90 if pd.notna(sweeper_p90) else sweeper_actions_p90
        metrics['Sweeper Quality'] = total_sweeper_actions
    else:
        metrics['Sweeper Quality'] = np.nan
    
    return metrics


def process_football_data(input_file='goalkeepers.csv', output_file='best_goalkeeper_prospects.csv'):
    try:
        print(f"Reading data from {input_file}...")
        df = pd.read_csv(input_file)
        print(f"Successfully read {len(df)} rows of player data")
        
        expected_columns = ['Name', 'Club', 'Age', 'Guide Value']
        missing_cols = [col for col in expected_columns if col not in df.columns]
        
        if missing_cols:
            print(f"Warning: Missing expected columns: {missing_cols}")
            return None
            
        # ... rest of function truncated for brevity
        
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
        return None
    except pd.errors.EmptyDataError:
        print("Error: CSV file is empty")
        return None
    except Exception as e:
        print(f"Unexpected error processing data: {e}")
        return None
