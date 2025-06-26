"""
Graph node implementations for the Graph Chat Agent
"""

import logging
from typing import List, Tuple
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from .models import (
    ChatState,
    SupervisorDecision,
    RewriterResponse,
)
from .tools import get_tools
from langchain_core.messages.tool import ToolMessage
import logging

logger = logging.getLogger(__name__)


class GraphNodes:
    """Collection of graph node implementations"""

    def __init__(self, llm, memory, prompts, tools):
        self.llm = llm
        self.memory = memory
        self.prompts = prompts
        self.tools = tools

    def supervisor_node(self, state: ChatState) -> ChatState:
        """Supervisor node that makes decisions about message processing"""
        try:
            # Use current message if available, otherwise original
            message_to_analyze = state.current_message or state.original_message

            # Create simple messages using the centralized method
            messages = self._create_simple_messages(
                system_prompt=self.prompts["supervisor_system"],
                user_message=message_to_analyze,
                include_history=True,
            )

            # Use structured output directly with message objects
            llm_with_structure = self.llm.with_structured_output(SupervisorDecision)
            decision = llm_with_structure.invoke(messages)

            # Update state
            state.supervisor_decision = decision
            state.current_message = message_to_analyze
            state.iteration_count += 1

            logger.info(
                f"Supervisor decision: {decision.intent}, confidence: {decision.confidence}"
            )
            return state

        except Exception as e:
            logger.error(f"Supervisor node failed: {e}")
            state.supervisor_decision = SupervisorDecision(
                intent="error",
                confidence=0.0,
                needs_rewrite=False,
                reasoning=f"Error in supervisor: {str(e)}",
            )
            return state

    def rewriter_node(self, state: ChatState) -> ChatState:
        """Rewriter node that clarifies ambiguous messages"""
        try:
            # Create additional context from supervisor
            additional_context = None
            if state.supervisor_decision and state.supervisor_decision.reasoning:
                additional_context = (
                    f"Supervisor reasoning: {state.supervisor_decision.reasoning}"
                )

            # Create simple messages using the centralized method
            messages = self._create_simple_messages(
                system_prompt=self.prompts["rewriter_system"],
                user_message=state.original_message,
                additional_context=additional_context,
                include_history=True,
            )

            # Get structured response directly with message objects
            llm_with_structure = self.llm.with_structured_output(RewriterResponse)
            rewrite = llm_with_structure.invoke(messages)

            # Update state
            state.rewriter_response = rewrite
            state.current_message = rewrite.rewritten_message

            logger.info(f"Message rewritten: {rewrite.rewritten_message}")
            return state

        except Exception as e:
            logger.error(f"Rewriter node failed: {e}")
            # Keep original message
            state.current_message = state.original_message
            return state

    def tool_selector_node(self, state: ChatState) -> ChatState:
        """Reactive tool execution node - LLM can call tools iteratively"""
        try:

            tools = get_tools()
            logger.info(f"Available tools: {[t.name for t in tools]}")

            # Create initial messages
            messages = self._create_simple_messages(
                system_prompt=self.prompts["tool_selector"],
                user_message=state.current_message,
                include_history=True,
            )

            # Bind tools to LLM
            llm_with_tools = self.llm.bind_tools(tools)

            max_iterations = 5
            iteration = 0
            tool_results = {}

            while iteration < max_iterations:
                logger.info(f"\n--- Iteration {iteration + 1} ---")

                # Invoke LLM with current conversation history
                ai_response = llm_with_tools.invoke(messages)
                logger.info(f"LLM response received")

                # If no tool calls, LLM has its final answer
                if not ai_response.tool_calls:
                    logger.info("LLM provided final answer without tool calls")
                    # Store the LLM's response in tool_results for response_generator to use
                    tool_results["llm_final_response"] = ai_response.content
                    state.tool_results = tool_results
                    return state

                # LLM made tool calls, add its request to history
                messages.append(ai_response)
                tool_names = [tc["name"] for tc in ai_response.tool_calls]
                logger.info(f"LLM wants to call: {tool_names}")

                # Execute requested tools
                for tool_call in ai_response.tool_calls:
                    tool_to_call = next(
                        (t for t in tools if t.name == tool_call["name"]), None
                    )
                    if tool_to_call:
                        try:
                            # Execute tool
                            observation = tool_to_call.invoke(tool_call["args"])
                            tool_results[tool_call["name"]] = observation

                            # Log tool call details
                            logger.info(f"Tool Call: {tool_call['name']}")
                            logger.info(f"Tool Args: {tool_call['args']}")
                            logger.info(f"Tool Output: {observation}")

                            # Add tool result to conversation history
                            messages.append(
                                ToolMessage(
                                    content=observation, tool_call_id=tool_call["id"]
                                )
                            )

                        except Exception as tool_error:
                            error_msg = f"Error executing {tool_call['name']}: {str(tool_error)}"
                            logger.error(error_msg)
                            messages.append(
                                ToolMessage(
                                    content=error_msg, tool_call_id=tool_call["id"]
                                )
                            )
                    else:
                        error_msg = f"Tool {tool_call['name']} not found"
                        logger.error(error_msg)
                        messages.append(
                            ToolMessage(content=error_msg, tool_call_id=tool_call["id"])
                        )

                iteration += 1

            # If we hit max iterations, get final response
            logger.warning(
                f"Reached max iterations ({max_iterations}), getting final response"
            )
            final_response = self.llm.invoke(
                messages
                + [
                    {
                        "role": "user",
                        "content": "Please provide your final answer based on the information gathered.",
                    }
                ]
            )
            # Store final response in tool_results for response_generator
            tool_results["llm_final_response"] = (
                final_response.content
                if hasattr(final_response, "content")
                else str(final_response)
            )
            state.tool_results = tool_results
            return state

        except Exception as e:
            logger.error(f"Tool selector failed: {e}")
            # Store error in tool_results for response_generator
            state.tool_results = {
                "error": f"I encountered an error while processing your request: {str(e)}"
            }
            return state

    def response_generator_node(self, state: ChatState) -> ChatState:
        """Generate final response based on all previous processing"""
        try:
            # Check if tool_selector already generated a final response
            if state.tool_results and "llm_final_response" in state.tool_results:
                state.final_response = state.tool_results["llm_final_response"]
                logger.info("Using final response from tool_selector reactive loop")
            elif state.tool_results and "error" in state.tool_results:
                state.final_response = state.tool_results["error"]
                logger.info("Using error response from tool_selector")
            else:
                # Use the centralized method to create response messages
                messages = self._create_response_messages(state)
                # Generate response
                response = self.llm.invoke(messages)

                if response and hasattr(response, "content"):
                    state.final_response = response.content
                    logger.info(
                        f"Response generated successfully: {len(response.content)} characters"
                    )
                else:
                    logger.warning(f"Unexpected LLM response format: {response}")
                    state.final_response = "I apologize, but I couldn't generate a proper response. Please try again."

            # Update memory
            if self.memory:
                self.memory.chat_memory.add_user_message(state.current_message)
                self.memory.chat_memory.add_ai_message(state.final_response)

            # Set metadata
            state.metadata = {
                "intent": (
                    state.supervisor_decision.intent
                    if state.supervisor_decision
                    else "unknown"
                ),
                "confidence": (
                    state.supervisor_decision.confidence
                    if state.supervisor_decision
                    else 0.0
                ),
                "tools_used": (
                    list(state.tool_results.keys()) if state.tool_results else []
                ),
                "iterations": state.iteration_count,
                "was_rewritten": state.rewriter_response is not None,
            }

            return state

        except Exception as e:
            logger.error(f"Response generator failed: {e}")
            state.final_response = "I'm sorry, I encountered an error processing your request. Please try again."
            state.metadata = {"error": str(e)}
            return state

    def supervisor_router(self, state: ChatState) -> str:
        """Simple routing based on intent"""
        decision = state.supervisor_decision

        if not decision:
            return "end"

        if decision.needs_rewrite and not state.rewriter_response:
            return "rewrite"

        # Route based on intent
        elif decision.intent == "tool_required":
            return "tools"

        else:
            return "respond"

    def _create_simple_messages(
        self,
        system_prompt: str,
        user_message: str,
        additional_context: str = None,
        include_history: bool = False,
        history_limit: int = 6,
        tool_results: dict = None,
    ) -> List:
        """Helper method to create simple message chains with optional conversation history and tool results"""
        messages = [SystemMessage(content=system_prompt)]

        # Add conversation history if requested and available
        if (
            include_history
            and self.memory
            and hasattr(self.memory, "chat_memory")
            and self.memory.chat_memory.messages
        ):
            recent_messages = self.memory.chat_memory.messages[-history_limit:]
            for msg in recent_messages:
                messages.append(msg)

        # Add tool results summary if provided
        if tool_results:
            tool_summary = self._create_tool_summary(tool_results)
            if tool_summary:
                messages.append(AIMessage(content=f"Context: {tool_summary}"))

        # Add additional context if provided
        if additional_context:
            messages.append(AIMessage(content=additional_context))

        # Add current user message
        messages.append(HumanMessage(content=user_message))

        return messages

    def _create_response_messages(self, state: ChatState) -> List:
        """Helper method to create response message chains"""
        return self._create_simple_messages(
            system_prompt=self.prompts["response_system"],
            user_message=state.original_message,
            include_history=True,
            history_limit=2,  # Keep original behavior: last 1 exchange (2 messages)
            tool_results=state.tool_results,
        )

    def _create_tool_summary(self, tool_results: dict) -> str:
        """Create a clean summary of tool results"""
        summaries = []
        for tool_name, result in tool_results.items():
            # Handle each tool type
            summaries.append(f"{tool_name}: {result}")

        return "; ".join(summaries)
