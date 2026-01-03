from app.state import AgentState
from app.llm import get_llm
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any

def cypher_generator(state: AgentState):
    llm = get_llm()
    entities = state.get("extracted_entities", {})
    intent = state.get("intent", "")

    if intent != "search" or not entities:
        return {"generated_cypher": None}

    # Construct WHERE clause dynamically based on entities
    # Note: We should use parameters, but for generation we construct the query text with placeholders
    # or simple string interpolation if using parameters separately.
    # The prompt requested "Always parameterize queries".
    
    # We will generate the Cypher string and also return the params to be used.
    # However, standard llm generation might be hard to get exact parameter names matching dict.
    # I'll implement a deterministic builder for the "Structured Search" as per prompt guidance.
    # "Cypher Template – Structured Search"
    
    # Actually, the prompt gives a template.
    # "Generate Cypher only from provided schema"
    
    candidates = []
    if "state" in entities:
        candidates.append("p.state = $state")
    if "city" in entities:
        candidates.append("p.city = $city")
    if "max_price" in entities:
        candidates.append("p.price <= $max_price")
    if "beds" in entities:
        candidates.append("p.beds >= $beds")
    if "baths" in entities:
        candidates.append("p.baths >= $baths")
    if "min_lot_size" in entities: # mapping from entity to schema? Schema has lotAreaValue/Units
        # Simple assumption: lotAreaValue. 
        # But for now let's stick to what's in the example template: beds, baths, price, city.
        pass

    where_clause = " AND ".join(candidates) if candidates else "1=1"
    
    cypher = f"""
    MATCH (p:Property)
    WHERE {where_clause}
    RETURN
      p.beds AS beds,
      p.baths AS baths,
      p.price AS price,
      p.streetAddress AS address,
      p.listingUrl AS listingUrl,
      p.lotAreaUnits AS lotAreaUnits
    LIMIT 5
    """
    
    return {"generated_cypher": cypher}
