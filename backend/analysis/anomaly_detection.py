# Anomaly detection module - Simplified pseudocode
# Path: ai_time_series_assistant/backend/analysis/anomaly_detection.py

import pandas as pd
from typing import Dict, Any

class AnomalyDetector:
    """
    Simplified anomaly detection for time series data
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize with basic config"""
        self.config = config or {}

    def detect_simple_outliers(self, series: pd.Series) -> pd.Series:
        """
        Simple outlier detection using IQR method
        
        Pseudocode:
        1. Calculate Q1, Q3, IQR
        2. Find values outside 1.5*IQR bounds
        3. Return boolean series of outliers
        """
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        return (series < lower_bound) | (series > upper_bound)
