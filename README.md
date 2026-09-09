# FM Scout Gem

This project provides tools for analyzing football player data and identifying value players based on various metrics.

## Requirements

The application requires the following Python packages:
- pandas (for data manipulation)
- numpy (for numerical operations)

Install dependencies using:
```bash
pip install pandas numpy
```

## Files

### scout_app.py
Main module containing functions for:
- Parsing currency values from strings (e.g., "€1.2M" to 1200000.0)
- Normalizing data series using min-max scaling
- Calculating age factors based on player age
- Automatically detecting column names in CSV files
- Analyzing CSV data and generating HTML reports

### requirements.txt
Lists the required Python packages.

### simple_test.py
Test script that verifies core functionality of scout_app functions.

## Usage

The main function `analyze_csv()` can be used to analyze football player data from a CSV file with specified filters:
```python
from scout_app import analyze_csv
result = analyze_csv("data.csv", price_threshold, min_apps, max_age)
```

## Features

- Automatic column name detection (handles variations in naming)
- Currency value parsing for different formats (M for millions, K for thousands)
- Age factor calculation that rewards younger players
- Offensive statistics normalization and weighting
- Value Index calculation combining offensive performance with age factors
- HTML output generation with Bootstrap styling