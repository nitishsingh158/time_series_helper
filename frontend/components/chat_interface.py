# Chat interface components for Streamlit
# Purpose:
# UI components for the chat
# Message routing to agents
# Displaying agent responses
# Managing conversation state

import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from agents.agent_factory import get_chat_agent


@dataclass
class AgentResponse:
    """Standardized response structure from agents"""

    text: str
    visualizations: List = None
    data: Optional[pd.DataFrame] = None
    metadata: Dict[str, Any] = None


def create_chat_interface(config: Dict[str, Any]) -> None:
    """
    Create the chat interface component using Streamlit's native chat UI
    """
    st.header("AI Time Series Assistant")

    # Initialize chat history
    initialize_chat_state()

    # Display chat messages using Streamlit's native chat interface
    display_chat_messages()

    # Handle new user input at the bottom
    handle_user_input(config)


def display_chat_messages() -> None:
    """Display all chat messages using Streamlit's native chat interface"""
    # Create a container for the chat messages with a fixed height
    chat_container = st.container()

    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                # Display the text content
                st.markdown(message["content"])

                # Display visualizations if present (only for assistant messages)
                if (
                    message["role"] == "assistant"
                    and "visualizations" in message
                    and message["visualizations"]
                ):
                    for viz in message["visualizations"]:
                        st.plotly_chart(viz, use_container_width=True)

                # Display data tables if present (only for assistant messages)
                if (
                    message["role"] == "assistant"
                    and "data" in message
                    and message["data"] is not None
                ):
                    st.dataframe(message["data"], use_container_width=True)


def initialize_chat_state() -> None:
    """Initialize conversation state if needed"""
    if "messages" not in st.session_state:
        st.session_state.messages = [create_welcome_message()]


def create_welcome_message() -> Dict[str, str]:
    """Create initial welcome message"""
    return {
        "role": "assistant",
        "content": """Hello! I'm your Time Series Analysis Assistant. 

I can help you analyze IoT data from connected assets.\n
What would you like to explore today?""",
    }


def handle_user_input(config: Dict[str, Any]) -> None:
    """Handle new user input and route to agents"""
    if prompt := st.chat_input("Ask me about machines, data, or analysis..."):
        # Add user message to history
        add_user_message(prompt)

        # Process through agents and get response
        with st.spinner("Thinking..."):
            response = route_message_to_agents(prompt, config)

        # Add agent response to history
        add_agent_response_to_history(response)

        # Refresh the page to show new messages
        st.rerun()


def add_user_message(prompt: str) -> None:
    """Add user message to conversation history"""
    st.session_state.messages.append({"role": "user", "content": prompt})


# Deprecated functions - removed as they're no longer needed with native chat interface


def route_message_to_agents(prompt: str, config: Dict[str, Any]) -> AgentResponse:
    """
    Main routing logic - sends message through agent pipeline
    """
    # Get chat agent from factory
    chat_agent = get_chat_agent(config)

    # Process message through the graph-based chat agent
    # The GraphChatAgent now handles intent parsing, routing, and response generation internally
    response = chat_agent.process_message(
        message=prompt,
    )

    return response


def validate_data_availability() -> bool:
    """Check if data is loaded and ready"""
    return (
        "data" in st.session_state
        and st.session_state.data is not None
        and isinstance(st.session_state.data, pd.DataFrame)
        and not st.session_state.data.empty
    )


def create_no_data_response() -> AgentResponse:
    """Create response when no data is available"""
    return AgentResponse(
        text="Please upload a CSV file first. I need data to analyze.",
        visualizations=[],
        metadata={"type": "no_data_error"},
    )


def add_agent_response_to_history(response: AgentResponse) -> None:
    """Add agent response to conversation history"""
    message = {"role": "assistant", "content": response.text}

    # Add visualizations and data to message if present
    if response.visualizations:
        message["visualizations"] = response.visualizations

    if response.data is not None:
        message["data"] = response.data

    st.session_state.messages.append(message)


# Helper functions for backward compatibility during transition
def show_help() -> AgentResponse:
    """Generate help response - could be moved to chat agent"""
    help_text = """
   ## Time Series Analysis Assistant Help
   [... existing help content ...]
   """
    return AgentResponse(text=help_text)


def handle_error(error: Exception) -> AgentResponse:
    """Handle errors and return user-friendly response"""
    error_message = f"I encountered an error: {str(error)}. Please try again."
    return AgentResponse(
        text=error_message, metadata={"type": "error", "error": str(error)}
    )
