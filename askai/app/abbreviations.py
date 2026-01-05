"""
Snaphomz Abbreviation Normalization System

This module provides comprehensive normalization for:
1. Metro area abbreviations (DFW, Bay Area, DMV, etc.)
2. Real estate terminology (HOA, sqft, bd/ba, etc.)
3. POI (Point of Interest) categories (schools, parks, malls, etc.)
"""

from typing import Optional, List, Dict
import re

# ============================================================================
# METRO AREA MAPPINGS
# ============================================================================

METRO_AREAS: Dict[str, List[str]] = {
    # Texas Metro Areas
    "dfw": ["Dallas", "Fort Worth", "Arlington", "Plano", "Irving", "Frisco", "McKinney", "Carrollton", "Richardson", "Denton", "Allen", "Lewisville", "Flower Mound", "Grapevine", "Grand Prairie"],
    "dallas fort worth": ["Dallas", "Fort Worth", "Arlington", "Plano", "Irving", "Frisco", "McKinney", "Carrollton", "Richardson", "Denton"],
    "greater houston": ["Houston", "Sugar Land", "The Woodlands", "Pearland", "League City", "Pasadena", "Baytown", "Missouri City", "Katy"],
    "houston metro": ["Houston", "Sugar Land", "The Woodlands", "Pearland", "League City", "Pasadena", "Baytown"],
    "austin metro": ["Austin", "Round Rock", "Cedar Park", "Georgetown", "Pflugerville", "Leander", "San Marcos"],
    "san antonio metro": ["San Antonio", "New Braunfels", "Schertz", "Seguin", "Universal City"],
    
    # California Metro Areas
    "bay area": ["San Francisco", "Oakland", "San Jose", "Berkeley", "Fremont", "Hayward", "Sunnyvale", "Santa Clara", "Mountain View", "Palo Alto", "Redwood City", "San Mateo", "Daly City"],
    "sf bay area": ["San Francisco", "Oakland", "San Jose", "Berkeley", "Fremont", "Hayward", "Sunnyvale", "Santa Clara"],
    "silicon valley": ["San Jose", "Sunnyvale", "Santa Clara", "Mountain View", "Palo Alto", "Cupertino", "Milpitas"],
    "greater la": ["Los Angeles", "Long Beach", "Anaheim", "Santa Ana", "Irvine", "Glendale", "Pasadena", "Torrance", "Orange", "Fullerton"],
    "socal": ["Los Angeles", "Long Beach", "Anaheim", "Santa Ana", "Irvine", "San Diego", "Riverside", "San Bernardino"],
    "los angeles metro": ["Los Angeles", "Long Beach", "Anaheim", "Santa Ana", "Irvine", "Glendale", "Pasadena"],
    "san diego metro": ["San Diego", "Chula Vista", "Oceanside", "Carlsbad", "El Cajon", "Vista", "Escondido"],
    "inland empire": ["Riverside", "San Bernardino", "Ontario", "Corona", "Moreno Valley", "Fontana", "Rancho Cucamonga"],
    
    # East Coast Metro Areas
    "dmv": ["Washington", "Arlington", "Alexandria", "Silver Spring", "Bethesda", "Rockville", "Frederick", "Gaithersburg"],
    "dc metro": ["Washington", "Arlington", "Alexandria", "Silver Spring", "Bethesda", "Rockville"],
    "tri-state": ["New York", "Newark", "Jersey City", "Yonkers", "Paterson", "Elizabeth", "Stamford", "Bridgeport"],
    "nyc metro": ["New York", "Newark", "Jersey City", "Yonkers", "Paterson", "Elizabeth", "White Plains"],
    "greater boston": ["Boston", "Cambridge", "Quincy", "Newton", "Somerville", "Brookline", "Waltham", "Medford", "Malden"],
    "south florida": ["Miami", "Fort Lauderdale", "West Palm Beach", "Boca Raton", "Coral Springs", "Pompano Beach", "Delray Beach"],
    "miami metro": ["Miami", "Fort Lauderdale", "Hialeah", "Pembroke Pines", "Hollywood", "Coral Springs"],
    
    # Pacific Northwest
    "greater seattle": ["Seattle", "Tacoma", "Bellevue", "Everett", "Kent", "Renton", "Spokane", "Bellingham"],
    "seattle metro": ["Seattle", "Tacoma", "Bellevue", "Everett", "Kent", "Renton", "Federal Way"],
    "portland metro": ["Portland", "Gresham", "Hillsboro", "Beaverton", "Tigard", "Lake Oswego"],
    
    # Southwest
    "greater phoenix": ["Phoenix", "Mesa", "Scottsdale", "Chandler", "Glendale", "Tempe", "Peoria", "Gilbert", "Surprise"],
    "phoenix metro": ["Phoenix", "Mesa", "Scottsdale", "Chandler", "Glendale", "Tempe"],
    "las vegas metro": ["Las Vegas", "Henderson", "North Las Vegas", "Paradise", "Spring Valley"],
    
    # Midwest
    "chicagoland": ["Chicago", "Aurora", "Naperville", "Joliet", "Rockford", "Elgin", "Waukegan", "Cicero"],
    "chicago metro": ["Chicago", "Aurora", "Naperville", "Joliet", "Rockford", "Elgin"],
    "twin cities": ["Minneapolis", "Saint Paul", "Rochester", "Bloomington", "Duluth", "Brooklyn Park"],
    "detroit metro": ["Detroit", "Grand Rapids", "Warren", "Sterling Heights", "Ann Arbor", "Lansing"],
    
    # South
    "atlanta metro": ["Atlanta", "Augusta", "Columbus", "Macon", "Savannah", "Athens", "Sandy Springs"],
    "charlotte metro": ["Charlotte", "Raleigh", "Greensboro", "Durham", "Winston-Salem", "Fayetteville"],
    "nashville metro": ["Nashville", "Memphis", "Knoxville", "Chattanooga", "Clarksville", "Murfreesboro"],
    "tampa bay": ["Tampa", "St. Petersburg", "Clearwater", "Lakeland", "Brandon", "Largo"],
    
    # Mountain West
    "denver metro": ["Denver", "Colorado Springs", "Aurora", "Fort Collins", "Lakewood", "Thornton"],
    "salt lake metro": ["Salt Lake City", "West Valley City", "Provo", "West Jordan", "Orem", "Sandy"],
}

