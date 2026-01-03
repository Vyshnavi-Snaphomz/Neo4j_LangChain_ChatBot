"""
Utility functions for property operations:
- Comparison
- Similar property search
- Filtering and sorting
"""
from typing import List, Dict, Any

def filter_properties(
    properties: List[Dict[str, Any]],
    price_min: float = None,
    price_max: float = None,
    beds: int = None,
    baths: float = None
) -> List[Dict[str, Any]]:
    """Filter properties based on criteria."""
    filtered = properties
    
    if price_min is not None:
        filtered = [p for p in filtered if p.get('price') and p['price'] >= price_min]
    
    if price_max is not None:
        filtered = [p for p in filtered if p.get('price') and p['price'] <= price_max]
    
    if beds is not None:
        filtered = [p for p in filtered if p.get('beds') and p['beds'] >= beds]
    
    if baths is not None:
        filtered = [p for p in filtered if p.get('baths') and p['baths'] >= baths]
    
    return filtered

def sort_properties(
    properties: List[Dict[str, Any]],
    sort_by: str = "price_asc"
) -> List[Dict[str, Any]]:
    """Sort properties by specified criteria."""
    if sort_by == "price_asc":
        return sorted(properties, key=lambda x: x.get('price', float('inf')))
    elif sort_by == "price_desc":
        return sorted(properties, key=lambda x: x.get('price', 0), reverse=True)
    elif sort_by == "beds":
        return sorted(properties, key=lambda x: x.get('beds', 0), reverse=True)
    elif sort_by == "baths":
        return sorted(properties, key=lambda x: x.get('baths', 0), reverse=True)
    else:
        return properties

def compare_properties(properties: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compare multiple properties and highlight differences.
    Returns comparison data structure.
    """
    if not properties:
        return {}
    
    comparison = {
        "properties": properties,
        "price_range": {
            "min": min(p.get('price', 0) for p in properties if p.get('price')),
            "max": max(p.get('price', 0) for p in properties if p.get('price')),
        },
        "avg_price": sum(p.get('price', 0) for p in properties if p.get('price')) / len(properties),
    }
    
    return comparison

def find_similar_properties(
    target_property: Dict[str, Any],
    all_properties: List[Dict[str, Any]],
    price_tolerance: float = 0.2
) -> List[Dict[str, Any]]:
    """
    Find properties similar to the target property.
    Similar = same state, similar price (±20%)
    """
    if not target_property or not all_properties:
        return []
    
    target_price = target_property.get('price', 0)
    target_state = target_property.get('state')
    
    if not target_price or not target_state:
        return []
    
    min_price = target_price * (1 - price_tolerance)
    max_price = target_price * (1 + price_tolerance)
    
    similar = []
    for prop in all_properties:
        # Skip the target property itself
        if prop == target_property:
            continue
        
        # Check if in same state and similar price
        if (prop.get('state') == target_state and
            prop.get('price') and
            min_price <= prop['price'] <= max_price):
            similar.append(prop)
    
    # Return top 5
    return similar[:5]
