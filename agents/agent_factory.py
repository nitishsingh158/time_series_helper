# Agent factory module - Improved Version

from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI as ChatLLM
from langchain.memory import ConversationBufferMemory
from .chat_agent import GraphChatAgent
import os
import logging

logger = logging.getLogger(__name__)


class AgentFactory:
    """
    Factory class for creating and managing different types of agents
    Handles all infrastructure setup (LLM, memory, etc.)
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the agent factory

        Args:
            config (Dict[str, Any]): Factory configuration
        """
        self.config = config
        self.llm = None
        self._initialized = False

        # Initialize infrastructure components
        self._initialize_infrastructure()

    def _initialize_infrastructure(self) -> None:
        """Initialize shared infrastructure components"""
        try:
            # Initialize LLM
            self.llm = self._create_llm()

            # Validate configuration
            self._validate_config()

            self._initialized = True
            logger.info("AgentFactory infrastructure initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize AgentFactory: {e}")
            raise

    def _create_llm(self) -> ChatLLM:
        """
        Initialize the LLM with configuration

        Returns:
            ChatLLM: Configured LLM instance
        """
        # Get API key from environment
        api_key = os.getenv("LLM_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "LLM_API_KEY environment variable is required. "
                "Please set it in your environment or .env file."
            )

        # Create LLM with configuration
        llm_config = {
            "model": self.config.get("model_name", "default-model"),
            "temperature": self.config.get("temperature", 0.0),
            "max_tokens": self.config.get("max_tokens", 2000),
            "google_api_key": api_key,  # Keep original param name for compatibility
        }

        try:
            llm = ChatLLM(**llm_config)
            logger.info(f"LLM initialized with model: {llm_config['model']}")
            return llm

        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise ValueError(f"LLM initialization failed: {e}")

    def _validate_config(self) -> None:
        """Validate factory configuration"""
        required_keys = ["model_name", "temperature", "max_tokens"]
        missing_keys = [key for key in required_keys if key not in self.config]

        if missing_keys:
            logger.warning(f"Missing config keys (using defaults): {missing_keys}")

    def _create_memory(self, memory_type: str = "buffer") -> ConversationBufferMemory:
        """
        Create conversation memory instance

        Args:
            memory_type (str): Type of memory to create

        Returns:
            ConversationBufferMemory: Configured memory instance
        """
        if memory_type == "buffer":
            return ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                max_token_limit=self.config.get("memory_token_limit", 2000),
                human_prefix="Human",
                ai_prefix="Assistant",
            )
        else:
            raise ValueError(f"Unsupported memory type: {memory_type}")

    def create_chat_agent(self) -> "GraphChatAgent":
        """
        Create a graph-based chat agent with pre-configured infrastructure

        Returns:
            GraphChatAgent: Fully configured and initialized graph chat agent
        """
        if not self._initialized:
            raise RuntimeError("AgentFactory not initialized")

        try:
            # Create memory for this agent instance
            memory = self._create_memory("buffer")

            # Prepare agent configuration with infrastructure components
            agent_config = {
                # Infrastructure components (pre-initialized)
                "llm": self.llm,
                "memory": memory,
                # Agent-specific configuration
                "agent_type": "chat",
                "verbose": self.config.get("verbose", False),
                "max_iterations": self.config.get("max_graph_iterations", 3),
                # Graph-specific configuration
                "supervisor_confidence_threshold": self.config.get(
                    "supervisor_confidence_threshold", 0.7
                ),
                "max_rewrite_attempts": self.config.get("max_rewrite_attempts", 2),
                # Pass through other config
                **{k: v for k, v in self.config.items() if k not in ["llm", "memory"]},
            }

            # Create and initialize the agent
            chat_agent = GraphChatAgent(agent_config)
            chat_agent.initialize()  # Agent handles its own specific setup

            logger.info("GraphChatAgent created and initialized successfully")
            return chat_agent

        except Exception as e:
            logger.error(f"Failed to create GraphChatAgent: {e}")
            raise


    def get_llm_info(self) -> Dict[str, Any]:
        """Get information about the configured LLM"""
        if not self._initialized:
            return {"status": "not_initialized"}

        return {
            "status": "initialized",
            "model": self.config.get("model_name", "unknown"),
            "temperature": self.config.get("temperature", 0.0),
            "max_tokens": self.config.get("max_tokens", 2000),
        }


# Global agent management (singleton pattern for efficiency)
_agent_factory: Optional[AgentFactory] = None
_chat_agent: Optional[GraphChatAgent] = None


def initialize_factory(config: Dict[str, Any]) -> AgentFactory:
    """
    Initialize the global agent factory

    Args:
        config (Dict[str, Any]): Factory configuration

    Returns:
        AgentFactory: Initialized factory instance
    """
    global _agent_factory

    try:
        _agent_factory = AgentFactory(config)
        logger.info("Global AgentFactory initialized")
        return _agent_factory

    except Exception as e:
        logger.error(f"Failed to initialize global AgentFactory: {e}")
        raise


def get_chat_agent(config: Dict[str, Any]) -> "GraphChatAgent":
    """
    Get or create a graph-based chat agent instance

    Args:
        config (Dict[str, Any]): Agent configuration

    Returns:
        GraphChatAgent: Graph-based chat agent instance
    """
    global _agent_factory, _chat_agent

    # Initialize factory if needed
    if _agent_factory is None:
        _agent_factory = initialize_factory(config)

    # Create chat agent if needed
    if _chat_agent is None:
        _chat_agent = _agent_factory.create_chat_agent()
        logger.info("Global GraphChatAgent instance created")

    return _chat_agent




def reset_agents():
    """
    Reset all agent instances
    Useful for testing, config changes, or memory cleanup
    """
    global _agent_factory, _chat_agent

    logger.info("Resetting all global agent instances")

    # Clean up existing instances
    _agent_factory = None
    _chat_agent = None


def get_factory_status() -> Dict[str, Any]:
    """
    Get status of the global factory and agents

    Returns:
        Dict[str, Any]: Status information
    """
    global _agent_factory, _chat_agent

    return {
        "factory_initialized": _agent_factory is not None,
        "chat_agent_created": _chat_agent is not None,
        "llm_info": _agent_factory.get_llm_info() if _agent_factory else None,
    }