# ============================================================================
# REAL ESTATE ABBREVIATIONS
# ============================================================================

REAL_ESTATE_TERMS: Dict[str, str] = {
    # Property Features
    "hoa": "homeowners association",
    "h.o.a": "homeowners association",
    "h.o.a.": "homeowners association",
    "condo": "condominium",
    "sfh": "single family home",
    "sfr": "single family residence",
    "mfh": "multi family home",
    "pud": "planned unit development",
    
    # Measurements
    "sqft": "square feet",
    "sq ft": "square feet",
    "sf": "square feet",
    "sq. ft.": "square feet",
    "sq.ft.": "square feet",
    "ac": "acres",
    
    # Rooms
    "bd": "bedrooms",
    "br": "bedrooms",
    "beds": "bedrooms",
    "bdrm": "bedrooms",
    "ba": "bathrooms",
    "baths": "bathrooms",
    "bthrm": "bathrooms",
    
    # Listing Terms
    "mls": "multiple listing service",
    "fsbo": "for sale by owner",
    "dom": "days on market",
    "adom": "average days on market",
    "cdom": "cumulative days on market",
    "ppsf": "price per square foot",
    "arv": "after repair value",
    "roi": "return on investment",
    "cap rate": "capitalization rate",
    
    # Property Types
    "apt": "apartment",
    "twnhse": "townhouse",
    "th": "townhouse",
    
    # Amenities
    "a/c": "air conditioning",
    "ac": "air conditioning",
    "w/d": "washer dryer",
    "wd": "washer dryer",
    "fp": "fireplace",
    "gar": "garage",
    
    # Financial
    "apr": "annual percentage rate",
    "ltv": "loan to value",
    "dti": "debt to income",
    "piti": "principal interest taxes insurance",
    "pmi": "private mortgage insurance",
    
    # Status
    "uc": "under contract",
    "pend": "pending",
    "cont": "contingent",
    "actv": "active",
}

# ============================================================================
# POI (POINT OF INTEREST) CATEGORIES
# ============================================================================

POI_CATEGORIES: Dict[str, List[str]] = {
    "schools": [
        "school", "elementary school", "middle school", "high school", 
        "university", "college", "academy", "institute", "education",
        "preschool", "kindergarten", "primary school", "secondary school"
    ],
    "parks": [
        "park", "recreation area", "playground", "green space", 
        "nature reserve", "botanical garden", "public garden", "trail",
        "recreation center", "sports complex", "athletic field"
    ],
    "shopping": [
        "mall", "shopping center", "retail", "grocery store", "supermarket",
        "shopping plaza", "outlet", "marketplace", "store", "shop",
        "convenience store", "department store"
    ],
    "finance": [
        "bank", "financial district", "credit union", "atm",
        "financial center", "investment firm", "financial services"
    ],
    "tech": [
        "it company", "tech hub", "software company", "data center",
        "technology park", "innovation center", "tech campus",
        "startup hub", "coworking space"
    ],
    "government": [
        "city hall", "courthouse", "government building", "post office",
        "municipal building", "federal building", "dmv", "police station",
        "fire station", "public office"
    ],
    "culture": [
        "museum", "art gallery", "theater", "cultural center",
        "performing arts center", "concert hall", "opera house",
        "cinema", "movie theater", "exhibition center"
    ],
    "worship": [
        "church", "temple", "mosque", "synagogue", "place of worship",
        "cathedral", "chapel", "religious center", "prayer hall"
    ],
    "healthcare": [
        "hospital", "clinic", "medical center", "urgent care",
        "doctor office", "health center", "emergency room"
    ],
    "other": [
        "cemetery", "library", "community center", "senior center",
        "ymca", "recreation facility", "public facility"
    ],
}

