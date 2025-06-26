"""
Configuration settings loader
"""
import json
import os
from typing import Dict, Any
from pathlib import Path


def load_api_config() -> Dict[str, Any]:
    """Load API configuration from JSON file"""
    config_path = Path(__file__).parent / "api_config.json"
    
    if not config_path.exists():
        raise FileNotFoundError(f"API config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        return json.load(f)


# Load config once at module level
API_CONFIG = load_api_config()