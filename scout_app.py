import pandas as pd
import numpy as np
import re

def _generate_debug_html(df):
    """Generate debug HTML showing final Value Index for each row."""
    debug_df = df[['Name', 'Value Index']].copy()
    debug_df['Value Index'] = debug_df['Value Index'].round(6)
    debug_html = debug_df.to_html(classes='table table-striped', border=0, index=False)
    
    return debug_html

def parse_value(val):
    """Convert currency strings to numeric values.
    
    Args:
        val: String representing a value (e.g. "€1.2M", "€50K")
        
    Returns:
        float: Numeric representation of the value
    """
    if pd.isna(val) or val == '':
        return 0
    
    # Convert to string and remove currency symbols
    val_str = str(val).strip()
    
    # Remove non-numeric characters except decimal point and K/M
    val_clean = re.sub(r'[^0-9\.KMkm]', '', val_str)
    
    # Handle different suffixes
    if 'M' in val_clean.upper():
        return float(val_clean.replace('M', '').replace('m', '')) * 1000000
    elif 'K' in val_clean.upper():
        return float(val_clean.replace('K', '').replace('k', '')) * 1000
    else:
        # If no suffix, convert to float directly
        try:
            return float(val_clean)
        except ValueError:
            return 0

def normalize(series):
    """Normalize a pandas Series using min-max scaling.
    
    Args:
        series: pandas.Series to normalize
        
    Returns:
        pandas.Series: Min-max normalized version (values between 0 and 1)
    """
    # Check if series has only one unique value or zero variance
    if series.nunique() <= 1:
        return pd.Series([0.5] * len(series), index=series.index)
    
    # Min-max normalization: (x - min) / (max - min)
    series_min = series.min()
    series_max = series.max()
    range_diff = series_max - series_min
    
    # Avoid division by zero
    if range_diff == 0:
        return pd.Series([0.5] * len(series), index=series.index)
    
    normalized = (series - series_min) / range_diff
    return normalized

