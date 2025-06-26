"""
Tool implementations using @tool decorator
"""

import requests
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Union
from config.settings import API_CONFIG
from langchain.tools import tool

logger = logging.getLogger(__name__)


@tool
def get_data() -> str:
    """Get list of all available assets/machines/sensors. Use this when user asks about available data or assets.

    Args:
        None - no arguments required
    """
    try:
        url = API_CONFIG["base_url"] + API_CONFIG["endpoints"]["scan"]["path"]
        response = requests.get(url)

        if response.status_code == 200:
            assets = response.json()
            total_assets = len(assets)

            if total_assets > 5:
                displayed_assets = assets[:5]
                result = f"Found {total_assets} available assets (showing first 5):\n"
                for asset in displayed_assets:
                    result += f"- {asset['key']}: {asset['name']} at {asset['location']} (Type: {asset['classification']})\n"
                result += f"\nMetadata: {total_assets - 5} additional assets available. Use get_timeseries with specific asset_key to access data."
            else:
                result = f"Found {total_assets} available assets:\n"
                for asset in assets:
                    result += f"- {asset['key']}: {asset['name']} at {asset['location']} (Type: {asset['classification']})\n"

            return result
        else:
            return f"Error fetching assets: HTTP {response.status_code}"
    except Exception as e:
        logger.error(f"get_data failed: {e}")
        return f"Error getting data: {str(e)}"


@tool
def get_timeseries(
    asset_key: str, start_date: Union[str, int] = None, end_date: Union[str, int] = None
) -> str:
    """Get time series data for a specific asset. Use this when user asks for data from a specific asset.

    Args:
        asset_key (str): REQUIRED - The unique identifier for the asset (e.g., 'ABC123')
        start_date (str|int): OPTIONAL - Start timestamp (Unix timestamp or YYYY-MM-DD format, defaults to 24 hours ago)
        end_date (str|int): OPTIONAL - End timestamp (Unix timestamp or YYYY-MM-DD format, defaults to now)
    """
    try:
        url = API_CONFIG["base_url"] + API_CONFIG["endpoints"]["timeseries"]["path"]
        params = {"asset_key": asset_key}

        # Handle default dates (24 hours ago to now)
        if start_date is None and end_date is None:
            end_timestamp = int(time.time())
            start_timestamp = end_timestamp - (24 * 60 * 60)  # 24 hours ago
        else:
            # Convert provided dates to Unix timestamps
            if start_date is not None:
                if isinstance(start_date, str):

                    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                    start_timestamp = int(start_dt.timestamp())
                else:
                    start_timestamp = start_date
            else:
                start_timestamp = int(time.time()) - (24 * 60 * 60)

            if end_date is not None:
                if isinstance(end_date, str):
                    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                    end_timestamp = int(end_dt.timestamp())
                else:
                    end_timestamp = end_date
            else:
                end_timestamp = int(time.time())

        params["start_date"] = start_timestamp
        params["end_date"] = end_timestamp

        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            measurements = data.get("data", [])

            if not measurements:
                return f"No data found for asset {asset_key}"

            result = f"Retrieved {len(measurements)} measurement types for asset {asset_key}:\n"
            for measurement in measurements:
                measurement_type = list(measurement.keys())[0]
                data_points = len(measurement[measurement_type])
                result += f"- {measurement_type}: {data_points} data points\n"

            return result
        else:
            return f"Error fetching timeseries: HTTP {response.status_code}"
    except Exception as e:
        logger.error(f"get_timeseries failed: {e}")
        return f"Error getting timeseries data: {str(e)}"


@tool
def get_statistics(asset_key: str, measurement_type: str = None) -> str:
    """Get statistical analysis of time series data for an asset.

    Args:
        asset_key (str): REQUIRED - The unique identifier for the asset
        measurement_type (str): OPTIONAL - Specific measurement to analyze (e.g., 'temperature', 'pressure')
    """
    try:
        # First get the timeseries data
        url = API_CONFIG["base_url"] + API_CONFIG["endpoints"]["timeseries"]["path"]
        params = {"asset_key": asset_key}
        response = requests.get(url, params=params)

        if response.status_code != 200:
            return f"Error fetching data for statistics: HTTP {response.status_code}"

        data = response.json()
        measurements = data.get("data", [])

        if not measurements:
            return f"No data available for asset {asset_key}"

        result = f"Statistical analysis for asset {asset_key}:\n"

        for measurement in measurements:
            measure_name = list(measurement.keys())[0]

            # Skip if specific measurement requested and this isn't it
            if measurement_type and measure_name != measurement_type:
                continue

            values = list(measurement[measure_name].values())
            if values:
                import statistics

                result += f"\n{measure_name}:\n"
                result += f"  - Count: {len(values)}\n"
                result += f"  - Mean: {statistics.mean(values):.2f}\n"
                result += f"  - Min: {min(values):.2f}\n"
                result += f"  - Max: {max(values):.2f}\n"
                result += f"  - Std Dev: {statistics.stdev(values):.2f}\n"

        return result
    except Exception as e:
        logger.error(f"get_statistics failed: {e}")
        return f"Error calculating statistics: {str(e)}"


@tool
def get_last_value(asset_key: str) -> str:
    """Get the most recent data point for a specific asset. Use this when user asks for current values or latest readings.

    Args:
        asset_key (str): REQUIRED - The unique identifier for the asset (e.g., 'ABC123')
    """
    try:
        url = API_CONFIG["base_url"] + API_CONFIG["endpoints"]["lastvalue"]["path"]
        params = {"asset_key": asset_key}
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()

            if not data:
                return f"No recent data found for asset {asset_key}"

            # Parse the LastValueResponse format: {asset_id, data, timestamp}
            asset_id = data.get("asset_id", asset_key)
            measurements = data.get("data", {})
            timestamp = data.get("timestamp")

            if not measurements:
                return f"No measurement data found for asset {asset_key}"

            result = f"Latest values for asset {asset_id}:\n"

            for measurement_type, value in measurements.items():
                result += f"- {measurement_type}: {value}\n"

            if timestamp:
                # Convert timestamp to readable format
                from datetime import datetime

                readable_time = datetime.fromtimestamp(timestamp).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                result += f"\nTimestamp: {readable_time}"

            return result
        else:
            return f"Error fetching last value: HTTP {response.status_code}"
    except Exception as e:
        logger.error(f"get_last_value failed: {e}")
        return f"Error getting last value: {str(e)}"


def get_tools():
    """Return list of available tools"""
    return [get_data, get_timeseries, get_statistics, get_last_value]
