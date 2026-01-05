from app.state import AgentState
from app.neo4j_client import neo4j_client

def neo4j_search(state: AgentState):
    """
    Neo4j search using ACTUAL database schema.
    
    Available fields in database:
    - price, state, city, streetAddress, zipcode
    - bedrooms, bathrooms
    - livingArea, lotSize, lotAreaValue
    - yearBuilt, homeType, homeStatus
    - description, url, embedding_text, embedding
    """
    entities = state.get("extracted_entities", {})
    
    print(f"[DEBUG] Search called with entities: {entities}")
    
    # Build Cypher query using actual available properties
    where_clauses = []
    params = {}
    
    # Handle state
    # US State Mapping
    us_states = {
        "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA",
        "colorado": "CO", "connecticut": "CT", "delaware": "DE", "florida": "FL", "georgia": "GA",
        "hawaii": "HI", "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA",
        "kansas": "KS", "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
        "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS", "missouri": "MO",
        "montana": "MT", "nebraska": "NE", "nevada": "NV", "new hampshire": "NH", "new jersey": "NJ",
        "new mexico": "NM", "new york": "NY", "north carolina": "NC", "north dakota": "ND", "ohio": "OH",
        "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
        "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT", "vermont": "VT",
        "virginia": "VA", "washington": "WA", "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY"
    }

    # Handle state
    if "state" in entities:
        state_input = entities["state"]
        # Normalize input to title case for generic match, and get code
        state_norm = state_input.lower()
        state_code = us_states.get(state_norm, state_input[:2].upper())
        
        # Match against Full Name (case insensitive) OR Abbreviation
        where_clauses.append("(toLower(p.state) = toLower($state_full) OR p.state = $state_code)")
        params["state_full"] = state_input
        params["state_code"] = state_code
        print(f"[DEBUG] State filter: '{state_input}' (Code: {state_code})")
    
    # Handle city (single or multiple cities for metro areas)
    if "cities" in entities and entities["cities"]:
        # Multi-city search (e.g., DFW, Bay Area)
        cities_list = entities["cities"]
        where_clauses.append("p.city IN $cities")
        params["cities"] = cities_list
        print(f"[DEBUG] Multi-city filter: {cities_list}")
    elif "city" in entities:
        # Single city search
        city_value = entities["city"]
        where_clauses.append("toLower(p.city) = toLower($city)")
        params["city"] = city_value
        print(f"[DEBUG] City filter: {city_value}")
    
    
    # Handle price
    if "max_price" in entities:
        where_clauses.append("p.price <= $max_price")
        params["max_price"] = entities["max_price"]
        print(f"[DEBUG] Price filter: <= {params['max_price']}")
        
    if "min_price" in entities:
        where_clauses.append("p.price >= $min_price")
        params["min_price"] = entities["min_price"]
        print(f"[DEBUG] Price filter: >= {params['min_price']}")
    
    # Handle beds
    if "beds" in entities:
        beds_value = entities["beds"]
        where_clauses.append("(p.bedrooms >= $beds OR p.bed >= $beds OR p.bedroom >= $beds)")
        params["beds"] = beds_value
        print(f"[DEBUG] Beds filter: >= {beds_value}")
    
    # Handle baths
    if "baths" in entities:
        baths_value = entities["baths"]
        where_clauses.append("(p.bathrooms >= $baths OR p.bath >= $baths OR p.bathroom >= $baths)")
        params["baths"] = baths_value
        print(f"[DEBUG] Baths filter: >= {baths_value}")
    
    # Handle keywords - search in description field
    if "keywords" in entities and entities["keywords"]:
        keywords = entities["keywords"]
        keyword_clauses = []
        for i, keyword in enumerate(keywords):
            param_name = f"keyword_{i}"
            # Search in BOTH description and embedding_text to ensure coverage
            keyword_clauses.append(f"(toLower(p.description) CONTAINS toLower(${param_name}) OR toLower(p.embedding_text) CONTAINS toLower(${param_name}))")
            params[param_name] = keyword
        
        if keyword_clauses:
            # Use OR for keywords - match any of them
            where_clauses.append(f"({' OR '.join(keyword_clauses)})")
            print(f"[DEBUG] Keyword filter: {keywords}")
    
    # Construct WHERE clause
    where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    # STRICT FILTER: Ensure we only return properties that have some description data
    where_clause += " AND (p.description IS NOT NULL OR size(p.embedding_text) > 20)"
    
    # Query ALL available fields including rich Zillow data
    # ORDER BY prioritizes:
    # 1. Exact Beds Match (if requested)
    # 2. Exact Baths Match (if requested)
    # 3. Rich Data (Description/Photos)
    # 4. Price (Descending/Quality)
    
    order_by_parts = []
    
    # 1. Exact Beds Match
    if "beds" in entities:
        # COALESCE ensures we match against the resolved value
        order_by_parts.append("(CASE WHEN COALESCE(p.bedrooms, p.bed, p.bedroom) = $beds THEN 1 ELSE 0 END) DESC")
        # Then closer beds are better (ASC)
        order_by_parts.append("COALESCE(p.bedrooms, p.bed, p.bedroom) ASC")

    # 2. Exact Baths Match
    if "baths" in entities:
        order_by_parts.append("(CASE WHEN COALESCE(p.bathrooms, p.bath, p.bathroom) = $baths THEN 1 ELSE 0 END) DESC")
        order_by_parts.append("COALESCE(p.bathrooms, p.bath, p.bathroom) ASC")

    # 3. Rich Data Priority
    order_by_parts.append("(CASE WHEN p.description IS NOT NULL AND size(p.description) > 50 THEN 1 ELSE 0 END) DESC")
    order_by_parts.append("(CASE WHEN p.yearBuilt IS NOT NULL THEN 1 ELSE 0 END) DESC")

    # 4. Price Priority
    if "min_price" in entities:
         # unique case: if looking for luxury (min price), sort ASC from that price point?
         # Or DESC to show most expensive? User said "exact... then greater".
         # For min_price 1M, exact is 1M. So ASC makes sense.
         order_by_parts.append("p.price ASC")
    else:
         # Normal budget search: Show highest quality (closest to max)
         order_by_parts.append("p.price DESC")

    order_by_clause = ", ".join(order_by_parts)

    cypher_query = f"""
    MATCH (p:Property)
    WHERE {where_clause}
    RETURN
      p.zpid AS zpid,
      p.price AS price,
      p.state AS state,
      p.city AS city,
      p.streetAddress AS streetAddress,
      p.zipcode AS zipcode,
      COALESCE(p.bedrooms, p.bed, p.bedroom) AS beds,
      COALESCE(p.bathrooms, p.bath, p.bathroom) AS baths,
      p.livingArea AS livingArea,
      p.lotSize AS lotSize,
      p.lotAreaValue AS lotAreaValue,
      p.yearBuilt AS yearBuilt,
      p.homeType AS homeType,
      p.homeStatus AS homeStatus,
      p.description AS description,
      p.url AS url,
      p.hdpUrl AS hdpUrl
    ORDER BY {order_by_clause}
    LIMIT 10
    """
    
    print(f"[DEBUG] Executing query with params: {params}")
    
    try:
        results = neo4j_client.query(cypher_query, params)
        
        print(f"[DEBUG] Query returned {len(results)} results")
        
        # Process results with all fields
        processed_results = []
        for r in results:
            processed_results.append({
                "zpid": r.get("zpid"),
                "price": r.get("price"),
                "state": r.get("state"),
                "city": r.get("city"),
                "streetAddress": r.get("streetAddress"),
                "zipcode": r.get("zipcode"),
                "beds": r.get("beds"),
                "baths": r.get("baths"),
                "livingArea": r.get("livingArea"),
                "lotSize": r.get("lotSize"),
                "lotAreaValue": r.get("lotAreaValue"),
                "yearBuilt": r.get("yearBuilt"),
                "homeType": r.get("homeType"),
                "homeStatus": r.get("homeStatus"),
                "description": r.get("description", ""),
                "url": r.get("url"),
                "hdpUrl": r.get("hdpUrl")
            })
        
        return {"search_results": processed_results}
    except Exception as e:
        print(f"Cypher Search Error: {e}")
        import traceback
        traceback.print_exc()
        return {"search_results": []}
