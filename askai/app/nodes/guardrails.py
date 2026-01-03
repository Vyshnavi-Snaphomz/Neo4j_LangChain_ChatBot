from app.state import AgentState

def policy_guardrails(state: AgentState):
    results = state.get("search_results", [])
    
    print(f"[DEBUG] Guardrails received {len(results)} results")
    
    # Check if empty
    if not results:
        return {"search_results": []}
    
    # Filter allowed fields - rich Zillow schema
    allowed_fields = {
        "zpid", "price", "state", "city", "streetAddress", "zipcode",
        "beds", "baths", "livingArea", "lotSize", "lotAreaValue",
        "yearBuilt", "homeType", "homeStatus",
        "description", "url", "hdpUrl", "score"
    }
    
    sanitized_results = []
    for res in results:
        sanitized = {k: v for k, v in res.items() if k in allowed_fields}
        sanitized_results.append(sanitized)
    
    print(f"[DEBUG] Guardrails returning {len(sanitized_results)} sanitized results")
        
    return {"search_results": sanitized_results}

