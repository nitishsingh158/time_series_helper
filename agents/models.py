"""
Pydantic models for the Graph Chat Agent
Path: ai_time_series_assistant/agents/models.py
"""

from typing import Dict, Any, List, Optional, Literal
from dataclasses import dataclass
from pydantic import BaseModel, Field
import pandas as pd


class SupervisorDecision(BaseModel):
    """Structured response from supervisor agent"""

    intent: Literal[
        "tool_required", "conversation", "help", "unclear", "error"
    ] = Field(description="The determined intent of the user message")
    confidence: float = Field(
        description="Confidence level (0.0-1.0) in the intent determination",
        ge=0.0,
        le=1.0,
    )
    needs_rewrite: bool = Field(
        description="Whether the message needs clarification/rewriting"
    )
    reasoning: str = Field(description="Brief explanation of the decision")


class RewriterResponse(BaseModel):
    """Structured response from rewriter agent"""

    rewritten_message: str = Field(
        description="The clarified and rewritten user message"
    )
    clarifications_added: List[str] = Field(
        description="List of clarifications that were added", default_factory=list
    )
    confidence: float = Field(
        description="Confidence in the rewrite quality", ge=0.0, le=1.0
    )



class ChatState(BaseModel):
    """State that flows through the graph"""

    model_config = {"arbitrary_types_allowed": True}
    # Input
    original_message: str

    # Processing state
    current_message: str = ""
    supervisor_decision: Optional[SupervisorDecision] = None
    rewriter_response: Optional[RewriterResponse] = None
    tool_results: Dict[str, Any] = Field(default_factory=dict)

    # Output
    final_response: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)
    # Flow control
    next_node: str = ""
    iteration_count: int = 0
    max_iterations: int = 3


@dataclass
class AgentResponse:
    """Standardized response structure from agents"""

    text: str
    visualizations: List = None
    data: Optional[pd.DataFrame] = None
    metadata: Dict[str, Any] = None
