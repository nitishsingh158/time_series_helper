from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
import logging

logger = logging.getLogger(__name__)


class DataSourceConfig:
    """Configuration for a data source"""

    def __init__(
        self,
        name: str,
        base_url: str,
        auth_type: str = "none",
        username: Optional[str] = None,
        password: Optional[str] = None,
        api_key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.name = name
        self.base_url = base_url
        self.auth_type = auth_type
        self.username = username
        self.password = password
        self.api_key = api_key
        self.headers = headers or {}


class DataSource(ABC):
    """Abstract base class for data sources"""

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the data source"""
        pass

    @abstractmethod
    def fetch_data(
        self,
        start_time: datetime,
        end_time: datetime,
        measurements: List[str],
        **kwargs,
    ) -> pd.DataFrame:
        """Fetch time series data from the source"""
        pass

    @abstractmethod
    def validate_connection(self) -> bool:
        """Validate the connection to the data source"""
        pass


class RESTDataSource(DataSource):
    """REST API data source implementation"""

    def __init__(self, config: DataSourceConfig):
        self.config = config
        self.session = requests.Session()
        self._setup_session()

    def _setup_session(self):
        """Setup the session with authentication and headers"""
        if self.config.auth_type == "basic":
            self.session.auth = HTTPBasicAuth(
                self.config.username, self.config.password
            )
        elif self.config.auth_type == "api_key":
            self.session.headers.update(
                {"Authorization": f"Bearer {self.config.api_key}"}
            )

        self.session.headers.update(self.config.headers)

    def connect(self) -> bool:
        """Establish connection to the REST API"""
        try:
            response = self.session.get(f"{self.config.base_url}/docs")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to connect to {self.config.name}: {str(e)}")
            return False

    def fetch_data(
        self,
        start_time: datetime,
        end_time: datetime,
        measurements: List[str],
        **kwargs,
    ) -> pd.DataFrame:
        """
        Fetch time series data from the REST API

        Args:
            start_time: Start time for data fetch
            end_time: End time for data fetch
            measurements: List of measurements to fetch
            **kwargs: Additional parameters for the API request

        Returns:
            DataFrame containing the time series data
        """
        try:
            params = {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "measurements": ",".join(measurements),
                **kwargs,
            }

            response = self.session.get(
                f"{self.config.base_url}/timeseries", params=params
            )
            response.raise_for_status()

            data = response.json()
            df = pd.DataFrame(data)
            df["datetime"] = pd.to_datetime(df["datetime"])
            df.set_index("datetime", inplace=True)

            return df

        except Exception as e:
            logger.error(f"Failed to fetch data from {self.config.name}: {str(e)}")
            raise

    def validate_connection(self) -> bool:
        """Validate the connection to the REST API"""
        return self.connect()


class APIConnector:
    """Main API connector class for managing multiple data sources"""

    def __init__(self):
        self.sources: Dict[str, DataSource] = {}

    def add_source(self, source: DataSource, name: str):
        """Add a new data source"""
        self.sources[name] = source

    def get_source(self, name: str) -> Optional[DataSource]:
        """Get a data source by name"""
        return self.sources.get(name)

    def fetch_data(
        self,
        source_name: str,
        start_time: datetime,
        end_time: datetime,
        measurements: List[str],
        **kwargs,
    ) -> pd.DataFrame:
        """
        Fetch data from a specific source

        Args:
            source_name: Name of the data source
            start_time: Start time for data fetch
            end_time: End time for data fetch
            measurements: List of measurements to fetch
            **kwargs: Additional parameters for the API request

        Returns:
            DataFrame containing the time series data
        """
        source = self.get_source(source_name)
        if not source:
            raise ValueError(f"Data source '{source_name}' not found")

        return source.fetch_data(start_time, end_time, measurements, **kwargs)

    def validate_all_connections(self) -> Dict[str, bool]:
        """Validate connections to all data sources"""
        return {
            name: source.validate_connection() for name, source in self.sources.items()
        }
