# Main Streamlit application - Simplified for API-only access

import streamlit as st
from typing import Dict, Any
from frontend.components.chat_interface import create_chat_interface
from frontend.components.visualization import create_visualization_panel
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_streamlit_app(config: Dict[str, Any]) -> None:
    """
    Create and configure the Streamlit application for API-based data access

    Args:
        config (Dict[str, Any]): Application configuration
    """
    # Configure the page
    st.set_page_config(
        page_title="AI Time Series Assistant", page_icon="📊", layout="wide"
    )

    # Initialize session state for API data
    if "api_data" not in st.session_state:
        st.session_state.api_data = {}

    # App title
    st.title("AI Time Series Assistant")
    st.markdown("*Connect to IoT data via API - Ask about available machines and data*")

    # Create sidebar for information
    with st.sidebar:
        create_sidebar(config)

    # Create the main chat interface
    create_chat_interface(config)


def create_sidebar(config: Dict[str, Any]) -> None:
    """
    Create the sidebar with API information and status

    Args:
        config (Dict[str, Any]): Application configuration
    """
    st.sidebar.header("API Data Access")
    
    # Show API status
    st.sidebar.markdown("🔗 **Connected to IoT API**")
    st.sidebar.markdown("📍 Test Server: `localhost:8000`")
    
    # Show loaded data info
    if st.session_state.api_data:
        st.sidebar.header("Loaded Data")
        for machine_id, df in st.session_state.api_data.items():
            st.sidebar.markdown(f"**{machine_id}**: {len(df)} data points")
    else:
        st.sidebar.info("No data loaded yet. Ask me to 'show available machines' to get started!")

    # Add information section
    st.sidebar.header("About")
    st.sidebar.info(
        """
        This application connects to IoT APIs to analyze time series data using natural language.
        
        **Available Commands:**
        - "Show me available machines"
        - "Get data for MACHINE-001" 
        - "What are the statistics for pressure?"
        
        **Features:**
        - Real-time API data access
        - Intelligent caching
        - Basic statistical analysis
        """
    )


