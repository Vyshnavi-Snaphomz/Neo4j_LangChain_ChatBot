from app.state import AgentState
from app.llm import get_llm
from langchain_core.prompts import ChatPromptTemplate

def query_planner(state: AgentState):
    llm = get_llm()
    entities = state.get("extracted_entities", {})
    intent = state.get("intent", "")
    
    if intent != "search":
        return {"plan": "direct_response"}
    
    # Simple logic for now: if sufficient entities, structured search, else vector/hybrid?
    # Keeping it simple as per creating a 'plan' string
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Query Planner. Based on the extracted entities: {entities}, decide the best search strategy (Cypher, Vector, or Hybrid). Output a brief plan."),
        ("user", "Make a plan.")
    ])
    
    chain = prompt | llm
    result = chain.invoke({"entities": str(entities)})
    
    return {"plan": result.content}
