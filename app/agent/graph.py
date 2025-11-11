"""
LangGraph-based agentic framework for persona switching and state management.
"""
import os
from typing import TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from app.repositories.thread_repository import ThreadRepository
from app.utils.persona_manager import PersonaManager
from app.core.config import settings
from app.core.exceptions import LLMError, ConfigurationError
from app.core.logging_config import logger


class AgentState(TypedDict):
    """State for the LangGraph agent."""
    messages: Annotated[list[BaseMessage], add_messages]
    user_id: str
    thread_name: str
    thread_id: int
    persona_prompt: str


class PersonaSwitchingAgent:
    """Agent that manages persona switching and conversation threads."""
    
    def __init__(self, repository: ThreadRepository, model_name: str = None):
        self.repository = repository
        self.persona_manager = PersonaManager()
        
        # Initialize LLM
        api_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ConfigurationError(
                "OPENAI_API_KEY not found. Please set it in environment variables or .env file"
            )
        
        self.llm = ChatOpenAI(
            model=model_name or settings.model_name,
            temperature=settings.temperature,
            api_key=api_key
        )
        
        # Build the graph
        self.graph = self._build_graph()
        logger.info(f"Initialized PersonaSwitchingAgent with model: {model_name or settings.model_name}")
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("route", self._route_message)
        workflow.add_node("process_message", self._process_message)
        workflow.add_node("save_message", self._save_message)
        
        # Set entry point
        workflow.set_entry_point("route")
        
        # Add edges
        workflow.add_edge("route", "process_message")
        workflow.add_edge("process_message", "save_message")
        workflow.add_edge("save_message", END)
        
        return workflow.compile()
    
    def _route_message(self, state: AgentState) -> AgentState:
        """Route message to determine if we need to switch threads or create new ones."""
        messages = state["messages"]
        user_id = state["user_id"]
        last_message = messages[-1]
        
        if isinstance(last_message, HumanMessage):
            user_text = last_message.content
            
            # If thread_name is explicitly provided in state, use it
            if state.get("thread_name") and state["thread_name"] != "":
                thread_name = state["thread_name"]
                existing_thread = self.repository.get_thread(user_id, thread_name)
                if existing_thread:
                    state["thread_id"] = existing_thread.id
                    state["persona_prompt"] = existing_thread.persona_prompt
                else:
                    # Create thread with base persona if it doesn't exist
                    persona_prompt = self.persona_manager.BASE_META_PROMPT
                    new_thread = self.repository.create_thread(user_id, thread_name, persona_prompt)
                    state["thread_id"] = new_thread.id
                    state["persona_prompt"] = persona_prompt
                return state
            
            # Check if this is a persona switch request
            persona_name = self.persona_manager.extract_persona_request(user_text)
            
            if persona_name:
                # Normalize thread name
                thread_name = self.persona_manager.normalize_thread_name(persona_name)
                
                # Check if thread exists
                existing_thread = self.repository.get_thread(user_id, thread_name)
                
                if existing_thread:
                    # Switch to existing thread
                    state["thread_id"] = existing_thread.id
                    state["thread_name"] = thread_name
                    state["persona_prompt"] = existing_thread.persona_prompt
                else:
                    # Create new thread
                    persona_prompt = self.persona_manager.get_persona_prompt(persona_name)
                    new_thread = self.repository.create_thread(user_id, thread_name, persona_prompt)
                    state["thread_id"] = new_thread.id
                    state["thread_name"] = thread_name
                    state["persona_prompt"] = persona_prompt
            else:
                # Use existing thread or create default
                if "thread_id" not in state or state["thread_id"] == 0:
                    # Try to get the most recently used thread
                    recent_thread = self.repository.get_most_recent_thread(user_id)
                    
                    if recent_thread:
                        # Use the most recent thread
                        state["thread_id"] = recent_thread.id
                        state["thread_name"] = recent_thread.thread_name
                        state["persona_prompt"] = recent_thread.persona_prompt
                    else:
                        # Create a default thread if none exists
                        thread_name = "default"
                        persona_prompt = self.persona_manager.BASE_META_PROMPT
                        new_thread = self.repository.create_thread(user_id, thread_name, persona_prompt)
                        state["thread_id"] = new_thread.id
                        state["thread_name"] = thread_name
                        state["persona_prompt"] = persona_prompt
        
        return state
    
    def _process_message(self, state: AgentState) -> AgentState:
        """Process the message with the LLM using the appropriate persona context."""
        messages = state["messages"]
        thread_id = state["thread_id"]
        persona_prompt = state["persona_prompt"]
        
        try:
            # Load conversation history for this thread
            history_messages = self.repository.get_thread_messages(thread_id)
            
            # Build message list with system prompt and history
            conversation_messages = [SystemMessage(content=persona_prompt)]
            
            # Add historical messages (excluding the current one)
            for msg in history_messages:
                if msg.role == "user":
                    conversation_messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    conversation_messages.append(AIMessage(content=msg.content))
            
            # Add the current user message
            conversation_messages.extend(messages)
            
            # Get response from LLM
            logger.debug(f"Invoking LLM for thread {thread_id}")
            response = self.llm.invoke(conversation_messages)
            
            # Add assistant response to state
            state["messages"].append(response)
            
            return state
        except Exception as e:
            logger.error(f"Error processing message with LLM: {e}")
            raise LLMError(f"Failed to process message: {str(e)}")
    
    def _save_message(self, state: AgentState) -> AgentState:
        """Save user and assistant messages to the database."""
        messages = state["messages"]
        thread_id = state["thread_id"]
        
        try:
            # Get the last user and assistant messages
            user_message = None
            assistant_message = None
            
            for msg in reversed(messages):
                if isinstance(msg, HumanMessage) and user_message is None:
                    user_message = msg
                elif isinstance(msg, AIMessage) and assistant_message is None:
                    assistant_message = msg
                if user_message and assistant_message:
                    break
            
            # Save messages
            if user_message:
                self.repository.add_message(thread_id, "user", user_message.content)
            
            if assistant_message:
                self.repository.add_message(thread_id, "assistant", assistant_message.content)
            
            return state
        except Exception as e:
            logger.error(f"Error saving messages: {e}")
            raise
    
    def chat(self, user_id: str, message: str, thread_name: str = None) -> dict:
        """
        Main chat interface.
        
        Args:
            user_id: User identifier
            message: User's message
            thread_name: Optional thread name to use (if None, will be determined from message)
        
        Returns:
            Dictionary with response and thread information
        """
        # Initialize state
        initial_state: AgentState = {
            "messages": [HumanMessage(content=message)],
            "user_id": user_id,
            "thread_name": thread_name or "",
            "thread_id": 0,
            "persona_prompt": ""
        }
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        # Extract response
        assistant_messages = [msg for msg in final_state["messages"] if isinstance(msg, AIMessage)]
        response_text = assistant_messages[-1].content if assistant_messages else ""
        
        return {
            "response": response_text,
            "thread_name": final_state["thread_name"],
            "thread_id": final_state["thread_id"],
            "persona_prompt": final_state["persona_prompt"]
        }

