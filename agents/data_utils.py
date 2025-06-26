"""
Data access utilities for the Graph Chat Agent
Path: ai_time_series_assistant/agents/data_utils.py
"""

import logging
from backend.data.api_connector import APIConnector

logger = logging.getLogger(__name__)


class DataAccessManager:
    """Manages data access components for the chat agent"""

    def __init__(self):
        self.api_connector = APIConnector()

    def get_components(self):
        """Return initialized data access components"""
        return self.api_connector
