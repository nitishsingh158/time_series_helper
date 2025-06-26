# Data preprocessing module
# Path: ai_time_series_assistant/backend/data/preprocessor.py

from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional


class TimeSeriesPreprocessor:
    """
    Class for preprocessing time series data
    """

    def __init__(
        self,
    ):
        """
        Initialize the preprocessor

        Args:
            config (Optional[Dict[str, Any]]): Preprocessing configuration
        """
        self.scaler = MinMaxScaler()
        self.train_data_pct = 0.05

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values in the dataframe

        Args:
            df (pd.DataFrame): Dataframe with missing values

        Returns:
            pd.DataFrame: Dataframe with handled missing values
        """
        for col in df.columns:
            if df[col].isna().sum() > 0.20 * len(df):
                df.drop(columns=[col], inplace=True)
        df = df.ffill()
        return df

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess the time series data

        Args:
            df (pd.DataFrame): Raw time series data

        Returns:
            pd.DataFrame: Preprocessed data
        """
        #  handle missing values
        df = self.handle_missing_values(df)

        # convert columns to numeric data type if possible
        for col in df.columns:
            if df[col].dtype == "object":
                try:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                except ValueError:
                    pass

        # remove binary columns
        num_cols = df.select_dtypes(include=[np.number]).columns
        binary_cols = [col for col in num_cols if df[col].nunique() < 3]
        continuous_cols = [col for col in num_cols if col not in binary_cols]

        train_data = df[continuous_cols].iloc[0 : int(len(df) * self.train_data_pct)]

        # scale data
        scaler = self.scaler.fit(train_data)
        scaled_data = pd.DataFrame(
            scaler.transform(df[continuous_cols]),
            columns=train_data.columns,
            index=df.index,
        )

        #  pca
        if len(scaled_data.columns) > 3:
            scaled_train_data = pd.DataFrame(
                scaler.transform(train_data[continuous_cols]),
                columns=train_data.columns,
            )
            explained_variance_ratio = 0.90
            temp_pca = PCA()
            temp_pca.fit(scaled_train_data)
            explained_variance_ratio_cumsum = np.cumsum(
                temp_pca.explained_variance_ratio_
            )
            n_components = (
                np.argmax(explained_variance_ratio_cumsum >= explained_variance_ratio)
                + 1
            )

            if n_components > 3:
                n_components = 3

            pca = PCA(n_components=n_components)
            principal_components = pca.fit_transform(scaled_data)
            col_names = [f"PC_{i}" for i in range(n_components)]
            scaled_data = pd.DataFrame(
                principal_components, columns=col_names, index=scaled_data.index
            )

        return scaled_data
