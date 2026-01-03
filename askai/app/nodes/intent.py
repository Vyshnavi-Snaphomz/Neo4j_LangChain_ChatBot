from app.state import AgentState
from app.llm import get_llm
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Optional

class IntentClassification(BaseModel):
    intent: str = Field(description="Intent: 'search', 'greet', 'question', 'reference', 'comparison', or 'unknown'")

def intent_classifier(state: AgentState):
    """
    Classify user intent to determine if they're:
    - 'search': Looking for properties
    - 'reference': Asking about previous results (e.g., "show me the 4th one")
    - 'comparison': Wants to compare properties (e.g., "compare property 1 and 3")
    - 'question': Asking a question about a property
    - 'greet': Greeting
    - 'unknown': Other
    """
    llm = get_llm()
    last_message = state["messages"][-1][1]
    conversation_history = state.get("conversation_history", [])
    previous_results = state.get("previous_results")
    
    structured_llm = llm.with_structured_output(IntentClassification)
    
    # Build context
    context = ""
    if conversation_history and len(conversation_history) > 1:
        recent_history = conversation_history[-4:]
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_history[:-1]])
        context = f"\nRecent conversation:\n{context}\n\n"
    
    has_previous_results = previous_results and len(previous_results) > 0
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""Classify the user's intent into one of these categories:

- 'search': User wants to search for properties (e.g., "houses in Texas", "properties under 500k")
- 'reference': User is referring to a specific previous result (e.g., "show me the 4th one", "tell me about property #3")
- 'comparison': User wants to compare multiple properties (e.g., "compare property 1 and 3", "compare the first two", "show comparison of #2 and #5")
  * ONLY classify as 'comparison' if there are previous results available
  * Current status: {"Previous results available" if has_previous_results else "No previous results"}
- 'question': User is asking a general question about real estate
- 'greet': User is greeting or saying hello
- 'unknown': Anything else

Examples:
- "properties in California" → search
- "show me the 4th property" → reference
- "compare property 1 and 3" → comparison
- "compare the first two" → comparison
- "what about 3 bedrooms?" → search (refining search)
- "hello" → greet"""),
        ("user", "{context}Current message: {input}")
    ])
    
    chain = prompt | structured_llm
    result = chain.invoke({"input": last_message, "context": context})
    
    return {"intent": result.intent}
