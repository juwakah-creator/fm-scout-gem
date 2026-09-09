#!/usr/bin/env python3
# Simple test for scout_app functionality

import sys
sys.path.append('.')

from scout_app import parse_value, normalize, age_factor
import pandas as pd
import numpy as np

def test_parse_value():
    print("Testing parse_value function...")
    assert parse_value("€1.2M") == 1200000.0
    assert parse_value("€50K") == 50000.0
    assert parse_value("€800K") == 800000.0
    print("parse_value tests passed!")

def test_age_factor():
    print("Testing age_factor function...")
    assert age_factor(18) == 2.0
    assert age_factor(22) == 1.6
    assert age_factor(25) == 1.3
    assert age_factor(30) == 1.0
    print("age_factor tests passed!")

def test_normalize():
    print("Testing normalize function...")
    series = pd.Series([1, 2, 3, 4, 5])
    normalized = normalize(series)
    # Should be between 0 and 1
    assert all(0 <= x <= 1 for x in normalized)
    print("normalize tests passed!")

if __name__ == "__main__":
    test_parse_value()
    test_age_factor() 
    test_normalize()
    print("All tests passed successfully!")