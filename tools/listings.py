import re
from typing import Optional, Tuple, Dict

from graph import get_graph


# ----------------------------
# Constants
# ----------------------------

 


# ----------------------------
# Basic extractors


_US_STATE_ABBRS = {
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
    "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
    "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY","DC","PR",
}

_STATE_ALIASES = {
    "california": "CA",
    "texas": "TX",
    "new york": "NY",
    "florida": "FL",
    "puerto rico": "PR",
    "puerto rica": "PR",
}

_ABBR_TO_STATE = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri",
    "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
    "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
    "DC": "District of Columbia", "PR": "Puerto Rico"
}


# ----------------------------
# Basic extractors
# ----------------------------

def _extract_state(query: str) -> Optional[str]:
    q = (query or "").lower()
    for name, abbr in sorted(_STATE_ALIASES.items(), key=lambda x: len(x[0]), reverse=True):
        if name in q:
            return abbr
    m = re.search(r"\b([a-zA-Z]{2})\b", query or "")
    if m and m.group(1).upper() in _US_STATE_ABBRS:
        return m.group(1).upper()
    return None


def _extract_zip(query: str) -> Optional[str]:
    m = re.search(r"\b(\d{5})\b", query or "")
    return m.group(1) if m else None


def _parse_money(token: str) -> Optional[float]:
    t = token.lower().replace("$", "").replace(",", "")
    m = re.fullmatch(r"(\d+(?:\.\d+)?)([km]?)", t)
    if not m:
        return None
    v = float(m.group(1))
    if m.group(2) == "k":
        v *= 1_000
    elif m.group(2) == "m":
        v *= 1_000_000
    return v


def _extract_price_range(query: str) -> Tuple[Optional[float], Optional[float]]:
    q = (query or "").lower()

    m = re.search(r"(?:under|less than|lower than)\s+(\$?\d[\d,]*[km]?)", q)
    if m:
        return None, _parse_money(m.group(1))

    m = re.search(r"(?:over|more than|greater than)\s+(\$?\d[\d,]*[km]?)", q)
    if m:
        return _parse_money(m.group(1)), None

    return None, None


def _extract_min_count(query: str, pattern: str) -> Optional[int]:
    m = re.search(rf"(\d+)\s+(?:{pattern})", query.lower())
    return int(m.group(1)) if m else None




# ----------------------------
# Main search
# ----------------------------

def _format_baths(baths_val: Optional[float]) -> str:
    if baths_val is None:
        return "N/A"
    full_baths = int(baths_val)
    half_baths = baths_val - full_baths
    parts = []
    if full_baths > 0:
        parts.append(f"{full_baths} {'bath' if full_baths == 1 else 'baths'}")
    if half_baths > 0:
        parts.append("1 half bath")
    return " and ".join(parts) if parts else "N/A"


