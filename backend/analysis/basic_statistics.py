# Basic statistics module - Simplified pseudocode

import pandas as pd
from typing import Dict

class BasicStatistics:
    """
    Simplified statistics calculator for time series data
    """

    def calculate_stats(self, series: pd.Series, column: str) -> Dict[str, float]:
        """
        Calculate basic statistics for a column
        
        Pseudocode:
        1. Calculate min, max, mean, std, median
        2. Return as dictionary
        """
        return {
            "min": series.min(),
            "max": series.max(), 
            "mean": series.mean(),
            "std": series.std(),
            "median": series.median(),
        }
