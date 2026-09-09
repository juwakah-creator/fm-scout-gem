#!/usr/bin/env python3
"""Debug script to trace archetype assignment in app context."""

import pandas as pd
from scout_app import detect_columns, parse_value, normalize, calculate_tactical_dimensions, assign_archetype, get_archetype_multiplier, age_factor

df = pd.read_csv('sample_players.csv')
cm = detect_columns(df)
df['_price'] = df[cm['Guide Value']].apply(parse_value)
df['_age'] = pd.to_numeric(df[cm['Age']], errors='coerce')
df['_apps'] = pd.to_numeric(df[cm['Appearances']], errors='coerce')

# Filter like in run_scout_analysis
filtered_df = df[(df['_price'] <= 15000000) & (df['_apps'] >= 10) & (df['_age'] < 30)].copy()
print(f'Filtered players: {len(filtered_df)}')

# Available offensive stats
available_off = {'Goal Contributions per 90': 'Goal Contributions per 90', 'xG per 90': 'xG per 90', 'xA per 90': 'xA per 90', 'Shots on Target per 90': 'Shots on Target per 90', 'Key Passes per 90': 'Key Passes per 90', 'Attacking Actions per 90': 'Attacking Actions per 90', 'NP-xG per 90': 'NP-xG per 90', 'xG Overperformance': 'xG Overperformance', 'Shots per 90': 'Shots per 90'}

# Normalize offensive stats
for standard_name, actual_column in available_off.items():
    filtered_df[f'_numeric_{actual_column}'] = pd.to_numeric(filtered_df[actual_column], errors='coerce')
    normalized_col_name = f'_norm_{actual_column}'
    filtered_df[normalized_col_name] = normalize(filtered_df[f'_numeric_{actual_column}'])

# Calculate offensive score
weights = {'Goal Contributions per 90': 2.0, 'xG per 90': 2.0, 'xA per 90': 2.0, 'Shots on Target per 90': 1.0, 'Key Passes per 90': 1.0, 'Attacking Actions per 90': 1.0, 'NP-xG per 90': 1.5, 'xG Overperformance': 0.5}
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

# Normalize tactical dimensions
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