# ============================================================================
# DISTANCE KEYWORDS
# ============================================================================

DISTANCE_KEYWORDS: Dict[str, float] = {
    # Explicit distances (in miles)
    "walking distance": 0.5,
    "short walk": 0.3,
    "close": 1.0,
    "nearby": 2.0,
    "near": 2.0,
    "within walking distance": 0.5,
    "short drive": 5.0,
    "easy commute": 10.0,
    
    # Default if no distance specified
    "default": 5.0,
}

# ============================================================================
# NORMALIZATION FUNCTIONS
# ============================================================================

def normalize_metro_area(text: str) -> Optional[List[str]]:
    """
    Normalize metro area abbreviations to list of cities.
    
    Args:
        text: User input text (e.g., "DFW", "Bay Area")
        
    Returns:
        List of cities in the metro area, or None if not recognized
    """
    text_lower = text.lower().strip()
    
    # Direct match
    if text_lower in METRO_AREAS:
        return METRO_AREAS[text_lower]
    
    # Partial match (e.g., "dfw area" -> "dfw")
    for key in METRO_AREAS.keys():
        if key in text_lower or text_lower in key:
            return METRO_AREAS[key]
    
    return None


def normalize_real_estate_terms(text: str) -> str:
    """
    Expand real estate abbreviations in text.
    
    Args:
        text: User input text with potential abbreviations
        
    Returns:
        Text with abbreviations expanded
    """
    result = text.lower()
    
    # Sort by length (longest first) to avoid partial replacements
    sorted_terms = sorted(REAL_ESTATE_TERMS.items(), key=lambda x: len(x[0]), reverse=True)
    
    for abbrev, full_term in sorted_terms:
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(abbrev) + r'\b'
        result = re.sub(pattern, full_term, result, flags=re.IGNORECASE)
    
    return result


def normalize_poi_category(text: str) -> Optional[str]:
    """
    Identify POI category from user input.
    
    Args:
        text: User input text (e.g., "near schools", "close to parks")
        
    Returns:
        POI category name, or None if not recognized
    """
    text_lower = text.lower()
    
    for category, keywords in POI_CATEGORIES.items():
        for keyword in keywords:
            if keyword in text_lower:
                return category
    
    return None


def extract_distance_preference(text: str) -> float:
    """
    Extract distance preference from user input.
    
    Args:
        text: User input text (e.g., "within 1 mile", "walking distance")
        
    Returns:
        Distance in miles
    """
    text_lower = text.lower()
    
    # Check for explicit distance patterns
    # Pattern: "within X miles", "X mile", "X mi"
    mile_pattern = r'(\d+(?:\.\d+)?)\s*(?:mile|mi|miles)'
    match = re.search(mile_pattern, text_lower)
    if match:
        return float(match.group(1))
    
    # Check for keyword-based distances
    for keyword, distance in DISTANCE_KEYWORDS.items():
        if keyword in text_lower:
            return distance
    
    # Default distance
    return DISTANCE_KEYWORDS["default"]


def get_poi_keywords(category: str) -> List[str]:
    """
    Get all keywords for a POI category.
    
    Args:
        category: POI category name
        
    Returns:
        List of keywords for the category
    """
    return POI_CATEGORIES.get(category, [])


# ============================================================================
# TESTING FUNCTIONS
# ============================================================================

if __name__ == "__main__":
    # Test metro area normalization
    print("=== Metro Area Tests ===")
    print(f"DFW: {normalize_metro_area('DFW')}")
    print(f"Bay Area: {normalize_metro_area('Bay Area')}")
    print(f"dmv: {normalize_metro_area('dmv')}")
    
    # Test real estate term expansion
    print("\n=== Real Estate Term Tests ===")
    print(f"4 bd 3 ba with HOA: {normalize_real_estate_terms('4 bd 3 ba with HOA')}")
    print(f"2500 sqft: {normalize_real_estate_terms('2500 sqft')}")
    
    # Test POI category detection
    print("\n=== POI Category Tests ===")
    print(f"near schools: {normalize_poi_category('near schools')}")
    print(f"close to parks: {normalize_poi_category('close to parks')}")
    print(f"shopping malls nearby: {normalize_poi_category('shopping malls nearby')}")
    
    # Test distance extraction
    print("\n=== Distance Extraction Tests ===")
    print(f"within 2 miles: {extract_distance_preference('within 2 miles')}")
    print(f"walking distance: {extract_distance_preference('walking distance')}")
    print(f"near: {extract_distance_preference('near')}")