def age_factor(age):
    """Calculate age factor - younger players get MUCH higher value.
    
    Players under 23 get maximum bonus (2.0x), then gradually decreases until 27.
    Players 27+ get standard factor (1.0).
    This strongly favors young players with good stats and low value.
    
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

def calculate_tactical_dimensions(df, available_off):
    """Calculate tactical dimensions from offensive statistics.
    
    Maps offensive stats to 5 tactical dimensions based on the project's analysis:
    - Attacco (Attack): xG + NP-xG + SOT
    - Pressing: Attacking Actions + Key Passes
    - Finalizzazione (Finishing): Shots per 90 + Goals per 90
    - Creatività (Creativity): Key Passes + Assists
    - Minuto Medio Goal (Goal Timing): Minutes per Goal
    
    Args:
        df: DataFrame with offensive statistics
        available_off: dict mapping standard names to actual column names
        
    Returns:
        DataFrame with added tactical dimension columns
    """
    # Map standard names to actual columns
    xg_col = None
    npxg_col = None
    sot_col = None
    actions_col = None
    key_passes_col = None
    shots_col = None
    goals_col = None
    assists_col = None
    minutes_col = None
    
    for standard_name, actual_column in available_off.items():
        if standard_name == 'xG per 90':
            xg_col = actual_column
        elif standard_name == 'NP-xG per 90':
            npxg_col = actual_column
        elif standard_name == 'Shots on Target per 90':
            sot_col = actual_column
        elif standard_name == 'Attacking Actions per 90':
            actions_col = actual_column
        elif standard_name == 'Key Passes per 90':
            key_passes_col = actual_column
        elif standard_name == 'Shots per 90':
            shots_col = actual_column
        elif standard_name == 'Goals per 90':
            goals_col = actual_column
        elif standard_name == 'Assists per 90':
            assists_col = actual_column
        elif standard_name == 'Minutes per Goal':
            minutes_col = actual_column
    
    # Calculate tactical dimensions (only if columns exist)
    if xg_col and npxg_col and sot_col:
        df['Attacco'] = df[xg_col] + df[npxg_col] + df[sot_col]
    else:
        df['Attacco'] = 0
    
    if actions_col and key_passes_col:
        df['Pressing'] = df[actions_col] + df[key_passes_col]
    else:
        df['Pressing'] = 0
    
    if shots_col and goals_col:
        df['Finalizzazione'] = df[shots_col] + df[goals_col]
    else:
        df['Finalizzazione'] = 0
    
    if key_passes_col and assists_col:
        df['Creatività'] = df[key_passes_col] + df[assists_col]
    else:
        df['Creatività'] = 0
    
    # Goal timing dimension (lower is better - scoring sooner)
    if minutes_col:
        df['Minuto Medio Goal'] = df[minutes_col]
    else:
        df['Minuto Medio Goal'] = 90  # Default to full match time
    
    return df


def detect_columns(df):
    """Automatically identify standard column names from DataFrame.
    
    Args:
        df: pandas.DataFrame containing the data
        
    Returns:
        dict mapping standard column names to actual column names found
        
    Raises:
        ValueError: If any required column is missing
    """
    # Define expected columns and their possible variations
    column_mappings = {
        'Name': ['name', 'player', 'fullname', 'full_name', 'title'],
        'Club': ['club', 'team', 'organization', 'company'],
        'Age': ['age', 'years', 'duration'],
        'Guide Value': ['value', 'price', 'guide_value', 'guide value', 'cost', 'worth'],
        'Appearances': ['appearances', 'apps', 'games_played', 'playtime']
    }
    
    # Create reverse mapping for easier lookups
    column_aliases = {}
    for standard_name, variations in column_mappings.items():
        for variation in variations:
            column_aliases[variation.lower()] = standard_name
    
    # Find actual columns
    found_columns = {}
    df_columns_lower = [col.lower() for col in df.columns]
    
    for standard_name, variations in column_mappings.items():
        matching_column = None
        
        # Check if any of the variations match a column name (case insensitive)
        for i, col_lower in enumerate(df_columns_lower):
            if col_lower in [var.lower() for var in variations]:
                matching_column = df.columns[i]
                break
                
        if matching_column:
            found_columns[standard_name] = matching_column
        else:
            raise ValueError(f"Required column '{standard_name}' not found. "
                           f"Expected one of: {', '.join(variations)}")
    
    return found_columns

def analyze_csv(file_path, price_threshold, min_price=0.0, min_apps=0, max_age=40):
    """Main analysis function.
    
    Args:
        file_path: Path to the CSV file
        price_threshold: Maximum value threshold for filtering (in €)
        min_price: Minimum value threshold for filtering (in €)
        min_apps: Minimum number of appearances required
        max_age: Maximum age allowed
        
    Returns:
        str: HTML string with results or error message
    """
    try:
        # Read CSV file with fallback encoding
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='latin1')
        
        # Detect columns automatically
        column_mapping = detect_columns(df)
        
        # Extract relevant columns
        name_col = column_mapping['Name']
        club_col = column_mapping['Club']
        age_col = column_mapping['Age']
        value_col = column_mapping['Guide Value']
        apps_col = column_mapping['Appearances']
        
        # Create a working copy of the DataFrame
        df_filtered = df.copy()
        
        # Parse Guide Value to numeric _price in € millions
        df_filtered['_price'] = df_filtered[value_col].apply(parse_value)
        
        # Convert Age and Apappearances to numeric values
        df_filtered['_age'] = pd.to_numeric(df_filtered[age_col], errors='coerce')
        df_filtered['_apps'] = pd.to_numeric(df_filtered[apps_col], errors='coerce')
        
        # Apply filters
        filtered_df = df_filtered[
            (df_filtered['_price'] >= min_price) &
            (df_filtered['_price'] <= price_threshold) &
            (df_filtered['_apps'] >= min_apps) &
            (df_filtered['_age'] < max_age) &
            (df_filtered['_age'].notna()) &
            (df_filtered['_price'].notna())
        ].copy()
        
        # Check if filtered DataFrame is empty
        if filtered_df.empty:
            return f"<div><p> No players match the criteria. Try adjusting filters.</p></div>"
        
        # Detect offensive statistic columns
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
        
        # Find first matching column for each offensive statistic
        for standard_name, variations in offensive_candidates.items():
            matching_column = None
            for variation in variations:
                if variation.lower() in df_columns_lower:
                    matching_column = df.columns[df_columns_lower.index(variation.lower())]
                    break
            
            if matching_column:
                available_off[standard_name] = matching_column
        
        # Check that at least 3 offensive columns are found
        if len(available_off) < 3:
            raise ValueError(f"Insufficient offensive statistics columns detected. Found {len(available_off)}, need at least 3.")
        
        # Normalize the offensive stats
        for standard_name, actual_column in available_off.items():
            # Convert to numeric
            filtered_df[f'_numeric_{actual_column}'] = pd.to_numeric(filtered_df[actual_column], errors='coerce')
            
            # Apply normalization
            normalized_col_name = f'_norm_{actual_column}'
            filtered_df[normalized_col_name] = normalize(filtered_df[f'_numeric_{actual_column}'])
        
        # Define weights for offensive stats
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
        
        # Calculate weighted offensive score
        offensive_score = 0
        weight_sum = 0
        
        # For each available offensive column, multiply by its weight and sum
        for standard_name, actual_column in available_off.items():
            if standard_name in weights:
                normalized_col_name = f'_norm_{actual_column}'
                if normalized_col_name in filtered_df.columns:
                    weighted_value = filtered_df[normalized_col_name] * weights[standard_name]
                    offensive_score += weighted_value
                    weight_sum += weights[standard_name]
        
        # Handle case where no valid columns were found
        if weight_sum > 0:
            # Normalize by total weight to get final score (between 0 and 1)
            filtered_df['Offensive Score'] = offensive_score / weight_sum
        else:
            # If no weights applied, set all scores to 0
            filtered_df['Offensive Score'] = 0
        
        # Calculate tactical dimensions from offensive statistics
        filtered_df = calculate_tactical_dimensions(filtered_df, available_off)
        
        # Normalize tactical dimensions to 0-100 scale
        tactical_cols = ['Attacco', 'Pressing', 'Finalizzazione', 'Creatività']
        for col in tactical_cols:
            if col in filtered_df.columns:
                normalized = normalize(filtered_df[col])
                # Scale from [0, 1] to [0, 100]
                filtered_df[col] = normalized * 100
        
        # Apply age factor to _age column
        filtered_df['Age Factor'] = filtered_df['_age'].apply(age_factor)
        
        # Calculate Value Index: (Offensive Score * Age Factor) / (_price in millions)
        # Handle division by zero and invalid values
        valid_price = filtered_df['_price'].replace(0, np.inf)
        value_index_raw = (filtered_df['Offensive Score'] * filtered_df['Age Factor']) / (valid_price / 1_000_000)
        raw_value_index = value_index_raw.replace([np.inf, -np.inf], np.nan).fillna(0)
        
        # Normalize Value Index to ensure exactly one player has score 100 per price range
        # The best player in the current filter gets 100, others scale proportionally
        if len(raw_value_index) > 0:
            max_val = raw_value_index.max()
            if max_val > 0:
                # Scale all values relative to the maximum (which becomes 100)
                normalized_vi = (raw_value_index / max_val * 100).round(2)
                filtered_df['Value Index'] = normalized_vi.clip(upper=100)
            else:
                filtered_df['Value Index'] = 0
        else:
            filtered_df['Value Index'] = 0
        
        # Calculate Offensive Efficiency as (Goal Contributions per 90) / (Shots per 90)
        goal_contributions_col = None
        shots_col = None
        
        # Find the actual column names for Goal Contributions and Shots
        for standard_name, actual_column in available_off.items():
            if standard_name == 'Goal Contributions per 90':
                goal_contributions_col = actual_column
            elif standard_name == 'Shots per 90':
                shots_col = actual_column
        
        # If both columns are found, calculate efficiency
        if goal_contributions_col and shots_col:
            filtered_df['Offensive Efficiency'] = (
                filtered_df[goal_contributions_col] / filtered_df[shots_col]).replace([np.inf, -np.inf], np.nan)
        else:
            # If either column is missing, set efficiency to NaN
            filtered_df['Offensive Efficiency'] = np.nan
        
        # Sort by Value Index in descending order and keep top 20 rows
        sorted_df = filtered_df.sort_values('Value Index', ascending=False).head(20)
        
        # Build the output DataFrame with specified column order
        result_out = pd.DataFrame()
        
        # Add columns in specified order
        result_out['Name'] = sorted_df['Name']
        result_out['Club'] = sorted_df['Club']
        result_out['Age'] = sorted_df['_age']
        result_out['Guide Value'] = df.loc[sorted_df.index, value_col]  # Original string values
        result_out['Offensive Score'] = sorted_df['Offensive Score']
        result_out['Value Index'] = sorted_df['Value Index']
        result_out['Age Factor'] = sorted_df['Age Factor']
        result_out['Offensive Efficiency'] = sorted_df['Offensive Efficiency']
        
        # Add all the actual offensive statistic columns found
        for standard_name, actual_column in available_off.items():
            if actual_column in sorted_df.columns:
                result_out[standard_name] = sorted_df[actual_column]
        
        # Generate HTML table
        html_table = result_out.to_html(classes='table table-striped', border=0, index=False)
        
        # Create full HTML document with Bootstrap and custom CSS
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
  <style>
    body {{
      background-color: #0d1117;
      color: #c9d1d9;
    }}
    .table-striped {{
      background-color: #161b22;
      padding: 10px;
      color: #f5f5f5;
    }}
    .table-header {{
      background-color: #0d1117;
      color: #58a6ff;
      font-weight: bold;
    }}
    table {{
      border-collapse: collapse;
    }}
    th, td {{
      border: 1px solid #30363d;
      padding: 8px 12px;
      color: #f5f5f5;
    }}
    tr:nth-child(even) {{
      background-color: #1a1a1a;
    }}
    tr:nth-child(odd) {{
      background-color: #0d1117;
    }}
  </style>
</head>

<body>
<p>
    Filtered results using price range: {float(min_price):,.0f} € - {float(price_threshold):,.0f} €, minimum appearances: {int(min_apps)}, maximum age: {int(max_age)}.
    Found {len(result_out)} players matching criteria.
</p>

  {html_table}
</body>

</html>
"""
        
        # Test by printing first 100 characters to ensure it's valid
        print(html_content[:100])
        return html_content
        
    except Exception as e:
        error_message = f"<div><p> Error: {str(e)}</p></div>"
        return error_message

# Example usage (uncomment to use):
# if __name__ == "__main__":
#     result = analyze_csv("data.csv", 100000, 5, 30)
#     print(result)