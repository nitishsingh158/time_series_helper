from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    """Analysis request with LLM confidence scoring"""

    intent: str = Field(
        description="Type of analysis requested: anomaly_detection, statistical_analysis, pattern_analysis, or correlation_analysis"
    )
    target_columns: List[str] = Field(
        description="List of measurements/columns to analyze (e.g., temperature, pressure, flow, vibration, energy_consumption)",
        default_factory=list,
    )
    asset_ids: List[str] = Field(
        description="List of specific asset IDs mentioned (e.g., MACHINE-001, SENSOR-A1)",
        default_factory=list,
    )
    time_range_description: str = Field(
        description="Time range mentioned in natural language (e.g., 'last 24 hours', 'this week', 'yesterday')",
        default="last week",
    )
    parameters: Dict[str, Any] = Field(
        description="Analysis-specific parameters like thresholds, window sizes",
        default_factory=dict,
    )
    confidence: float = Field(
        description="Confidence level (0.0-1.0) in parameter extraction accuracy",
        ge=0.0,
        le=1.0,
    )
    needs_clarification: bool = Field(
        description="True if the request is too ambiguous to execute reliably"
    )
    clarification_message: Optional[str] = Field(
        description="Specific clarification message to show user when needs_clarification=True or confidence is low",
        default=None,
    )


@dataclass
class AnalysisResults:
    """
    Results from analysis operations
    """

    summary: str
    details: Dict[str, Any]
    visualizations: List[Dict[str, Any]]
    recommendations: List[str]
    metadata: Dict[str, Any]


@dataclass
class AssetInfo:
    """
    Information about an asset in the system
    """

    asset_id: str
    asset_type: str
    location: str
    status: str
    available_measurements: List[str]
    description: Optional[str] = None
