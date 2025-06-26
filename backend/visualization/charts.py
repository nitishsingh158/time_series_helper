# Chart visualization module

import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List, Optional, Tuple
import numpy as np


class TimeSeriesCharts:
    """
    Class for creating time series visualizations
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the charts class

        Args:
            config (Dict[str, Any], optional): Configuration parameters
        """
        self.config = config or {}
        self.default_height = self.config.get("default_height", 500)
        self.default_width = self.config.get("default_width", 800)
        self.colors = {
            "primary": "#1f77b4",  # Blue
            "secondary": "#ff7f0e",  # Orange
            "anomaly": "#d62728",  # Red
            "trend": "#2ca02c",  # Green
            "seasonal": "#9467bd",  # Purple
            "residual": "#8c564b",  # Brown
            "highlight": "#e377c2",  # Pink
        }

    def create_line_chart(
        self,
        df: pd.DataFrame,
        column: str,
        title: str = "",
        height: int = None,
        width: int = None,
    ) -> go.Figure:
        """
        Create a line chart for time series data

        Args:
            df (pd.DataFrame): Time series data
            column (str): Column name to visualize
            title (str): Chart title
            height (int, optional): Chart height
            width (int, optional): Chart width

        Returns:
            go.Figure: Plotly figure object
        """
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in dataframe")

        height = height or self.default_height
        width = width or self.default_width

        # Create figure
        fig = go.Figure()

        # Add line trace
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[column],
                mode="lines",
                name=column,
                line=dict(color=self.colors["primary"], width=2),
            )
        )

        # Set layout
        fig.update_layout(
            title=title or f"Time Series: {column}",
            xaxis_title="Time",
            yaxis_title=column,
            height=height,
            width=width,
            hovermode="x unified",
            template="plotly_white",
        )

        return fig

    def create_anomaly_chart(
        self,
        df: pd.DataFrame,
        columns: List[str],
        anomalies: pd.Series,
        title: str = "",
        height: int = None,
        width: int = None,
    ) -> px.line:
        """
        Create a chart highlighting anomalies in time series data by extending the multi-line chart

        Args:
            df (pd.DataFrame): Time series data
            column (str): Column name to visualize
            anomalies (pd.Series): Boolean series indicating anomalies
            title (str): Chart title
            height (int, optional): Chart height
            width (int, optional): Chart width

        Returns:
            px.line: Plotly Express line chart with anomalies marked
        """

        # Reuse the multi-line chart function to create the base chart
        fig = self.create_multi_line_chart(
            df=df,
            columns=columns,
            title=title,
            height=height,
            width=width,
        )

        # Add vertical lines for anomalies
        if anomalies is not None and any(anomalies):
            # Get timestamps where anomalies is True
            anomaly_timestamps = df.index[anomalies]

            # Add vertical lines for each anomaly
            for timestamp in anomaly_timestamps:
                fig.add_vline(
                    x=timestamp,
                    line_color=self.colors["anomaly"],
                    line_width=1,
                    line_dash="dash",
                    opacity=0.7,
                )

        return fig

    def create_multi_line_chart(
        self,
        df: pd.DataFrame,
        columns: List[str] = None,
        title: str = "",
        height: int = None,
        width: int = None,
    ) -> px.line:
        """
        Create a multi-line chart for multiple time series using plotly.express

        Args:
            df (pd.DataFrame): Time series data
            columns (List[str], optional): Column names to visualize
            title (str): Chart title
            height (int, optional): Chart height
            width (int, optional): Chart width

        Returns:
            px.line: Plotly Express line chart
        """
        height = height or self.default_height
        width = width or self.default_width

        # Create a long-format dataframe for plotly express
        plot_df = df[columns].copy()
        plot_df.index.name = "timestamp"  # Name the index
        plot_df = plot_df.reset_index().melt(
            id_vars="timestamp",
            value_vars=columns,
            var_name="variable",
            value_name="value",
        )

        # Create figure with plotly express
        fig = px.line(
            plot_df,
            x="timestamp",
            y="value",
            color="variable",
            title=title,
            height=height,
            width=width,
            template="plotly_white",
        )

        # Update layout
        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Value",
            hovermode="x unified",
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
        )

        return fig

    def create_dashboard(
        self,
        df: pd.DataFrame,
        column: str,
        window: int = 24,
        anomalies: pd.Series = None,
        components: Dict[str, pd.Series] = None,
    ) -> Dict[str, go.Figure]:
        """
        Create a comprehensive dashboard with multiple charts

        Args:
            df (pd.DataFrame): Time series data
            column (str): Primary column name to visualize
            window (int): Rolling window size
            anomalies (pd.Series, optional): Boolean series indicating anomalies
            components (Dict[str, pd.Series], optional): Decomposed time series components

        Returns:
            Dict[str, go.Figure]: Dictionary of plotly figures
        """
        dashboard = {}

        # 1. Time series with anomalies
        if anomalies is not None and any(anomalies):
            dashboard["anomaly_chart"] = self.create_anomaly_chart(
                df, column, anomalies, title=f"Anomaly Detection: {column}"
            )
        else:
            dashboard["main_chart"] = self.create_line_chart(
                df, column, title=f"Time Series: {column}"
            )

        # 2. Statistics chart
        dashboard["stats_chart"] = self.create_statistics_chart(
            df,
            column,
            window,
            stats=["mean", "std"],
            title=f"Rolling Statistics: {column} (Window: {window})",
        )

        # 3. Seasonality chart if components available
        if components is not None:
            dashboard["seasonality_chart"] = self.create_seasonality_chart(
                components, title=f"Time Series Decomposition: {column}"
            )

        # 4. Correlation heatmap
        dashboard["correlation"] = self.create_heatmap(
            df, title="Feature Correlation Matrix"
        )

        # 5. Autocorrelation for the column
        dashboard["autocorrelation"] = self.create_heatmap(
            df, column, title=f"Autocorrelation: {column}"
        )

        return dashboard
