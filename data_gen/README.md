# Asset Data Server

This is a simple FastAPI server that generates mock asset data and time series data for testing and development purposes.

## Features

-   Provides a list of assets with their properties (id, key, name, location, classification)
-   Generates realistic time series data for each asset
-   Configurable time ranges and intervals
-   RESTful API with OpenAPI documentation

## API Endpoints

### GET /scan

Returns a list of all available assets with their properties:

-   id: Unique numeric identifier
-   key: Unique alphanumeric identifier
-   name: Human-readable name
-   location: Physical location of the asset
-   classification: Type of asset (mechanical, electrical, equipment, etc.)

Example response:

```json
[
    {
        "id": 1,
        "key": "A1B2C3D4",
        "name": "Temperature Sensor 1",
        "location": "Building-A Floor-2",
        "classification": "sensor"
    },
    {
        "id": 2,
        "key": "E5F6G7H8",
        "name": "Pressure Sensor 2",
        "location": "Building-B Floor-1",
        "classification": "mechanical"
    }
]
```

### GET /timeseries

Returns time series data for a specific asset.

Query parameters:

-   `asset_key` (required): The alphanumeric key of the asset
-   `start_date` (optional): Start timestamp in Unix format
-   `end_date` (optional): End timestamp in Unix format
-   `time_interval` (optional): Time interval in minutes (currently only 5 min supported)

Example response:

```json
{
    "asset_id": "A1B2C3D4",
    "data": [
        {
            "flow": {
                "1623456789": 75.23,
                "1623456723": 73.22
            }
        },
        {
            "pressure": {
                "1623456789": 75.23,
                "1623456723": 73.22
            }
        },
        {
            "vibration": {
                "1623456789": 75.23,
                "1623456723": 73.22
            }
        },
        {
            "energy_consumption": {
                "1623456789": 75.23,
                "1623456723": 73.22
            }
        }
    ]
}
```

## Running the Server

To start the server:

```bash
python start_server_refactored.py
```

The server will run on http://localhost:8000 by default.

## API Documentation

Once the server is running, you can access the auto-generated API documentation:

-   Swagger UI: http://localhost:8000/docs
-   ReDoc: http://localhost:8000/redoc
