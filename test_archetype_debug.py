#!/usr/bin/env python3
"""Debug script to verify archetype assignment with normalization."""

import pandas as pd
from scout_app import calculate_tactical_dimensions, assign_archetype, detect_columns, parse_value, normalize

df = pd.read_csv('sample_players.csv')
cm = detect_columns(df)
df['_price'] = df[cm['Guide Value']].apply(parse_value)
df['_age'] = pd.to_numeric(df[cm['Age']], errors='coerce')
df['_apps'] = pd.to_numeric(df[cm['Appearances']], errors='coerce')

# Filter for all players under 15M and age < 30
f = df[(df['_price'] <= 15000000) & (df['_apps'] >= 10) & (df['_age'] < 30)].copy()
print('All filtered players:')
for _, r in f.iterrows():
    print(f'  {r["Name"]}: age={r["_age"]}, price={r["_price"]}')

off = {
    'Goal Contributions per 90': 'Goal Contributions per 90',
    'xG per 90': 'xG per 90',
    'xA per 90': 'xA per 90',
    'Shots on Target per 90': 'Shots on Target per 90',
    'Key Passes per 90': 'Key Passes per 90',
    'Attacking Actions per 90': 'Attacking Actions per 90',
    'NP-xG per 90': 'NP-xG per 90',
    'xG Overperformance': 'xG Overperformance',
    'Shots per 90': 'Shots per 90'
}

f = calculate_tactical_dimensions(f, off)
print('\nRAW tactical dims:')
print(f[['Name','Attacco','Pressing','Finalizzazione','Creatività']].to_string())

# Normalize tactical dimensions to 0-100 scale
for col in ['Attacco', 'Pressing', 'Finalizzazione', 'Creatività']:
    if col in f.columns:
        norm = normalize(f[col])
        f[col] = norm * 100

print('\nNormalized tactical dims:')
print(f[['Name','Attacco','Pressing','Finalizzazione','Creatività']].to_string())

print('\nArchetype assignments:')
for i, r in f.iterrows():
    arch = assign_archetype(r)
    print(f'{r["Name"]}: A={r["Attacco"]:.1f}, P={r["Pressing"]:.1f}, C={r["Creatività"]:.1f}, F={r["Finalizzazione"]:.1f} -> {arch}')
