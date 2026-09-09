#!/usr/bin/env python3
"""Debug script to trace archetype assignment in app context."""

import pandas as pd
from scout_app import detect_columns, parse_value, normalize, calculate_tactical_dimensions, assign_archetype, get_archetype_multiplier, age_factor

df = pd.read_csv('sample_players.csv')
cm = detect_columns(df)
print('Columns:', list(df.columns))
print('Guide Value type:', df['Guide Value'].dtype)
print('Age type:', df['Age'].dtype)
print('Appearances type:', df['Appearances'].dtype)

df_filtered = df.copy()
df_filtered['_price'] = df_filtered[cm['Guide Value']].apply(parse_value)
df_filtered['_age'] = pd.to_numeric(df_filtered[cm['Age']], errors='coerce')
df_filtered['_apps'] = pd.to_numeric(df_filtered[cm['Appearances']], errors='coerce')

# Apply filters like in app.py (min_price_val=0, price_val=15.0, min_apps=10, max_age=30)
filtered_df = df_filtered[
    (df_filtered['_price'] >= 0) &
    (df_filtered['_price'] <= 15000000) &
    (df_filtered['_apps'] >= 10) &
    (df_filtered['_age'] < 30) &
    (df_filtered['_age'].notna()) &
    (df_filtered['_price'].notna())
].copy()

print(f'Filtered: {len(filtered_df)}')

# Calculate offensive stats and archetype for debug display
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

available_off = {}
df_columns_lower = [col.lower() for col in df.columns]
for standard_name, variations in offensive_candidates.items():
    matching_column = None
    for variation in variations:
        if variation.lower() in df_columns_lower:
            matching_column = df.columns[df_columns_lower.index(variation.lower())]
            break
    if matching_column:
        available_off[standard_name] = matching_column

print(f'Available off keys: {list(available_off.keys())}')
print(f'Available off values: {list(available_off.values())}')

if len(available_off) >= 3:
    for standard_name, actual_column in available_off.items():
        filtered_df[f'_numeric_{actual_column}'] = pd.to_numeric(filtered_df[actual_column], errors='coerce')
        normalized_col_name = f'_norm_{actual_column}'
        filtered_df[normalized_col_name] = normalize(filtered_df[f'_numeric_{actual_column}'])
    
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
    
    filtered_df = calculate_tactical_dimensions(filtered_df, available_off)
    # Normalize tactical dimensions to 0-100 scale for archetype assignment
    tactical_cols = ['Attacco', 'Pressing', 'Finalizzazione', 'Creatività']
    for col in tactical_cols:
        if col in filtered_df.columns:
            normalized = normalize(filtered_df[col])
            filtered_df[col] = normalized * 100
    filtered_df['Age Factor'] = filtered_df['_age'].apply(age_factor)
    filtered_df['Archetype'] = filtered_df.apply(lambda row: assign_archetype(row), axis=1)
    filtered_df['Archetype Multiplier'] = filtered_df['Archetype'].apply(get_archetype_multiplier)
    filtered_df['Value Index'] = (filtered_df['Offensive Score'] * filtered_df['Age Factor'] * filtered_df['Archetype Multiplier']) / filtered_df['_price']
    
    print('Archetypes:')
    for _, r in filtered_df.iterrows():
        print(f'  {r["Name"]}: A={r["Attacco"]:.1f}, P={r["Pressing"]:.1f} -> {r["Archetype"]}')
    
    # Test filter
    archetype_filter = ['Segna & Pressa']
    filtered_df2 = filtered_df[filtered_df['Archetype'].isin(archetype_filter)]
    print(f'\nFiltered by Segna & Pressa: {len(filtered_df2)}')
    if len(filtered_df2) > 0:
        print(filtered_df2[['Name', 'Archetype']].to_string())
