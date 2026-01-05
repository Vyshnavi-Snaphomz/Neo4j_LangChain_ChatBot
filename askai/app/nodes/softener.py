from app.state import AgentState
from app.llm import get_llm
from langchain_core.prompts import ChatPromptTemplate
from app.nodes.census_data import format_census_insights_for_response

def response_softener(state: AgentState):
    results = state.get("search_results", [])
    query = state["messages"][-1][1]
    intent = state.get("intent", "search")
    market_insights = state.get("market_insights")
    
    print(f"[DEBUG] Softener received {len(results)} results")
    print(f"[DEBUG] Intent: {intent}")

    if not results and intent == "search":
        print(f"[DEBUG] No results found, returning 'Data not available'")
        return {"final_response": "I couldn't find any properties matching your criteria in the database. Try adjusting your search parameters (price range, location, bedrooms, etc.)."}

    if not results:
        # Non-search intent with no results
        return {}

    print(f"[DEBUG] Formatting {len(results)} results for response")

    
    # Format results with rich property details
    formatted_results = []
    for i, r in enumerate(results, 1):
        property_str = f"**Property {i}:**\n"
        
        # Price
        if r.get("price"):
            property_str += f"- **Price:** ${r['price']:,.0f}\n"
        
        # Beds & Baths
        if r.get("beds"):
            property_str += f"- **Bedrooms:** {int(r['beds'])}\n"
        if r.get("baths"):
            property_str += f"- **Bathrooms:** {r['baths']}\n"
        
        # Address
        street = r.get("streetAddress")
        city = r.get("city")
        state_val = r.get("state")
        zipcode = r.get("zipcode")
        
        if street and city and state_val:
            property_str += f"- **Address:** {street}, {city}, {state_val}"
            if zipcode:
                property_str += f" {zipcode}"
            property_str += "\n"
        elif city and state_val:
            property_str += f"- **Location:** {city}, {state_val}\n"
        
        # Living Area
        if r.get("livingArea"):
            property_str += f"- **Living Area:** {r['livingArea']:,.0f} sqft\n"
        
        # Lot Size
        if r.get("lotAreaValue"):
            property_str += f"- **Lot Size:** {r['lotAreaValue']:,.0f} sqft\n"
        elif r.get("lotSize"):
            property_str += f"- **Lot Size:** {r['lotSize']}\n"
        
        # Year Built
        if r.get("yearBuilt"):
            property_str += f"- **Year Built:** {r['yearBuilt']}\n"
        
        # Home Type
        if r.get("homeType"):
            home_type = r['homeType'].replace('_', ' ').title()
            property_str += f"- **Type:** {home_type}\n"
        
        # Status
        if r.get("homeStatus"):
            status = r['homeStatus'].replace('_', ' ').title()
            property_str += f"- **Status:** {status}\n"
        
        # Description - try 'description' field first, then 'embedding_text'
        desc = r.get("description")
        if not desc:
            desc = r.get("embedding_text")
            
        if desc:
            # Clean up if it's embedding_text (often has repetitive headers)
            if not r.get("description") and "for_sale" in desc:
                 # It's likely raw embedding text, keep it as is or try to format
                 pass
                 
            if len(desc) > 800:
                desc = desc[:800] + "..."
            property_str += f"- **Description:**\n> {desc}\n"
        else:
            # Fallback for truly empty descriptions (should be rare with new filter)
            property_str += f"- **Description:** *No detailed description available.*\n"
        
        # URL
        if r.get("url"):
            property_str += f"- **Listing URL:** {r['url']}\n"
        elif r.get("hdpUrl"):
            property_str += f"- **View on Zillow:** https://www.zillow.com{r['hdpUrl']}\n"
        
        formatted_results.append(property_str)
    
    results_text = "\n\n".join(formatted_results)
    
    # Add Census market insights if available
    census_insights_text = format_census_insights_for_response(market_insights)
    
    # Use LLM to create natural response
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful real estate agent. Present the property listings in a clear, professional manner.\n\nIMPORTANT: You MUST include the full 'Description' AND the 'Listing URL' provided for each property in your response. Do not summarize or remove them."),
        ("user", "User query: {query}\n\nProperty listings:\n{results}\n\nProvide a helpful response with the property details. Make sure to include the descriptions and URLs.")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"query": query, "results": results_text})
    
    # Append Census insights to the response
    final_response = response.content
    if census_insights_text:
        final_response += census_insights_text
    
    print(f"[DEBUG] Softener generated response: '{final_response[:100]}'...")
    
    return {"final_response": final_response}