def search_listings(query: str) -> str:
    query = query.strip()

    # Build filters from query
    filters = {
        "state": _extract_state(query),
        "zip": _extract_zip(query),
        "price_min": None,
        "price_max": None,
        "beds_min": _extract_min_count(query, "beds?|bedrooms?"),
        "baths_min": _extract_min_count(query, "baths?|bathrooms?"),
        "for_rent": "rent" in query.lower() or "renting" in query.lower(),
    }

    pmn, pmx = _extract_price_range(query)
    filters["price_min"] = pmn
    filters["price_max"] = pmx

    # Build Cypher
    where = []
    params = {}

    if filters.get("state"):
        # Check both abbreviation and full name
        where.append("(l.state = $state OR l.state = $stateFull)")
        params["state"] = filters["state"]
        params["stateFull"] = _ABBR_TO_STATE.get(filters["state"], filters["state"])

    if filters.get("zip"):
        where.append("toString(l.zipCode) = $zip")
        params["zip"] = filters["zip"]

    if filters.get("price_min") is not None:
        where.append("l.price >= $priceMin")
        params["priceMin"] = filters["price_min"]

    if filters.get("price_max") is not None:
        where.append("l.price <= $priceMax")
        params["priceMax"] = filters["price_max"]

    if filters.get("beds_min") is not None:
        where.append("l.beds >= $bedsMin")
        params["bedsMin"] = filters["beds_min"]

    if filters.get("baths_min") is not None:
        where.append("l.baths >= $bathsMin")
        params["bathsMin"] = filters["baths_min"]
    
    if filters.get("for_rent"):
        where.append("l.description CONTAINS 'rent'")

    where_clause = "WHERE " + " AND ".join(where) if where else ""

    cypher = f"""
    MATCH (l:Listing)
    {where_clause}
    RETURN
      l.street AS street,
      l.city AS city,
      l.state AS state,
      l.zipCode AS zipCode,
      l.price AS price,
      l.beds AS beds,
      l.baths AS baths,
      l.houseSize AS houseSize,
      l.description AS description,
      l.url AS url
    ORDER BY price ASC
    LIMIT 10
    """
    
    print("Filters:", filters)
    print("Cypher:", cypher)
    print("Params:", params)

    rows = get_graph().query(cypher, params)

    if not rows:
        return "No listings matched your criteria. Try relaxing price or location."

    lines = ["Here are matching listings:"]
    for r in rows:
        beds = r['beds'] if r['beds'] is not None else "N/A"
        baths = _format_baths(r['baths'])
        price = f"${r['price']:,}" if r['price'] is not None else "N/A"
        size = f"{r['houseSize']:,} sqft" if r['houseSize'] is not None else "N/A"
        description = r['description'] if r['description'] is not None else "No description available."
        url = r['url'] if r['url'] is not None else "No URL available."
        
        address_parts = [r.get('street'), r.get('city'), r.get('state'), r.get('zipCode')]
        address = ", ".join(filter(None, [str(p) for p in address_parts if p]))

        lines.append(
            f"- {address}\n"
            f"  Price: {price} | Beds: {beds} | Baths: {baths} | Size: {size}\n"
            f"  Description: {description}\n"
            f"  URL: {url}"
        )

    return "\n".join(lines)


def search_schools(query: str) -> str:
    query = query.strip()
    state = _extract_state(query)
    zip_code = _extract_zip(query)

    if not state and not zip_code:
        return "Please provide a state or zip code to search for schools."

    where = []
    params = {}

    if state:
        where.append("s.state = $state")
        params["state"] = state

    if zip_code:
        where.append("toString(s.zipCode) = $zip")
        params["zip"] = zip_code

    where_clause = "WHERE " + " AND ".join(where)

    cypher = f"""
    MATCH (s:School)
    {where_clause}
    RETURN s.name as name, s.city as city, s.state as state
    LIMIT 10
    """

    rows = get_graph().query(cypher, params)

    if not rows:
        return "No schools found matching your criteria."

    lines = ["Here are matching schools:"]
    for r in rows:
        lines.append(f"- {r['name']} ({r['city']}, {r['state']})")

    return "\n".join(lines)


def search_colleges(query: str) -> str:
    query = query.strip()
    state = _extract_state(query)
    zip_code = _extract_zip(query)

    if not state and not zip_code:
        return "Please provide a state or zip code to search for colleges."

    where = []
    params = {}

    if state:
        where.append("c.state = $state")
        params["state"] = state

    if zip_code:
        where.append("toString(c.zipCode) = $zip")
        params["zip"] = zip_code

    where_clause = "WHERE " + " AND ".join(where)

    cypher = f"""
    MATCH (c:College)
    {where_clause}
    RETURN c.name as name, c.city as city, c.state as state
    LIMIT 10
    """

    rows = get_graph().query(cypher, params)

    if not rows:
        return "No colleges found matching your criteria."

    lines = ["Here are matching colleges:"]
    for r in rows:
        lines.append(f"- {r['name']} ({r['city']}, {r['state']})")

    return "\n".join(lines)
