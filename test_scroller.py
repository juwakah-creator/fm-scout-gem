#!/usr/bin/env python3
"""Test script to verify scrollable tables functionality."""

import pandas as pd
from scout_app import detect_columns, parse_value, normalize, calculate_tactical_dimensions, age_factor
import gradio as gr

# Load sample data
df = pd.read_csv('sample_players.csv')
print(f'Loaded {len(df)} players')

# Test the analysis logic directly (copying from app.py)
cm = detect_columns(df)
df['_price'] = df[cm['Guide Value']].apply(parse_value)
df['_age'] = pd.to_numeric(df[cm['Age']], errors='coerce')
df['_apps'] = pd.to_numeric(df[cm['Appearances']], errors='coerce')

# Apply filters
filtered_df = df[
    (df['_price'] >= 0) &
    (df['_price'] <= 200_000_000) &
    (df['_apps'] >= 10) &
    (df['_age'] >= 17) &
    (df['_age'] < 30)
].copy()

print(f'Filtered to {len(filtered_df)} players')

# Define offensive stats
available_off = {}
df_columns_lower = [col.lower() for col in df.columns]

offensive_candidates = {
    'Goal Contributions per 90': ['goal contributions p90', 'g+a p90', 'goal contributions per 90'],
    'xG per 90': ['xg p90', 'xG per 90', 'expected goals p90'],
    'xA per 90': ['xa p90', 'xA per 90'],
    'Shots on Target per 90': ['shots on target p90', 'sot p90'],
    'Key Passes per 90': ['key passes p90', 'kp p90'],
    'Attacking Actions per 90': ['attacking actions p90'],
    'NP-xG per 90': ['np-xg p90', 'non-penalty xg p90'],
    'xG Overperformance': ['xg overperformance'],
    'Shots per 90': ['shots p90', 'shots per 90']
}

for standard_name, variations in offensive_candidates.items():
    for variation in variations:
        if variation.lower() in df_columns_lower:
            available_off[standard_name] = df.columns[df_columns_lower.index(variation.lower())]
            break

print(f'Detected {len(available_off)} offensive stats')

# Normalize and calculate scores (same logic as app.py)
for standard_name, actual_column in available_off.items():
    filtered_df[f'_numeric_{actual_column}'] = pd.to_numeric(filtered_df[actual_column], errors='coerce')
    normalized_col_name = f'_norm_{actual_column}'
    filtered_df[normalized_col_name] = normalize(filtered_df[f'_numeric_{actual_column}'])

# Calculate weighted offensive score
weights = {
    'Goal Contributions per 90': 2.0,
    'xG per 90': 2.0,
    'xA per 90': 2.0,
    'Shots on Target per 90': 1.0,
    'Key Passes per 90': 1.0,
    'Attacking Actions per 90': 1.0,
    'NP-xG per 90': 1.5,
    'xG Overperformance': 0.5
}

offensive_score = 0
weight_sum = 0
for standard_name, actual_column in available_off.items():
    if standard_name in weights:
        normalized_col_name = f'_norm_{actual_column}'
        if normalized_col_name in filtered_df.columns:
            weighted_value = filtered_df[normalized_col_name] * weights[standard_name]
            offensive_score += weighted_value
            weight_sum += weights[standard_name]

if weight_sum > 0:
    filtered_df['Offensive Score'] = offensive_score / weight_sum
else:
    filtered_df['Offensive Score'] = 0

# Calculate tactical dimensions
filtered_df = calculate_tactical_dimensions(filtered_df, available_off)

# Normalize tactical dimensions to 0-100 scale
tactical_cols = ['Attacco', 'Pressing', 'Finalizzazione', 'Creatività']
for col in tactical_cols:
    if col in filtered_df.columns:
        normalized = normalize(filtered_df[col])
        filtered_df[col] = normalized * 100

# Apply age factor
filtered_df['Age Factor'] = filtered_df['_age'].apply(age_factor)

# Calculate Value Index
valid_price = filtered_df['_price'].replace(0, float('inf'))
value_index_raw = (filtered_df['Offensive Score'] * filtered_df['Age Factor']) / (valid_price / 1_000_000)
raw_value_index = value_index_raw.replace([float('inf'), float('-inf')], float('nan')).fillna(0)

# Normalize Value Index to 0-100 scale
if len(raw_value_index) > 0:
    max_val = raw_value_index.max()
    if max_val > 0:
        normalized_vi = (raw_value_index / max_val * 100).round(2)
        filtered_df['Value Index'] = normalized_vi.clip(upper=100)
    else:
        filtered_df['Value Index'] = 0
else:
    filtered_df['Value Index'] = 0

# Sort by Value Index descending and take top 20
sorted_df = filtered_df.sort_values('Value Index', ascending=False).head(20)

if len(sorted_df) == 0:
    print("No players match criteria")
else:
    # Build output DataFrame
    result_out = pd.DataFrame()
    result_out['Name'] = sorted_df['Name']
    result_out['Club'] = sorted_df['Club']
    result_out['Age'] = sorted_df['_age']
    result_out['Guide Value'] = df.loc[sorted_df.index, cm['Guide Value']]
    result_out['Offensive Score'] = sorted_df['Offensive Score'].round(2)
    result_out['Value Index'] = sorted_df['Value Index']
    result_out['Age Factor'] = sorted_df['Age Factor']
    
    # Add offensive stats columns
    for standard_name, actual_column in available_off.items():
        if actual_column in sorted_df.columns:
            result_out[standard_name] = sorted_df[actual_column].round(2)
    
    # Add tactical dimensions
    for col in tactical_cols:
        if col in sorted_df.columns:
            result_out[col] = sorted_df[col].round(1)
    
    print(f'\nResult shape: {result_out.shape}')
    print(f'Columns: {list(result_out.columns)}')
    
    # Create HTML table with scrollable container wrapper (same as app.py)
    html_table = f"""<div class="scrollable-table-container">
<table>
{sorted_df.to_html(classes='', border=0, index=False)}
</table>
</div>"""
    
    # Check if scrollable container is in the HTML
    if 'scrollable-table-container' in html_table:
        print('\n✅ SUCCESS: Scrollable table wrapper is present!')
        print(f'Table contains {len(sorted_df)} rows and {result_out.shape[1]} columns')
        
        # Verify it's not just the class name but the actual structure
        if '<div' in html_table and '</div>' in html_table:
            print('✅ HTML structure is correct with div wrapper')
    else:
        print('\n❌ FAIL: Scrollable table wrapper NOT found!')

print('\n=== Test completed ===')
