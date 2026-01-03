from app.state import AgentState
import re

def reference_handler(state: AgentState):
    """
    Handle reference queries like "show me the 4th property" or "tell me about #3".
    Returns the specific property from previous_results.
    """
    last_message = state["messages"][-1][1].lower()
    previous_results = state.get("previous_results", [])
    
    if not previous_results:
        return {
            "final_response": "I don't have any previous search results to reference. Please search for properties first."
        }
    
    # Extract number from message
    # Patterns: "4th", "#4", "property 4", "number 4", "fourth"
    number_words = {
        "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5,
        "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10
    }
    
    index = None
    
    # Try word numbers
    for word, num in number_words.items():
        if word in last_message:
            index = num - 1
            break
    
    # Try numeric patterns
    if index is None:
        patterns = [
            r'(\d+)(?:st|nd|rd|th)',  # 1st, 2nd, 3rd, 4th
            r'#(\d+)',                 # #4
            r'property\s+(\d+)',       # property 4
            r'number\s+(\d+)',         # number 4
            r'listing\s+(\d+)',        # listing 4
            r'\b(\d+)\b'               # just a number
        ]
        
        for pattern in patterns:
            match = re.search(pattern, last_message)
            if match:
                index = int(match.group(1)) - 1
                break
    
    # Validate index
    if index is None:
        return {
            "final_response": "I couldn't determine which property you're referring to. Please specify a number (e.g., 'show me the 4th property')."
        }
    
    if index < 0 or index >= len(previous_results):
        return {
            "final_response": f"I only have {len(previous_results)} properties in the previous results. Please choose a number between 1 and {len(previous_results)}."
        }
    
    # Get the property
    p = previous_results[index]
    
    # Format Rich Response
    response = f"Here are the details for property #{index + 1}:\n\n"
    
    # Price
    if p.get("price"):
        response += f"**Price:** ${p['price']:,.0f}\n"
        
    # Location
    location_parts = [p.get("streetAddress"), p.get("city"), p.get("state"), p.get("zipcode")]
    location_str = ", ".join([str(part) for part in location_parts if part])
    if location_str:
        response += f"**Address:** {location_str}\n"
        
    # Specs
    specs = []
    if p.get("beds"): specs.append(f"{int(p['beds'])} Beds")
    if p.get("baths"): specs.append(f"{p['baths']} Baths")
    if p.get("livingArea"): specs.append(f"{p['livingArea']:,.0f} sqft")
    if p.get("lotAreaValue"): specs.append(f"{p['lotAreaValue']:,.0f} sqft Lot")
    if p.get("yearBuilt"): specs.append(f"Built in {p['yearBuilt']}")
    if specs:
        response += f"**Specs:** {' | '.join(specs)}\n"
        
    # Type/Status
    if p.get("homeType"): response += f"**Type:** {p['homeType'].replace('_', ' ').title()}\n"
    
    # Description
    desc = p.get("description") or p.get("embedding_text") or "No description available."
    if len(desc) > 1500: # Allow longer description for specific lookup
        desc = desc[:1500] + "..."
    response += f"\n**Description:**\n> {desc}\n"
    
    # URL
    if p.get("url"):
        response += f"\n**Listing URL:** {p['url']}\n"
    elif p.get("hdpUrl"):
         response += f"\n**View on Zillow:** https://www.zillow.com{p['hdpUrl']}\n"

    response += "\nWould you like to know more about this property or see other listings?"
    
    return {"final_response": response}
