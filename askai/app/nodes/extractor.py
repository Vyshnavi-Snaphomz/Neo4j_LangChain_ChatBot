from app.state import AgentState
from app.llm import get_llm
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Optional, List
from app.abbreviations import (
    normalize_metro_area,
    normalize_real_estate_terms,
    normalize_poi_category,
    extract_distance_preference
)

class SearchEntities(BaseModel):
    city: Optional[str] = Field(None, description="City name")
    cities: Optional[List[str]] = Field(None, description="List of cities for metro area searches")
    state: Optional[str] = Field(None, description="State abbreviation or full name")
    min_price: Optional[float] = Field(None, description="Minimum budget/price")
    max_price: Optional[float] = Field(None, description="Maximum budget/price")
    beds: Optional[int] = Field(None, description="Minimum number of bedrooms")
    baths: Optional[float] = Field(None, description="Minimum number of bathrooms")
    min_lot_size: Optional[float] = Field(None, description="Minimum lot size in acres/sqft")
    keywords: Optional[List[str]] = Field(None, description="Descriptive keywords like aesthetic, countryside, modern, luxury, etc.")
    poi_type: Optional[str] = Field(None, description="Point of interest type (schools, parks, shopping, etc.)")
    max_distance: Optional[float] = Field(None, description="Maximum distance to POI in miles")

def entity_extractor(state: AgentState):
    llm = get_llm()
    last_message = state["messages"][-1][1]
    conversation_history = state.get("conversation_history", [])
    
    # Pre-process user input with abbreviations module
    normalized_message = normalize_real_estate_terms(last_message)
    
    # Check for metro area abbreviations
    metro_cities = normalize_metro_area(last_message)
    
    # Check for POI proximity requirements
    poi_category = normalize_poi_category(last_message)
    distance_pref = None
    if poi_category:
        distance_pref = extract_distance_preference(last_message)
    
    structured_llm = llm.with_structured_output(SearchEntities)
    
    # Build context from conversation history
    context = ""
    if conversation_history and len(conversation_history) > 1:
        # Get last few messages for context
        recent_history = conversation_history[-6:]  # Last 3 exchanges
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_history[:-1]])
        context = f"\nConversation history:\n{context}\n\n"
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Extract real estate search criteria from the user message.

IMPORTANT: For state field, always use the FULL state name, not abbreviations.
- If user says "CA" or "ca" or "cali", extract state as "California"
- If user says "TX" or "tx", extract state as "Texas"
- If user says "NY" or "ny", extract state as "New York"
- If user says "NV" or "nv", extract state as "Nevada"
- If user says "FL" or "fl", extract state as "Florida"
- If user types "i ca" (typo for "in ca"), extract state as "California"
- If user types "i the" (typo/filler), IGNORE it.
- If user mentions "San Francisco" or "San Fransisco", extract city as "San Francisco" and state as "California".
- If user mentions "Los Vegas" (typo), extract city as "Las Vegas" and state as "Nevada".

HANDLING BROAD LOCATIONS:
- If user says "USA" or "US" or "America", IGNORE it for the 'state' field. Do NOT extract "USA" as a state.
- If no specific state is mentioned, leave state as None.

PRICE MAPPING (Crucial):
- "luxury", "upscale", "premium" -> Set min_price to 1,000,000 (do NOT set max_price)
- "cheap", "affordable", "budget" -> Set max_price to 400,000
- "expensive" -> Set min_price to 800,000

KEYWORDS: Extract descriptive terms that describe the property style or features:
- "aesthetic", "beautiful", "modern", "contemporary"
- "countryside", "rural", "urban", "suburban", "hill top", "hilltop"
- "waterfront", "mountain", "view"
- Any other descriptive adjectives (EXCLUDING price terms like luxury/cheap)

POI PROXIMITY: Extract if user mentions proximity to points of interest:
- "near schools", "close to parks", "near shopping" -> Extract poi_type
- "within X miles", "walking distance" -> Extract max_distance

Extract all relevant search criteria including city, state, price, beds, baths, lot size, keywords, and POI proximity."""),
        ("user", "{context}Current query: {input}")
    ])
    
    chain = prompt | structured_llm
    entities = chain.invoke({"input": normalized_message, "context": context})
    
    # Post-processing for price mapping if LLM misses it
    extracted = entities.dict(exclude_none=True)
    keywords = extracted.get("keywords", [])
    
    # Move price keywords to explicit price filters if not already set
    if "luxury" in keywords or "premium" in keywords:
        if "min_price" not in extracted:
            extracted["min_price"] = 1000000
        keywords = [k for k in keywords if k not in ["luxury", "premium"]]
        
    if "cheap" in keywords or "affordable" in keywords:
        if "max_price" not in extracted:
            extracted["max_price"] = 400000
        keywords = [k for k in keywords if k not in ["cheap", "affordable"]]
        
    extracted["keywords"] = keywords
    
    # Override with metro area cities if detected
    if metro_cities:
        extracted["cities"] = metro_cities
        print(f"[DEBUG] Detected metro area with cities: {metro_cities}")
    
    # Add POI proximity if detected
    if poi_category:
        extracted["poi_type"] = poi_category
        extracted["max_distance"] = distance_pref
        print(f"[DEBUG] Detected POI proximity: {poi_category} within {distance_pref} miles")
    
    return {"extracted_entities": extracted}

