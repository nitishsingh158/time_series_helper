from fastapi import FastAPI, HTTPException, Query, Path, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Set
import random
import time
from datetime import datetime, timedelta
import math
import string
from enum import Enum

app = FastAPI(title="Asset Data Server", version="2.0.0")

# Enums for validation
class Classification(str, Enum):
    MECHANICAL = "mechanical"
    ELECTRICAL = "electrical"
    EQUIPMENT = "equipment"
    SENSOR = "sensor"
    HVAC = "hvac"

class MeasurementType(str, Enum):
    FLOW = "flow"
    PRESSURE = "pressure"
    VIBRATION = "vibration"
    ENERGY_CONSUMPTION = "energy_consumption"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    SPEED = "speed"
    TORQUE = "torque"

# Data models
class Asset(BaseModel):
    id: int
    key: str = Field(..., description="Unique alphanumeric identifier")
    name: str
    location: str
    classification: Classification


class TimeseriesResponse(BaseModel):
    asset_id: str
    data: List[Dict[str, Dict[str, float]]]

class LastValueResponse(BaseModel):
    asset_id: str
    data: Dict[str, float]
    timestamp: int

# Mock data configuration
ASSET_COUNT = 15
CLASSIFICATIONS = [c.value for c in Classification]
BUILDINGS = ["Building-A", "Building-B", "Building-C"]
FLOORS = ["Floor-1", "Floor-2", "Floor-3", "Floor-4"]
SENSOR_TYPES = ["temperature", "pressure", "flow", "vibration", "energy"]

# Data ranges
FLOW_RANGE = (0, 100)  # L/min
PRESSURE_RANGE = (0, 50)  # PSI
VIBRATION_RANGE = (0, 10)  # mm/s
ENERGY_RANGE = (0, 1000)  # kWh
TEMPERATURE_RANGE = (10, 40)  # °C
HUMIDITY_RANGE = (20, 80)  # %
SPEED_RANGE = (0, 3000)  # RPM
TORQUE_RANGE = (0, 200)  # Nm

# Measurement availability by classification
CLASSIFICATION_MEASUREMENTS = {
    "mechanical": ["flow", "pressure", "vibration", "speed", "torque"],
    "electrical": ["energy_consumption", "temperature"],
    "equipment": ["flow", "pressure", "vibration", "energy_consumption", "speed", "torque"],
    "sensor": ["temperature", "humidity", "pressure", "flow"],
    "hvac": ["temperature", "humidity", "flow", "energy_consumption"]
}

# Time configuration
INTERVAL_MINUTES = 5
MONTHS_SPAN = 3

