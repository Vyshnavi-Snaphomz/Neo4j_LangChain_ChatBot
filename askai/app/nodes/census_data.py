"""
Census Data Enrichment Node

Enriches property search results with US Census Bureau market data:
- SOMA (Survey of Market Absorption) - Absorption rates for multifamily units
- RHFS (Rental Housing Finance Survey) - Rental property financial characteristics
"""

from app.state import AgentState
from app.census_client import census_client
from typing import Dict, Optional

def census_data_enrichment(state: AgentState) -> Dict:
    """
    Enrich property search results with Census Bureau market data
    
    Args:
        state: Current agent state with search results and extracted entities
        
    Returns:
        Dict with market_insights added to state (and search_results passed through)
    """
    search_results = state.get("search_results", [])
    extracted_entities = state.get("extracted_entities", {})
    
    # Always pass through search results
    result = {"search_results": search_results}
    
    # Only try to enrich if we have search results
    if not search_results:
        return result
    
    # Extract location from search criteria
    state_code = extracted_entities.get("state")
    city = extracted_entities.get("city")
    cities = extracted_entities.get("cities")
    
    # Use first city from cities list if available
    if cities and len(cities) > 0:
        city = cities[0]
    
    # Fetch Census data if we have a state
    if state_code:
        print(f"[DEBUG] Fetching Census data for {city}, {state_code}" if city else f"[DEBUG] Fetching Census data for {state_code}")
        
        try:
            # Get comprehensive market insights
            insights = census_client.get_market_insights(state_code, city)
            
            if insights and insights.get("has_data"):
                print(f"[DEBUG] Census data retrieved successfully")
                result["market_insights"] = insights
            else:
                print(f"[DEBUG] No Census data available for this location")
        except Exception as e:
            print(f"[DEBUG] Error fetching Census data: {e}")
    
    return result



def format_census_insights_for_response(market_insights: Optional[Dict]) -> str:
    """
    Format Census market insights for inclusion in final response
    
    Args:
        market_insights: Market insights dict from census_data_enrichment
        
    Returns:
        Formatted markdown string to append to response
    """
    if not market_insights or not market_insights.get("has_data"):
        return ""
    
    return census_client.format_market_insights(market_insights)
