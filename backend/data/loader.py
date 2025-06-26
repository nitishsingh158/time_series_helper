# Data loading module - Simplified for API-only access

import pandas as pd
from typing import Dict, Any
from datetime import datetime

class DataLoader:
    """
    Simplified data loader for API-based time series data
    """
    
    def process_api_response(self, api_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Process API response into pandas DataFrame
        
        Args:
            api_data: Raw API response data
            
        Returns:
            pd.DataFrame: Processed time series data
        """
        # Convert API response to DataFrame
        df = pd.DataFrame(api_data['data'])
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        df.set_index('datetime', inplace=True)
        df.drop('timestamp', axis=1, inplace=True)
        return df
    
    def validate_time_series(self, df: pd.DataFrame) -> bool:
        """
        Validate if the dataframe is a proper time series
        
        Args:
            df (pd.DataFrame): Dataframe to validate
            
        Returns:
            bool: True if valid time series, False otherwise
        """
        # Basic validation: has datetime index and numeric columns
        return (hasattr(df.index, 'dtype') and 
                'datetime' in str(df.index.dtype) and
                len(df.select_dtypes(include=['number']).columns) > 0)