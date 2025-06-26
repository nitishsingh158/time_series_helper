# Visualization components for Streamlit
# Path: ai_time_series_assistant/frontend/components/visualization.py

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Any
from backend.visualization.charts import TimeSeriesCharts
from backend.analysis.anomaly_detection import AnomalyDetector
import logging

logger = logging.getLogger(__name__)


def create_visualization_panel(config: Dict[str, Any]) -> None:
    """
    Create the visualization panel component

    Args:
        config (Dict[str, Any]): Application configuration
    """
    st.header("Data Visualization")

    # Check if data is available
    if "data" not in st.session_state or st.session_state.data is None:
        st.info("Upload a CSV file to see visualizations here.")
        return

    # Get the data to use (processed or original)
    df = st.session_state.data

    # Get selected column and visualization type
    columns = st.session_state.selected_columns
    viz_type = st.session_state.visualization_type

    # Create charts object
    charts = TimeSeriesCharts()

    # Show different visualizations based on selected type
    if viz_type == "line_chart":
        display_line_chart(df, columns, charts)

    elif viz_type == "anomaly_detection":
        display_anomaly_detection(df, columns, charts)


def display_line_chart(
    df: pd.DataFrame, columns: str, charts: TimeSeriesCharts
) -> None:
    """
    Display a line chart visualization

    Args:
        df (pd.DataFrame): Time series data
        column (str): Column name to visualize
        charts (TimeSeriesCharts): Charts object for creating visualizations
    """

    # Create line chart
    fig = charts.create_multi_line_chart(
        df,
        columns,
    )

    # Display the chart
    st.plotly_chart(fig, use_container_width=True)


def display_anomaly_detection(
    df: pd.DataFrame, column: str, charts: TimeSeriesCharts
) -> None:
    """
    Display anomaly detection visualization

    Args:
        df (pd.DataFrame): Time series data
        column (str): Column name to visualize
        charts (TimeSeriesCharts): Charts object for creating visualizations
    """

    # Get z-score threshold from session state or use default
    z_score_threshold = st.session_state.get("z_score_threshold", 3.0)

    # Create anomaly detector
    detector = AnomalyDetector({"z_score_threshold": z_score_threshold})

    # Detect anomalies
    with st.spinner("Detecting anomalies..."):
        anomalies = detector.detect_multiple_anomalies(df)

    # Create anomaly chart
    fig = charts.create_anomaly_chart(
        df,
        column,
        anomalies,
    )

    # Display the chart
    st.plotly_chart(fig, use_container_width=True)