def generate_alphanumeric_key(length=8):
    """Generate a random alphanumeric key"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_assets() -> List[Asset]:
    """Generate mock asset data"""
    assets = []
    
    # Generate sensor assets
    for i in range(1, ASSET_COUNT + 1):
        sensor_type = random.choice(SENSOR_TYPES)
        classification = random.choice(CLASSIFICATIONS)
        
        asset = Asset(
            id=i,
            key=generate_alphanumeric_key(),
            name=f"{sensor_type.capitalize()} Sensor {i}",
            location=f"{random.choice(BUILDINGS)} {random.choice(FLOORS)}",
            classification=classification
        )
        assets.append(asset)
    
    return assets

def get_asset_by_key(asset_key: str) -> Optional[Asset]:
    """Get asset by its key"""
    for asset in ASSETS:
        if asset.key == asset_key:
            return asset
    return None

def generate_timeseries_data(
    asset_key: str, 
    start_timestamp: int, 
    end_timestamp: int,
    measurements: Optional[List[str]] = None
) -> List[Dict[str, Dict[str, float]]]:
    """Generate mock timeseries data for an asset within the specified time range"""
    # Get the asset to determine its classification
    asset = get_asset_by_key(asset_key)
    if not asset:
        return []
        
    # Determine which measurements to include based on classification
    available_measurements = CLASSIFICATION_MEASUREMENTS.get(asset.classification, [])
    
    # Filter by requested measurements if provided
    if measurements:
        available_measurements = [m for m in available_measurements if m in measurements]
    
    # If no measurements are available or requested, return empty data
    if not available_measurements:
        return []
    
    # Set random seed based on asset_key for consistent data per asset
    random.seed(hash(asset_key))
    
    # Generate base values for this asset (each asset has different characteristics)
    base_values = {
        "flow": random.uniform(FLOW_RANGE[0] + 20, FLOW_RANGE[1] - 20) if "flow" in available_measurements else None,
        "pressure": random.uniform(PRESSURE_RANGE[0] + 10, PRESSURE_RANGE[1] - 10) if "pressure" in available_measurements else None,
        "vibration": random.uniform(VIBRATION_RANGE[0] + 1, VIBRATION_RANGE[1] - 2) if "vibration" in available_measurements else None,
        "energy_consumption": random.uniform(ENERGY_RANGE[0] + 100, ENERGY_RANGE[1] - 200) if "energy_consumption" in available_measurements else None,
        "temperature": random.uniform(TEMPERATURE_RANGE[0] + 5, TEMPERATURE_RANGE[1] - 5) if "temperature" in available_measurements else None,
        "humidity": random.uniform(HUMIDITY_RANGE[0] + 10, HUMIDITY_RANGE[1] - 10) if "humidity" in available_measurements else None,
        "speed": random.uniform(SPEED_RANGE[0] + 500, SPEED_RANGE[1] - 500) if "speed" in available_measurements else None,
        "torque": random.uniform(TORQUE_RANGE[0] + 50, TORQUE_RANGE[1] - 50) if "torque" in available_measurements else None
    }
    
    # Collect all data points first
    all_data_points = {}
    for measurement in available_measurements:
        all_data_points[measurement] = {}
    
    current_timestamp = start_timestamp
    
    while current_timestamp <= end_timestamp:
        # Add some realistic variation using sine waves and random noise
        time_factor = (current_timestamp - start_timestamp) / (24 * 3600)  # Days since start
        
        # Flow with daily cycle and random variation
        if "flow" in available_measurements:
            flow = base_values["flow"] + 15 * math.sin(time_factor * 2 * math.pi / 7) + random.uniform(-10, 10)
            flow = max(FLOW_RANGE[0], min(FLOW_RANGE[1], flow))
            all_data_points["flow"][str(current_timestamp)] = round(flow, 2)
        
        # Pressure with some correlation to flow
        if "pressure" in available_measurements:
            if "flow" in available_measurements:
                flow_val = all_data_points["flow"][str(current_timestamp)]
                pressure = base_values["pressure"] + (flow_val - base_values["flow"]) * 0.3 + random.uniform(-5, 5)
            else:
                pressure = base_values["pressure"] + random.uniform(-5, 5)
            pressure = max(PRESSURE_RANGE[0], min(PRESSURE_RANGE[1], pressure))
            all_data_points["pressure"][str(current_timestamp)] = round(pressure, 2)
        
        # Vibration with occasional spikes
        if "vibration" in available_measurements:
            vibration = base_values["vibration"] + random.uniform(-1, 1)
            if random.random() < 0.05:  # 5% chance of spike
                vibration += random.uniform(2, 4)
            vibration = max(VIBRATION_RANGE[0], min(VIBRATION_RANGE[1], vibration))
            all_data_points["vibration"][str(current_timestamp)] = round(vibration, 2)
        
        # Energy consumption with daily pattern
        if "energy_consumption" in available_measurements:
            energy = base_values["energy_consumption"] + 200 * math.sin(time_factor * 2 * math.pi) + random.uniform(-50, 50)
            energy = max(ENERGY_RANGE[0], min(ENERGY_RANGE[1], energy))
            all_data_points["energy_consumption"][str(current_timestamp)] = round(energy, 2)
            
        # Temperature with daily pattern
        if "temperature" in available_measurements:
            temp = base_values["temperature"] + 5 * math.sin(time_factor * 2 * math.pi) + random.uniform(-2, 2)
            temp = max(TEMPERATURE_RANGE[0], min(TEMPERATURE_RANGE[1], temp))
            all_data_points["temperature"][str(current_timestamp)] = round(temp, 2)
            
        # Humidity with inverse correlation to temperature
        if "humidity" in available_measurements:
            if "temperature" in available_measurements:
                temp_val = all_data_points["temperature"][str(current_timestamp)]
                humidity = base_values["humidity"] - (temp_val - base_values["temperature"]) * 2 + random.uniform(-5, 5)
            else:
                humidity = base_values["humidity"] + random.uniform(-5, 5)
            humidity = max(HUMIDITY_RANGE[0], min(HUMIDITY_RANGE[1], humidity))
            all_data_points["humidity"][str(current_timestamp)] = round(humidity, 2)
            
        # Speed with occasional variations
        if "speed" in available_measurements:
            speed = base_values["speed"] + random.uniform(-100, 100)
            if random.random() < 0.1:  # 10% chance of significant change
                speed += random.uniform(-300, 300)
            speed = max(SPEED_RANGE[0], min(SPEED_RANGE[1], speed))
            all_data_points["speed"][str(current_timestamp)] = round(speed, 2)
            
        # Torque with correlation to speed
        if "torque" in available_measurements:
            if "speed" in available_measurements:
                speed_val = all_data_points["speed"][str(current_timestamp)]
                torque = base_values["torque"] + (speed_val - base_values["speed"]) * 0.05 + random.uniform(-10, 10)
            else:
                torque = base_values["torque"] + random.uniform(-10, 10)
            torque = max(TORQUE_RANGE[0], min(TORQUE_RANGE[1], torque))
            all_data_points["torque"][str(current_timestamp)] = round(torque, 2)
        
        # Move to next interval (5 minutes)
        current_timestamp += INTERVAL_MINUTES * 60
    
    # Convert to the required format: list of dicts, each containing one measurement type
    result = []
    for measurement in available_measurements:
        if all_data_points[measurement]:
            result.append({measurement: all_data_points[measurement]})
    
    return result

def get_default_time_range():
    """Get default start and end timestamps for 3 months of data"""
    end_time = datetime.now()
    start_time = end_time - timedelta(days=MONTHS_SPAN * 30)  # Approximate 3 months
    return int(start_time.timestamp()), int(end_time.timestamp())

# Generate assets once at startup
ASSETS = generate_assets()

@app.get("/")
async def root():
    return {
        "message": "Asset Data Server",
        "endpoints": {
            "scan": "/scan - Get list of available assets",
            "timeseries": "/timeseries - Get timeseries data for an asset",
            "lastvalue": "/lastvalue - Get the most recent data point for an asset"
        }
    }

@app.get("/scan", response_model=List[Asset])
async def get_assets():
    """Get list of all available assets"""
    return ASSETS

@app.get("/timeseries", response_model=TimeseriesResponse)
async def get_timeseries(
    asset_key: str = Query(..., description="Asset key to get data for"),
    start_date: Optional[int] = Query(None, description="Start timestamp (Unix)"),
    end_date: Optional[int] = Query(None, description="End timestamp (Unix)"),
    time_interval: Optional[int] = Query(5, description="Time interval in minutes (currently only 5 min supported)")
):
    """Get timeseries data for a specific asset"""
    
    # Validate asset exists
    asset_keys = [asset.key for asset in ASSETS]
    if asset_key not in asset_keys:
        raise HTTPException(
            status_code=404, 
            detail=f"Asset with key {asset_key} not found. Available asset keys: {asset_keys}"
        )
    
    # Validate time interval
    if time_interval != 5:
        raise HTTPException(
            status_code=400,
            detail="Currently only 5-minute intervals are supported"
        )
    
    # Set default time range if not provided
    if start_date is None or end_date is None:
        default_start, default_end = get_default_time_range()
        start_date = start_date or default_start
        end_date = end_date or default_end
    
    # Validate time range
    if start_date >= end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date must be before end_date"
        )
    
    # Generate timeseries data
    data_points = generate_timeseries_data(asset_key, start_date, end_date)
    
    return TimeseriesResponse(
        asset_id=asset_key,
        data=data_points
    )

@app.get("/lastvalue", response_model=LastValueResponse)
async def get_last_value(
    asset_key: str = Query(..., description="Asset key to get the latest value for")
):
    """Get the most recent data point for a specific asset"""
    
    # Validate asset exists
    asset_keys = [asset.key for asset in ASSETS]
    if asset_key not in asset_keys:
        raise HTTPException(
            status_code=404, 
            detail=f"Asset with key {asset_key} not found. Available asset keys: {asset_keys}"
        )
    
    # Get the asset to determine its classification and available measurements
    asset = get_asset_by_key(asset_key)
    available_measurements = CLASSIFICATION_MEASUREMENTS.get(asset.classification, [])
    
    if not available_measurements:
        raise HTTPException(
            status_code=404,
            detail=f"No measurements available for asset {asset_key}"
        )
    
    # Generate current timestamp (now)
    current_timestamp = int(time.time())
    
    # Set random seed based on asset_key for consistent data per asset
    random.seed(hash(asset_key))
    
    # Generate base values for this asset (same as timeseries)
    base_values = {
        "flow": random.uniform(FLOW_RANGE[0] + 20, FLOW_RANGE[1] - 20) if "flow" in available_measurements else None,
        "pressure": random.uniform(PRESSURE_RANGE[0] + 10, PRESSURE_RANGE[1] - 10) if "pressure" in available_measurements else None,
        "vibration": random.uniform(VIBRATION_RANGE[0] + 1, VIBRATION_RANGE[1] - 2) if "vibration" in available_measurements else None,
        "energy_consumption": random.uniform(ENERGY_RANGE[0] + 100, ENERGY_RANGE[1] - 200) if "energy_consumption" in available_measurements else None,
        "temperature": random.uniform(TEMPERATURE_RANGE[0] + 5, TEMPERATURE_RANGE[1] - 5) if "temperature" in available_measurements else None,
        "humidity": random.uniform(HUMIDITY_RANGE[0] + 10, HUMIDITY_RANGE[1] - 10) if "humidity" in available_measurements else None,
        "speed": random.uniform(SPEED_RANGE[0] + 500, SPEED_RANGE[1] - 500) if "speed" in available_measurements else None,
        "torque": random.uniform(TORQUE_RANGE[0] + 50, TORQUE_RANGE[1] - 50) if "torque" in available_measurements else None
    }
    
    # Generate current values with some variation
    current_values = {}
    time_factor = current_timestamp / (24 * 3600)  # Current time factor
    
    for measurement in available_measurements:
        if measurement == "flow":
            value = base_values["flow"] + 15 * math.sin(time_factor * 2 * math.pi / 7) + random.uniform(-10, 10)
            value = max(FLOW_RANGE[0], min(FLOW_RANGE[1], value))
        elif measurement == "pressure":
            value = base_values["pressure"] + random.uniform(-5, 5)
            value = max(PRESSURE_RANGE[0], min(PRESSURE_RANGE[1], value))
        elif measurement == "vibration":
            value = base_values["vibration"] + random.uniform(-1, 1)
            if random.random() < 0.05:  # 5% chance of spike
                value += random.uniform(2, 4)
            value = max(VIBRATION_RANGE[0], min(VIBRATION_RANGE[1], value))
        elif measurement == "energy_consumption":
            value = base_values["energy_consumption"] + 200 * math.sin(time_factor * 2 * math.pi) + random.uniform(-50, 50)
            value = max(ENERGY_RANGE[0], min(ENERGY_RANGE[1], value))
        elif measurement == "temperature":
            value = base_values["temperature"] + 5 * math.sin(time_factor * 2 * math.pi) + random.uniform(-2, 2)
            value = max(TEMPERATURE_RANGE[0], min(TEMPERATURE_RANGE[1], value))
        elif measurement == "humidity":
            if "temperature" in current_values:
                value = base_values["humidity"] - (current_values["temperature"] - base_values["temperature"]) * 2 + random.uniform(-5, 5)
            else:
                value = base_values["humidity"] + random.uniform(-5, 5)
            value = max(HUMIDITY_RANGE[0], min(HUMIDITY_RANGE[1], value))
        elif measurement == "speed":
            value = base_values["speed"] + random.uniform(-100, 100)
            if random.random() < 0.1:  # 10% chance of significant change
                value += random.uniform(-300, 300)
            value = max(SPEED_RANGE[0], min(SPEED_RANGE[1], value))
        elif measurement == "torque":
            if "speed" in current_values:
                value = base_values["torque"] + (current_values["speed"] - base_values["speed"]) * 0.05 + random.uniform(-10, 10)
            else:
                value = base_values["torque"] + random.uniform(-10, 10)
            value = max(TORQUE_RANGE[0], min(TORQUE_RANGE[1], value))
        else:
            value = 0.0
        
        current_values[measurement] = round(value, 2)
    
    return LastValueResponse(
        asset_id=asset_key,
        data=current_values,
        timestamp=current_timestamp
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)