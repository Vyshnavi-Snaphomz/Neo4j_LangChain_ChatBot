from app.state import AgentState
from langchain_core.messages import AIMessage

def final_response(state: AgentState):
    response_text = state.get("final_response", "")
    
    print(f"[DEBUG] Final_response received: '{response_text[:100] if response_text else 'EMPTY'}'...")
    
    if not response_text:
         # Fallback if softener didn't produce anything (e.g. non-search intent meant to be handled)
         # If intent was 'greet', we should have handled it. 
         # Let's simple check:
         intent = state.get("intent")
         if intent == "greet":
             response_text = "Hello! I am your Real Estate AI Advisor. How can I help you regarding properties today?"
         elif intent == "unknown":
             response_text = "I'm sorry, I strictly answer real estate questions based on my database. Could you clarify?"
         else:
             response_text = "Data not available in database."
             
    print(f"Agent: {response_text}")
    return {"messages": [AIMessage(content=response_text)]}

