# app.py
# Main entry point for the AI Time Series Assistant application
# Path: ai_time_series_assistant/app.py

import streamlit as st
from frontend.streamlit_app import create_streamlit_app

# Minimal hardcoded configuration
DEFAULT_CONFIG = {
    "api": {
        "base_url": "http://localhost:8000",
        "timeout": 10
    },
    "model_name": "gemini-2.5-flash",
    "temperature": 0.0,
    "max_tokens": 2000
}

def main():
    """
    Main entry point for the application.
    Initializes the Streamlit app and all necessary components.
    """
    # Use minimal hardcoded configuration
    config = DEFAULT_CONFIG

    # Initialize and run the Streamlit app
    create_streamlit_app(config)


if __name__ == "__main__":
    main()
