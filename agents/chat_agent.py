# Graph-based Chat Agent with Supervisor Pattern
# Path: ai_time_series_assistant/agents/chat_agent.py
# Purpose:GraphChatAgent should focus on understanding user intent and preparing
# clear requests for the analytics agent, not doing the actual analytics.

from typing import Dict, Any, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langgraph.graph import StateGraph, END
import logging

# Import our extracted modules
from .models import ChatState, AgentResponse

# ChatAgentTools removed - using generic tools now
from .graph_nodes import GraphNodes
from .prompts import get_prompts
from .data_utils import DataAccessManager

logger = logging.getLogger(__name__)


class GraphChatAgent:
    """
    Graph-based chat agent using LangGraph with supervisor pattern
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the graph chat agent

        Args:
            config (Dict[str, Any]): Agent configuration including pre-initialized LLM
        """
        # Extract pre-initialized components from factory
        self.config = config
        self.llm: ChatGoogleGenerativeAI = config["llm"]
        self.memory: ConversationBufferMemory = config["memory"]

        # Graph components
        self.graph: Optional[StateGraph] = None
        self.compiled_graph = None

        self.data_manager = DataAccessManager()
        self.tools_manager = None
        self.graph_nodes = None

        # Prompts
        self.prompts: Dict[str, str] = {}

        # State
        self.is_initialized = False

    def create_prompts(self) -> None:
        """Initialize all prompt templates used throughout the agent"""
        self.prompts = get_prompts()
        logger.info("Prompts initialized successfully")

    def initialize(self) -> None:
        """Initialize the graph and all components"""
        try:
            # Create prompts first
            self.create_prompts()

            # Initialize graph nodes with no specific tools (using generic API calls)
            self.graph_nodes = GraphNodes(
                self.llm, self.memory, self.prompts, tools=None
            )

            # Build graph
            self._build_graph()

            # Compile graph
            self.compiled_graph = self.graph.compile()

            self.is_initialized = True
            logger.info("GraphChatAgent initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize GraphChatAgent: {e}")
            raise

    def _build_graph(self) -> None:
        """Build the LangGraph workflow"""

        # Create the graph
        workflow = StateGraph(ChatState)

        # Add nodes using graph_nodes
        workflow.add_node("supervisor", self.graph_nodes.supervisor_node)
        workflow.add_node("rewriter", self.graph_nodes.rewriter_node)
        workflow.add_node("tool_selector", self.graph_nodes.tool_selector_node)
        workflow.add_node(
            "response_generator", self.graph_nodes.response_generator_node
        )

        # Set entry point
        workflow.set_entry_point("supervisor")

        # Add conditional edges from supervisor
        workflow.add_conditional_edges(
            "supervisor",
            self.graph_nodes.supervisor_router,
            {
                "rewrite": "rewriter",
                "tools": "tool_selector",
                "respond": "response_generator",
                "end": END,
            },
        )

        # Add edges from rewriter back to supervisor
        workflow.add_edge("rewriter", "supervisor")

        # Tool selector goes to response generator for memory updates and metadata
        workflow.add_edge("tool_selector", "response_generator")

        # Add edge from response generator to end
        workflow.add_edge("response_generator", END)

        self.graph = workflow

    def process_message(
        self,
        message: str,
    ) -> AgentResponse:
        """
        Process a message through the graph

        Args:
            message (str): User message

        Returns:
            AgentResponse: Processed response
        """
        if not self.is_initialized:
            raise RuntimeError(
                "GraphChatAgent not initialized. Call initialize() first."
            )

        try:
            # Create initial state
            initial_state = ChatState(
                original_message=message,
            )

            # Run the graph
            final_state_dict = self.compiled_graph.invoke(initial_state)

            # Log final state for debugging
            logger.info(f"Final ChatState: {final_state_dict}")

            # Convert to AgentResponse
            return AgentResponse(
                text=final_state_dict.get("final_response", ""),
                visualizations=final_state_dict.get("visualizations", []),
                data=final_state_dict.get("data"),
                metadata=final_state_dict.get("metadata", {}),
            )

        except Exception as e:
            logger.error(f"Graph execution failed: {e}")
            return AgentResponse(
                text="I'm sorry, I encountered an error processing your request. Please try again.",
                metadata={"error": str(e), "type": "graph_execution_error"},
            )
