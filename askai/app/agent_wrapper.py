from typing import List, Dict
from app.graph import graph
from dotenv import load_dotenv
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

class AgentWrapper:
    """
    Wrapper for the Real Estate AI Agent with LangChain conversational memory.
    Uses ChatMessageHistory for proper session management.
    """
    
    def __init__(self):
        # LangChain chat message history
        self.chat_history = ChatMessageHistory()
        self.previous_results: List[Dict[str, any]] = []  # Store last search results
    
    def chat(self, user_message: str) -> str:
        """
        Process a user message and return the agent's response.
        Uses LangChain ChatMessageHistory for conversation history.
        """
        # Get conversation history from LangChain
        messages = self.chat_history.messages
        
        # Convert LangChain messages to our format
        conversation_history = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                conversation_history.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                conversation_history.append({"role": "assistant", "content": msg.content})
        
        # Prepare initial state with conversation history and previous results
        initial_state = {
            "messages": [("user", user_message)],
            "extracted_entities": {},
            "generated_cypher": None,
            "search_results": [],
            "plan": None,
            "intent": None,
            "final_response": None,
            "conversation_history": conversation_history,
            "previous_results": self.previous_results.copy() if self.previous_results else None
        }
        
        # Run the agent and collect the final state
        final_state = None
        try:
            for event in graph.stream(initial_state):
                for key, value in event.items():
                    # Update final_state with each event
                    if final_state is None:
                        final_state = value
                    else:
                        final_state.update(value)
        except Exception as e:
            print(f"Error running agent: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"
        
        # Extract response from final_state
        if final_state and "final_response" in final_state and final_state["final_response"]:
            response = final_state["final_response"]
        else:
            response = "I apologize, but I couldn't process your request."
        
        # Store search results if any were returned
        if final_state and "search_results" in final_state and final_state["search_results"]:
            self.previous_results = final_state["search_results"]
        
        # Add messages to LangChain history
        self.chat_history.add_user_message(user_message)
        self.chat_history.add_ai_message(response)
        
        return response
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get the conversation history from LangChain."""
        messages = self.chat_history.messages
        
        history = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                history.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                history.append({"role": "assistant", "content": msg.content})
        
        return history
    
    def clear_history(self):
        """Clear the conversation history and previous results."""
        self.chat_history.clear()
        self.previous_results = []
    
    def get_memory_summary(self) -> str:
        """Get a summary of the conversation (useful for debugging)."""
        messages = self.chat_history.messages
        return f"Conversation has {len(messages)} messages"
