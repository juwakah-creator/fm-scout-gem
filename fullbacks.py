#!/usr/bin/env python3
"""
Football Player Analysis Script for Identifying Best Value Full-Back/Wing-Back Prospects
"""

import pandas as pd
import numpy as np
from typing import Optional
import os
import sys
from scoring_v2_integration import calculate_score_percentile, calculate_value_index, parse_guide_value


def _parse_guide_value_local(value):
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


def calculate_fullback_score(row):
    df = pd.DataFrame([row])
    return calculate_score_percentile(df, role='full_back').iloc[0]


def min_max_normalize(series):
    if len(series) == 0 or series.min() == series.max():
        return pd.Series([0.0] * len(series), index=series.index)
    normalized = (series - series.min()) / (series.max() - series.min())
    return normalized.fillna(0)


def _calculate_value_index_local(row, price_threshold=5000000):
    guide_value = row.get('Guide Value', np.nan)
    age = pd.to_numeric(row.get('Age', np.nan), errors='coerce')
    full_back_score = row.get('Full-Back Score', np.nan)
    
    if pd.isna(guide_value) or pd.isna(age) or pd.isna(full_back_score):
        return np.nan
    
    parsed_price = _parse_guide_value_local(guide_value)
    if pd.isna(parsed_price) or parsed_price > price_threshold:
        return np.nan
    
    age_factor = calculate_age_factor(age)
    if parsed_price <= 0:
        return np.nan
        
    try:
        value_index = (full_back_score * age_factor) / parsed_price 
        return value_index
    except ZeroDivisionError:
        return np.nan


def calculate_additional_metrics(row):
    metrics = {}
    crosses_p90 = pd.to_numeric(row.get('Crosses per 90', np.nan), errors='coerce')
    through_balls_p90 = pd.to_numeric(row.get('Through Balls per 90', np.nan), errors='coerce')
    key_passes_p90 = pd.to_numeric(row.get('Key Passes per 90', np.nan), errors='coerce')
    
    if not pd.isna(crosses_p90) or not pd.isna(through_balls_p90):
        total_crossing_actions = crosses_p90 + through_balls_p90 if not pd.isna(through_balls_p90) else crosses_p90
        if key_passes_p90 > 0 and total_crossing_actions > 0:
            metrics['Progression vs Creativity'] = total_crossing_actions / key_passes_p90
        else:
            metrics['Progression vs Creativity'] = total_crossing_actions
    else:
        metrics['Progression vs Creativity'] = np.nan
    
    crosses_attempts_p90 = pd.to_numeric(row.get('Crosses Attempts per 90', np.nan), errors='coerce')
    if not pd.isna(crosses_p90) and not pd.isna(crosses_attempts_p90):
        metrics['Cross Accuracy'] = (crosses_p90 / crosses_attempts_p90) * 100 if crosses_attempts_p90 > 0 else 0
    else:
        metrics['Cross Accuracy'] = np.nan
    
    return metrics


def process_football_data(input_file='fullbacks.csv', output_file='best_fullback_prospects.csv'):
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
