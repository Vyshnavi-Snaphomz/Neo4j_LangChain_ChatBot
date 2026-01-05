from app.state import AgentState
from app.llm import get_llm
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Optional

class IntentClassification(BaseModel):
    intent: str = Field(description="Intent: 'search', 'greet', 'question', 'reference', 'comparison', 'financial_analysis', or 'unknown'")

def intent_classifier(state: AgentState):
    llm = get_llm()
    last_message = state["messages"][-1][1]
    conversation_history = state.get("conversation_history", [])
    
    structured_llm = llm.with_structured_output(IntentClassification)
    
    # Build context
    context = ""
    if conversation_history and len(conversation_history) > 1:
        recent_history = conversation_history[-4:]
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_history[:-1]])
        context = f"\nRecent conversation:\n{context}\n\n"
    
    has_previous_results = state.get("previous_results") and len(state.get("previous_results", [])) > 0

    
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""Classify the user's intent into one of these categories:

- 'search': User wants to find properties (e.g., "Find homes in Dallas", "Show me 4 bed houses")
- 'greet': User is greeting or saying goodbye (e.g., "Hello", "Hi", "Thanks", "Bye")
- 'question': User is asking a general real estate question (e.g., "What is HOA?", "How does PMI work?")
- 'reference': User is referencing a specific property from previous results (e.g., "Tell me more about property 2", "Show details of the first one")
  * ONLY classify as 'reference' if there are previous results available
  * Current status: {"Previous results available" if has_previous_results else "No previous results"}
- 'comparison': User wants to compare multiple properties (e.g., "compare property 1 and 3", "compare the first two", "show comparison of #2 and #5")
  * ONLY classify as 'comparison' if there are previous results available
  * Current status: {"Previous results available" if has_previous_results else "No previous results"}
- 'financial_analysis': User wants mortgage calculations, affordability analysis, or financial comparison (e.g., "Compare buying a 950k vs 1.15M home", "Calculate monthly payment with 180k down", "Should I buy this house?", "What's my mortgage payment?", "Compare these financially")
  * Can work with or without previous results
  * Look for: down payment mentions, mortgage/payment calculations, financial comparisons, affordability questions
- 'unknown': Anything else that doesn't fit the above categories

IMPORTANT:
- If user mentions specific property numbers (#1, #2, "first one", etc.) AND previous results exist → 'reference' or 'comparison'
- If user asks about mortgage, payments, affordability, financial comparison → 'financial_analysis'
- If user asks to find/search/show properties → 'search'
- Default to 'search' for property-related queries without clear intent

Examples:
- "Find 4 bed homes in DFW" → 'search'
- "Tell me about property 2" → 'reference' (if previous results exist)
- "Compare property 1 and 3" → 'comparison' (if previous results exist)
- "Compare buying a 950k vs 1.15M home" → 'financial_analysis'
- "I have 180k down, should I buy this?" → 'financial_analysis'
- "Calculate monthly payment for 950k home" → 'financial_analysis'
- "What is PMI?" → 'question'
- "Hello" → 'greet'
"""),
        ("user", "{context}Current message: {input}")
    ])
    
    chain = prompt | structured_llm
    result = chain.invoke({"input": last_message, "context": context})
    
    return {"intent": result.intent}
