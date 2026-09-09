# Test script for scout_app functionality

import sys
import os
import traceback

# Add current directory to path so we can import scout_app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scout_app import analyze_csv
import pandas as pd

if __name__ == "__main__":
    test_data = """Name,Club,Age,Guide Value,Appearances,Goal Contributions per 90,xG per 90,xA per 90,Shots on Target per 90,Shots per 90
Player1,Barcelona,25,€1.2M,30,1.5,0.8,0.5,1.5,2.0
Player2,Real Madrid,22,€2.5M,40,2.0,1.2,0.8,2.0,2.5
Player3,Chelsea,27,€800K,25,0.8,0.5,0.3,1.0,1.2"""

    with open("test_data.csv", "w", encoding="utf-8") as f:
        f.write(test_data)
    
    try:
        result = analyze_csv("test_data.csv", 5000000, 20, 30)
        if "Error:" in result:
            print("Analyze returned error:", result)
        else:
            print("Success! HTML length:", len(result))
            print(result[:300])
    except Exception as e:
        traceback.print_exc()
    
    if os.path.exists("test_data.csv"):
        os.remove("test_data.csv")
