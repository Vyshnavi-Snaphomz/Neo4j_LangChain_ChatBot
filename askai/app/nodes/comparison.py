from app.state import AgentState
from app.llm import get_llm
from langchain_core.prompts import ChatPromptTemplate
import re

def comparison_handler(state: AgentState):
    """
    Handle comparison requests like "compare property 1 and 3" or "compare the first two".
    Extracts property numbers and returns detailed comparison using full schema.
    """
    last_message = state["messages"][-1][1].lower()
    previous_results = state.get("previous_results", [])
    
    if not previous_results:
        return {
            "final_response": "I don't have any previous search results to compare. Please search for properties first."
        }
    
    # Extract numbers from message
    numbers = []
    
    # Pattern 1: "property 1 and 3", "properties 2 and 5"
    pattern1 = r'propert(?:y|ies)\s+(\d+)\s+and\s+(\d+)'
    match = re.search(pattern1, last_message)
    if match:
        numbers = [int(match.group(1)), int(match.group(2))]
    
    # Pattern 2: "first two", "first 3"
    if not numbers:
        pattern2 = r'first\s+(\w+)'
        match = re.search(pattern2, last_message)
        if match:
            num_word = match.group(1)
            num_map = {"two": 2, "three": 3, "2": 2, "3": 3, "four": 4, "4": 4, "five": 5, "5": 5}
            if num_word in num_map:
                count = num_map[num_word]
                numbers = list(range(1, min(count + 1, len(previous_results) + 1)))
    
    # Pattern 3: "#1 and #3", "1 and 3"
    if not numbers:
        pattern3 = r'#?(\d+)\s+and\s+#?(\d+)'
        match = re.search(pattern3, last_message)
        if match:
            numbers = [int(match.group(1)), int(match.group(2))]
    
    # Validate
    if not numbers or len(numbers) < 2:
        return {
            "final_response": "Please specify which properties to compare. For example:\n- 'Compare property 1 and 3'\n- 'Compare the first two properties'\n- 'Compare #2 and #5'"
        }
    
    # Check bounds
    invalid = [n for n in numbers if n < 1 or n > len(previous_results)]
    if invalid:
        return {
            "final_response": f"I only have {len(previous_results)} properties. Please choose numbers between 1 and {len(previous_results)}."
        }
    
    # Get properties (convert to 0-indexed)
    properties_to_compare = [previous_results[n-1] for n in numbers]
    
    # Build detailed comparison response
    response = f"## 🔄 Comparing {len(properties_to_compare)} Properties\n\n"
    
    # Price Analysis
    prices = [p.get('price', 0) for p in properties_to_compare if p.get('price')]
    if prices:
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)
        response += f"### 💰 Price Analysis\n"
        response += f"- **Average:** ${avg_price:,.0f}\n"
        response += f"- **Range:** ${min_price:,} - ${max_price:,}\n"
        response += f"- **Difference:** ${max_price - min_price:,}\n\n"
    
    # Detailed comparison table
    response += "### 📊 Property Comparison\n\n"
    
    for i, prop in enumerate(properties_to_compare, 1):
        response += f"**Property #{numbers[i-1]}:**\n"
        
        # Price
        if prop.get('price'):
            response += f"- **Price:** ${prop['price']:,}\n"
        
        # Beds & Baths
        if prop.get('beds'):
            response += f"- **Bedrooms:** {prop['beds']}\n"
        if prop.get('baths'):
            response += f"- **Bathrooms:** {prop['baths']}\n"
        
        # Location
        city = prop.get('city')
        state = prop.get('state')
        address = prop.get('streetAddress') or prop.get('address')
        if address and city and state:
            response += f"- **Address:** {address}, {city}, {state}\n"
        elif city and state:
            response += f"- **Location:** {city}, {state}\n"
        
        # Living Area
        if prop.get('livingArea'):
            response += f"- **Living Area:** {prop['livingArea']:,.0f} sqft\n"
        
        # Lot Size
        if prop.get('lotAreaValue'):
            lot_units = prop.get('lotAreaUnits', 'acres')
            response += f"- **Lot Size:** {prop['lotAreaValue']} {lot_units}\n"
        
        # Home Type
        if prop.get('homeType'):
            response += f"- **Type:** {prop['homeType']}\n"
        
        # Listing URL
        if prop.get('listingUrl'):
            response += f"- **Listing:** [View Property]({prop['listingUrl']})\n"
        
        response += "\n"
    
    # Add insights
    response += "### 💡 Insights\n"
    
    # Same location check
    cities = [p.get('city') for p in properties_to_compare if p.get('city')]
    if cities and len(set(cities)) == 1:
        response += f"- All properties are in **{cities[0]}**\n"
    
    # Price similarity
    if prices and len(prices) > 1:
        price_diff_pct = ((max(prices) - min(prices)) / max(prices)) * 100
        if price_diff_pct < 10:
            response += "- Properties are **similarly priced** (within 10%)\n"
        elif price_diff_pct > 50:
            response += "- Properties have **significant price differences** (>50%)\n"
    
    # Beds/baths comparison
    beds_list = [p.get('beds') for p in properties_to_compare if p.get('beds')]
    if beds_list and len(set(beds_list)) == 1:
        response += f"- All properties have **{beds_list[0]} bedrooms**\n"
    
    return {"final_response": response}
