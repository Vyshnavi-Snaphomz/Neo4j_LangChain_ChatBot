from typing import List, Dict, Optional
from app.graph import graph
from dotenv import load_dotenv
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from app.history import SessionManager
from app.smart_router import SmartRouter
from app.cost_tracker import CostTracker, InsightsEngine

load_dotenv()

class AgentWrapper:
    """
    Wrapper for the Real Estate AI Agent with Persistent Neo4j Memory.
    """
    
    def __init__(self, session_id: Optional[str] = None, user_id: Optional[str] = None):
        self.session_manager = SessionManager(user_id=user_id)
        self.user_id = user_id or "default"
        
        # Initialize smart routing and cost tracking
        self.router = SmartRouter()
        self.cost_tracker = CostTracker()
        self.insights = InsightsEngine()
        
        # If no session ID provided, create one
        if not session_id:
            self.session_id = self.session_manager.create_session()
        else:
            self.session_id = session_id
            
        # Initialize LangChain history
        self.chat_history = ChatMessageHistory()
        self.previous_results: List[Dict[str, any]] = []
        
        # Load existing history from DB
        self._load_history_from_db()
        self._load_context_from_db()
        
    def _load_history_from_db(self):
        """Populate in-memory history from Neo4j."""
        messages = self.session_manager.get_messages(self.session_id)
        for msg in messages:
            if msg["role"] == "user":
                self.chat_history.add_user_message(msg["content"])
            elif msg["role"] == "assistant":
                self.chat_history.add_ai_message(msg["content"])

    def _load_context_from_db(self):
        """Restore previous search results from Neo4j context."""
        context = self.session_manager.get_context(self.session_id, "last_results")
        if context:
            self.previous_results = context
    
    def chat(self, user_message: str) -> str:
        """
        Process a user message and return the agent's response.
        Uses smart routing for cost optimization and LangChain ChatMessageHistory for conversation history.
        """
        # Extract user insights for personalization
        self.insights.extract_signals(self.user_id, user_message)
        
        # Smart routing decision
        routing_decision = self.router.route_query(user_message)
        
        # If template route, return immediately (FREE)
        if routing_decision["route"] == "template":
            response = routing_decision["response"]
            
            # Log interaction
            self.cost_tracker.log_interaction(
                user_id=self.user_id,
                query=user_message,
                route="template",
                response_type="template",
                tokens_used={"input": 0, "output": 0, "total": 0},
                cost=0.0,
                metadata={"template_id": routing_decision.get("template_id")}
            )
            
            # Add to chat history
            self.chat_history.add_user_message(user_message)
            self.chat_history.add_ai_message(response)
            
            # Save to DB
            self.session_manager.save_message(self.session_id, "user", user_message)
            self.session_manager.save_message(self.session_id, "assistant", response)
            
            return response
        
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
        if final_state and "search_results" in final_state:
            if final_state["search_results"]:
                self.previous_results = final_state["search_results"]
                # PERSIST: Save context
                self.session_manager.save_context(self.session_id, "last_results", self.previous_results)
            else:
                # Clear previous_results if search returned empty
                self.previous_results = []
                self.session_manager.save_context(self.session_id, "last_results", [])
        # Also check if previous_results was directly updated (e.g., from financial_analysis)
        elif final_state and "previous_results" in final_state and final_state["previous_results"]:
            self.previous_results = final_state["previous_results"]
            # PERSIST: Save context
            self.session_manager.save_context(self.session_id, "last_results", self.previous_results)
        
        # Log interaction with cost tracking
        intent = final_state.get("intent", "unknown") if final_state else "unknown"
        self.cost_tracker.log_interaction(
            user_id=self.user_id,
            query=user_message,
            route=routing_decision["route"],
            response_type=intent,
            tokens_used={"input": len(user_message.split()), "output": len(response.split()), "total": len(user_message.split()) + len(response.split())},
            cost=routing_decision.get("estimated_cost", 0.02),
            metadata={"intent": intent, "has_results": len(self.previous_results) > 0}
        )
        
        # Add messages to LangChain history
        self.chat_history.add_user_message(user_message)
        self.chat_history.add_ai_message(response)
        
        # PERSIST: Save to Neo4j
        self.session_manager.save_message(self.session_id, "user", user_message)
        self.session_manager.save_message(self.session_id, "assistant", response)
        
        # Update session title if it's the first message
        if len(self.chat_history.messages) <= 2:
            self.session_manager.update_session_title(self.session_id, user_message[:50])
            
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
