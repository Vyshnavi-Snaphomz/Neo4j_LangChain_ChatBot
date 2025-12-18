import re
from typing import Optional

from graph import get_graph
from utils import get_session_id


_STATE_ALIASES = {
    "california": "CA",
    "texas": "TX",
    "new york": "NY",
    "florida": "FL",
}

_US_STATE_ABBRS = {
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
    "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
    "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY","DC",
}


def _extract_state(query: str) -> Optional[str]:
    q = (query or "").strip().lower()
    if not q:
        return None

    for name, abbr in _STATE_ALIASES.items():
        if name in q:
            return abbr

    # Prefer explicit "in XX" patterns.
    m = re.search(r"\b(?:in|within|near)\s+([A-Za-z]{2})\b", query or "", flags=re.IGNORECASE)
    if m:
        abbr = m.group(1).upper()
        if abbr in _US_STATE_ABBRS:
            return abbr

    m = re.search(r"\b([A-Z]{2})\b", query)
    if m:
        abbr = m.group(1).upper()
        if abbr in _US_STATE_ABBRS:
            return abbr

    # For lowercase 2-letter tokens, only accept valid state abbreviations
    # to avoid false positives like "at" -> "AT".
    stop = {"in", "at", "of", "to", "on", "or", "an", "as", "be", "we", "me", "my", "by", "up"}
    tokens = re.findall(r"\b([a-z]{2})\b", q)
    for t in reversed(tokens):
        if t in stop:
            continue
        abbr = t.upper()
        if abbr in _US_STATE_ABBRS:
            return abbr

    return None


def _extract_zip(query: str) -> Optional[str]:
    m = re.search(r"\b(\d{5})\b", query or "")
    return m.group(1) if m else None


def _parse_number_token(token: str) -> Optional[float]:
    """
    Parse tokens like "$450,000", "450000", "450k", "1.2m".
    """
    if token is None:
        return None
    t = str(token).strip().lower()
    t = t.replace("$", "").replace(",", "")
    m = re.fullmatch(r"(\d+(?:\.\d+)?)([km])?", t)
    if not m:
        return None
    val = float(m.group(1))
    suffix = m.group(2)
    if suffix == "k":
        val *= 1_000
    elif suffix == "m":
        val *= 1_000_000
    return val


def _is_likely_money(token: str) -> bool:
    t = (token or "").strip().lower()
    if not t:
        return False
    if "$" in t:
        return True
    if "k" in t or "m" in t:
        return True
    if "," in t:
        return True
    v = _parse_number_token(t)
    return v is not None and v >= 1000


def _extract_price_range(query: str) -> tuple[Optional[float], Optional[float]]:
    """
    Extract price constraints. Supports both explicit and implicit price phrases:
    - "under 800k", "below $1m", "between 500k and 900k"
    - "price under 800k"
    """
    q = (query or "").lower()
    if not q:
        return None, None

    num = r"(\$?\d[\d,]*(?:\.\d+)?\s*[km]?)"

    m = re.search(rf"\bbetween\s+{num}\s+and\s+{num}\b", q)
    if m and _is_likely_money(m.group(1)) and _is_likely_money(m.group(2)):
        return _parse_number_token(m.group(1)), _parse_number_token(m.group(2))

    m = re.search(rf"\b(?:under|below|less\s+than|up\s+to)\s+{num}\b", q)
    if m and _is_likely_money(m.group(1)):
        return None, _parse_number_token(m.group(1))

    # "maximum budget of 2000000" / "max price of 1.5m"
    m = re.search(rf"\b(?:max(?:imum)?\s+(?:budget|price)\s+of)\s+{num}\b", q)
    if m and _is_likely_money(m.group(1)):
        return None, _parse_number_token(m.group(1))

    m = re.search(rf"\b(?:over|above|more\s+than|at\s+least|minimum|min)\s+{num}\b", q)
    if m and _is_likely_money(m.group(1)):
        return _parse_number_token(m.group(1)), None

    m = re.search(rf"\bprice\b\s*(=|>=|<=|>|<)\s*{num}\b", q)
    if m and _is_likely_money(m.group(2)):
        op = m.group(1)
        v = _parse_number_token(m.group(2))
        if v is None:
            return None, None
        if op == "=":
            return v, v
        if op in (">", ">="):
            return v, None
        if op in ("<", "<="):
            return None, v

    return None, None


def _extract_range(query: str, *, field_patterns: list[str]) -> tuple[Optional[float], Optional[float]]:
    """
    Extract numeric min/max constraints for a field, supporting phrases like:
    - "under 500k", "below 500k", "less than 500k"
    - "over 500k", "above 500k", "more than 500k", "at least 500k"
    - "between 500k and 800k"
    - "price=500k" (treated as exact)
    """
    q = (query or "").lower()
    if not q:
        return None, None

    field_re = "(?:" + "|".join(field_patterns) + ")"
    num = r"(\$?\d[\d,]*(?:\.\d+)?\s*[km]?)"

    # between X and Y
    m = re.search(rf"\b{field_re}\b.*?\bbetween\s+{num}\s+and\s+{num}\b", q)
    if m:
        lo = _parse_number_token(m.group(1))
        hi = _parse_number_token(m.group(2))
        return lo, hi
    # between X and Y <field>
    m = re.search(rf"\bbetween\s+{num}\s+and\s+{num}\b.*?\b{field_re}\b", q)
    if m:
        lo = _parse_number_token(m.group(1))
        hi = _parse_number_token(m.group(2))
        return lo, hi

    # under/below/less than
    m = re.search(rf"\b{field_re}\b.*?\b(?:under|below|less\s+than|up\s+to)\s+{num}\b", q)
    if m:
        return None, _parse_number_token(m.group(1))
    # under/below ... <field>
    m = re.search(rf"\b(?:under|below|less\s+than|up\s+to)\s+{num}\b.*?\b{field_re}\b", q)
    if m:
        return None, _parse_number_token(m.group(1))

    # over/above/more than/at least/minimum
    m = re.search(rf"\b{field_re}\b.*?\b(?:over|above|more\s+than|at\s+least|minimum|min)\s+{num}\b", q)
    if m:
        return _parse_number_token(m.group(1)), None
    # over/above ... <field>
    m = re.search(rf"\b(?:over|above|more\s+than|at\s+least|minimum|min)\s+{num}\b.*?\b{field_re}\b", q)
    if m:
        return _parse_number_token(m.group(1)), None

    # explicit operator: field >= X / <= X / = X
    m = re.search(rf"\b{field_re}\b\s*(=|>=|<=|>|<)\s*{num}\b", q)
    if m:
        op = m.group(1)
        v = _parse_number_token(m.group(2))
        if v is None:
            return None, None
        if op == "=":
            return v, v
        if op in (">", ">="):
            return v, None
        if op in ("<", "<="):
            return None, v

    # plain "<num> <field>" is treated as minimum (e.g. "4 beds", "2.5 baths", "1500 sqft")
    m = re.search(rf"\b{num}\s*{field_re}\b", q)
    if m:
        v = _parse_number_token(m.group(1))
        return v, None

    return None, None


def _extract_unit_range(query: str, *, unit_patterns: list[str]) -> tuple[Optional[float], Optional[float]]:
    """
    Extract numeric min/max where the unit/field must be present (e.g. beds/baths/sqft/year built).
    This avoids mis-parsing phrases like "under 1m" (price) as beds/baths.
    """
    q = (query or "").lower()
    if not q:
        return None, None

    unit_re = "(?:" + "|".join(unit_patterns) + ")"
    num = r"(\d+(?:\.\d+)?)"

    # between X and Y <unit>
    m = re.search(rf"\bbetween\s+{num}\s+and\s+{num}\s*{unit_re}\b", q)
    if m:
        return float(m.group(1)), float(m.group(2))

    # <unit> between X and Y
    m = re.search(rf"\b{unit_re}\b.*?\bbetween\s+{num}\s+and\s+{num}\b", q)
    if m:
        return float(m.group(1)), float(m.group(2))

    # at least X <unit> / minimum X <unit>
    m = re.search(rf"\b(?:at\s+least|minimum|min)\s+{num}\s*{unit_re}\b", q)
    if m:
        return float(m.group(1)), None

    # <unit> at least X
    m = re.search(rf"\b{unit_re}\b.*?\b(?:at\s+least|minimum|min)\s+{num}\b", q)
    if m:
        return float(m.group(1)), None

    # explicit operator: <unit> >= X
    m = re.search(rf"\b{unit_re}\b\s*(=|>=|<=|>|<)\s*{num}\b", q)
    if m:
        op = m.group(1)
        v = float(m.group(2))
        if op == "=":
            return v, v
        if op in (">", ">="):
            return v, None
        if op in ("<", "<="):
            return None, v

    # plain "X <unit>" treated as minimum (e.g. "4 beds")
    m = re.search(rf"\b{num}\s*{unit_re}\b", q)
    if m:
        return float(m.group(1)), None

    return None, None


def _extract_bool_filter(query: str, field: str) -> Optional[bool]:
    """
    Parse simple boolean filters like:
    - "pool=true" / "pool=false"
    - "has pool" (defaults to True)
    """
    q = (query or "").strip().lower()
    if not q:
        return None

    # negative phrases
    if field == "pool":
        if re.search(r"\b(?:no|without)\s+(?:a\s+)?pool\b", q):
            return False

    # key=true/false
    m = re.search(rf"\b{re.escape(field)}\s*=\s*(true|false)\b", q)
    if m:
        return m.group(1) == "true"

    # key true/false (no '=')
    m = re.search(rf"\b{re.escape(field)}\s+(true|false)\b", q)
    if m:
        return m.group(1) == "true"

    # "with pool" / "has pool" -> true
    if field == "pool" and (
        re.search(r"\bwith\s+(?:a\s+)?pool\b", q)
        or re.search(r"\bhas\s+(?:a\s+)?pool\b", q)
        or re.search(r"\bpool\s+included\b", q)
    ):
        return True

    return None


def _extract_sort(query: str) -> tuple[str, str]:
    """
    Decide sort field + direction based on the query.
    """
    q = (query or "").lower()
    if not q:
        return "price", "ASC"

    if "cheapest" in q or "lowest price" in q:
        return "price", "ASC"
    if "most expensive" in q or "highest price" in q:
        return "price", "DESC"
    if "recent" in q or "newest" in q or "latest" in q:
        return "yearBuilt", "DESC"
    if "oldest" in q:
        return "yearBuilt", "ASC"
    if "largest" in q or "biggest" in q or "most square" in q:
        return "squareFeet", "DESC"
    if "smallest" in q:
        return "squareFeet", "ASC"

    return "price", "ASC"


def _should_clear_filters(query: str) -> bool:
    q = (query or "").lower()
    return bool(re.search(r"\b(reset|clear)\s+(filters|search)\b", q))


def _filter_clear_directives(query: str) -> set[str]:
    """
    Detect phrases like "any price" / "no budget" to clear previously applied filters.
    """
    q = (query or "").lower()
    clears = set()
    if re.search(r"\b(any\s+price|no\s+budget|remove\s+budget|any\s+budget)\b", q):
        clears.add("price")
    if re.search(r"\b(any\s+beds|any\s+bedrooms?|no\s+min(?:imum)?\s+beds?)\b", q):
        clears.add("beds")
    if re.search(r"\b(any\s+baths|any\s+bathrooms?|no\s+min(?:imum)?\s+baths?)\b", q):
        clears.add("baths")
    if re.search(r"\b(any\s+sqft|any\s+size|any\s+square\s+feet)\b", q):
        clears.add("sqft")
    if re.search(r"\b(any\s+year|any\s+age|any\s+year\s+built)\b", q):
        clears.add("year")
    if re.search(r"\b(any\s+pool|either\s+pool|pool\s+does(?:\s+not)?\s+matter)\b", q):
        clears.add("pool")
    if re.search(r"\b(any\s+state|anywhere|no\s+location)\b", q):
        clears.add("location")
    return clears


def _current_session_id() -> Optional[str]:
    try:
        return get_session_id()
    except Exception:
        return None


_listing_filters_by_session: dict[str, dict] = {}


def _parse_listing_filters(query: str) -> dict:
    query = (query or "").strip().strip('"').strip("'")
    state = _extract_state(query)
    zip_code = _extract_zip(query)
    has_pool = _extract_bool_filter(query, "pool")
    price_min, price_max = _extract_price_range(query)
    beds_min, beds_max = _extract_unit_range(query, unit_patterns=["beds?", "bedrooms?"])
    baths_min, baths_max = _extract_unit_range(query, unit_patterns=["baths?", "bathrooms?"])
    sqft_min, sqft_max = _extract_unit_range(
        query, unit_patterns=["sq\\s*ft", "sqft", "square\\s*feet", "square\\s*foot"]
    )
    year_min, year_max = _extract_unit_range(query, unit_patterns=["year\\s*built", "built"])
    sort_field, sort_dir = _extract_sort(query)
    return {
        "state": state,
        "zip": zip_code,
        "has_pool": has_pool,
        "price_min": price_min,
        "price_max": price_max,
        "beds_min": beds_min,
        "beds_max": beds_max,
        "baths_min": baths_min,
        "baths_max": baths_max,
        "sqft_min": sqft_min,
        "sqft_max": sqft_max,
        "year_min": year_min,
        "year_max": year_max,
        "sort_field": sort_field,
        "sort_dir": sort_dir,
    }


def _merge_listing_filters(prev: dict, new: dict, query: str) -> dict:
    merged = dict(prev or {})

    if _should_clear_filters(query):
        merged = {}

    clears = _filter_clear_directives(query)
    if "location" in clears:
        merged.pop("state", None)
        merged.pop("zip", None)
    if "pool" in clears:
        merged.pop("has_pool", None)
    if "price" in clears:
        merged.pop("price_min", None)
        merged.pop("price_max", None)
    if "beds" in clears:
        merged.pop("beds_min", None)
        merged.pop("beds_max", None)
    if "baths" in clears:
        merged.pop("baths_min", None)
        merged.pop("baths_max", None)
    if "sqft" in clears:
        merged.pop("sqft_min", None)
        merged.pop("sqft_max", None)
    if "year" in clears:
        merged.pop("year_min", None)
        merged.pop("year_max", None)

    # Anything explicitly provided in the new query overrides previous.
    for k, v in new.items():
        if v is None:
            continue
        merged[k] = v

    # Ensure sort always exists.
    merged.setdefault("sort_field", "price")
    merged.setdefault("sort_dir", "ASC")

    return merged


def search_listings(query: str) -> str:
    """
    Structured search over `(:Listing)` nodes.

    This does not require embeddings/vector indexes.
    """
    query = (query or "").strip().strip('"').strip("'")

    session_id = _current_session_id()
    new_filters = _parse_listing_filters(query)
    if session_id:
        prev_filters = _listing_filters_by_session.get(session_id, {})
        filters = _merge_listing_filters(prev_filters, new_filters, query)
        _listing_filters_by_session[session_id] = filters
    else:
        filters = new_filters

    state = filters.get("state")
    zip_code = filters.get("zip")
    has_pool = filters.get("has_pool")
    price_min, price_max = filters.get("price_min"), filters.get("price_max")
    beds_min, beds_max = filters.get("beds_min"), filters.get("beds_max")
    baths_min, baths_max = filters.get("baths_min"), filters.get("baths_max")
    sqft_min, sqft_max = filters.get("sqft_min"), filters.get("sqft_max")
    year_min, year_max = filters.get("year_min"), filters.get("year_max")
    sort_field, sort_dir = filters.get("sort_field", "price"), filters.get("sort_dir", "ASC")

    where = []
    params = {}
    if state:
        where.append("(coalesce(l.state, l.State) = $state)")
        params["state"] = state
    if zip_code:
        where.append("(toString(coalesce(l.zipCode, l.`Zip Code`)) = $zip)")
        params["zip"] = zip_code
    if has_pool is not None:
        # Support both boolean and string storage.
        where.append("(toBoolean(toString(coalesce(l.hasPool, l.`Has Pool`))) = $hasPool)")
        params["hasPool"] = has_pool
    if price_min is not None:
        where.append("(toFloat(coalesce(l.price, l.Price)) >= $priceMin)")
        params["priceMin"] = float(price_min)
    if price_max is not None:
        where.append("(toFloat(coalesce(l.price, l.Price)) <= $priceMax)")
        params["priceMax"] = float(price_max)
    if beds_min is not None:
        where.append("(toFloat(coalesce(l.bed, l.Beds)) >= $bedsMin)")
        params["bedsMin"] = float(beds_min)
    if beds_max is not None:
        where.append("(toFloat(coalesce(l.bed, l.Beds)) <= $bedsMax)")
        params["bedsMax"] = float(beds_max)
    if baths_min is not None:
        where.append("(toFloat(coalesce(l.bath, l.Baths)) >= $bathsMin)")
        params["bathsMin"] = float(baths_min)
    if baths_max is not None:
        where.append("(toFloat(coalesce(l.bath, l.Baths)) <= $bathsMax)")
        params["bathsMax"] = float(baths_max)
    if sqft_min is not None:
        where.append("(toFloat(coalesce(l.squareFoot, l.`Square Feet`)) >= $sqftMin)")
        params["sqftMin"] = float(sqft_min)
    if sqft_max is not None:
        where.append("(toFloat(coalesce(l.squareFoot, l.`Square Feet`)) <= $sqftMax)")
        params["sqftMax"] = float(sqft_max)
    if year_min is not None:
        where.append("(toFloat(coalesce(l.yearBuilt, l.`Year Built`)) >= $yearMin)")
        params["yearMin"] = float(year_min)
    if year_max is not None:
        where.append("(toFloat(coalesce(l.yearBuilt, l.`Year Built`)) <= $yearMax)")
        params["yearMax"] = float(year_max)

    where_clause = f"WHERE {' AND '.join(where)}" if where else ""

    order_expr = {
        "price": "price",
        "beds": "beds",
        "baths": "baths",
        "squareFeet": "squareFeet",
        "yearBuilt": "yearBuilt",
    }.get(sort_field, "price")

    cypher = f"""
MATCH (l:Listing)
{where_clause}
RETURN DISTINCT
  coalesce(l.address, l.Address) AS address,
  coalesce(l.state, l.State) AS state,
  coalesce(l.zipCode, l.`Zip Code`) AS zipCode,
  coalesce(l.price, l.Price) AS price,
  coalesce(l.bed, l.Beds) AS beds,
  coalesce(l.bath, l.Baths) AS baths,
  coalesce(l.squareFoot, l.`Square Feet`) AS squareFeet,
  coalesce(l.hasPool, l.`Has Pool`) AS hasPool,
  coalesce(l.yearBuilt, l.`Year Built`) AS yearBuilt
ORDER BY {order_expr} {sort_dir}
LIMIT 10
"""

    results = get_graph().query(cypher, params)
    if not results:
        criteria = []
        if state:
            criteria.append(f"state={state}")
        if zip_code:
            criteria.append(f"zip={zip_code}")
        if has_pool is not None:
            criteria.append(f"pool={has_pool}")
        if price_min is not None:
            criteria.append(f"minPrice={int(price_min)}")
        if price_max is not None:
            criteria.append(f"maxPrice={int(price_max)}")
        if beds_min is not None:
            criteria.append(f"minBeds={beds_min:g}")
        if baths_min is not None:
            criteria.append(f"minBaths={baths_min:g}")
        hint = f" for {', '.join(criteria)}" if criteria else ""
        return (
            f"I couldn't find any listings{hint}.\n\n"
            "Try asking with a 2-letter state code (e.g. CA, TX), a 5-digit zip code, or constraints like "
            "'under 800k', '3 beds', '2 baths', 'with pool', 'newest'."
        )

    applied = []
    if state:
        applied.append(f"state={state}")
    if zip_code:
        applied.append(f"zip={zip_code}")
    if has_pool is not None:
        applied.append(f"pool={has_pool}")
    if price_min is not None:
        applied.append(f"minPrice={int(price_min)}")
    if price_max is not None:
        applied.append(f"maxPrice={int(price_max)}")
    if beds_min is not None:
        applied.append(f"minBeds={beds_min:g}")
    if baths_min is not None:
        applied.append(f"minBaths={baths_min:g}")
    if sqft_min is not None:
        applied.append(f"minSqft={sqft_min:g}")
    if year_min is not None:
        applied.append(f"minYearBuilt={year_min:g}")
    applied.append(f"sort={order_expr} {sort_dir}")

    lines = ["Here are some matching listings:"]
    lines.append(f"Applied filters: {', '.join(applied)}")
    for r in results:
        lines.append(
            f"- {r.get('address')}, {r.get('state')} {r.get('zipCode')} | "
            f"${r.get('price')} | {r.get('beds')} bd / {r.get('baths')} ba | "
            f"{r.get('squareFeet')} sqft | pool={r.get('hasPool')} | built={r.get('yearBuilt')}"
        )
    return "\n".join(lines)


def search_schools(query: str) -> str:
    state = _extract_state(query)
    zip_code = _extract_zip(query)

    where = []
    params = {}
    if state:
        where.append("(coalesce(s.state, s.State) = $state)")
        params["state"] = state
    if zip_code:
        where.append("(toString(coalesce(s.zipCode, s.`Zip Code`)) = $zip)")
        params["zip"] = zip_code

    where_clause = f"WHERE {' AND '.join(where)}" if where else ""

    cypher = f"""
MATCH (s:School)
{where_clause}
RETURN
  coalesce(s.schoolName, s.`School Name`) AS name,
  coalesce(s.type, s.Type) AS type,
  coalesce(s.rating, s.Rating) AS rating,
  coalesce(s.state, s.State) AS state,
  coalesce(s.zipCode, s.`Zip Code`) AS zipCode,
  coalesce(s.studentCount, s.`Student Count`) AS studentCount
ORDER BY rating DESC
LIMIT 10
"""

    results = get_graph().query(cypher, params)
    if not results:
        return "I couldn't find any schools matching that query (try a state like TX or a zip code)."

    lines = ["Here are some matching schools:"]
    for r in results:
        lines.append(
            f"- {r.get('name')} ({r.get('type')}) | rating={r.get('rating')} | "
            f"{r.get('state')} {r.get('zipCode')} | students={r.get('studentCount')}"
        )
    return "\n".join(lines)


def search_colleges(query: str) -> str:
    state = _extract_state(query)
    zip_code = _extract_zip(query)

    where = []
    params = {}
    if state:
        where.append("(coalesce(c.state, c.State) = $state)")
        params["state"] = state
    if zip_code:
        where.append("(toString(coalesce(c.zipCode, c.`Zip Code`)) = $zip)")
        params["zip"] = zip_code

    where_clause = f"WHERE {' AND '.join(where)}" if where else ""

    cypher = f"""
MATCH (c:College)
{where_clause}
RETURN
  coalesce(c.collegeName, c.`College Name`) AS name,
  coalesce(c.type, c.Type) AS type,
  coalesce(c.ranking, c.Ranking) AS ranking,
  coalesce(c.state, c.State) AS state,
  coalesce(c.zipCode, c.`Zip Code`) AS zipCode,
  coalesce(c.tuition, c.Tuition) AS tuition
ORDER BY ranking ASC
LIMIT 10
"""

    results = get_graph().query(cypher, params)
    if not results:
        return "I couldn't find any colleges matching that query (try a state like CA or a zip code)."

    lines = ["Here are some matching colleges:"]
    for r in results:
        lines.append(
            f"- {r.get('name')} ({r.get('type')}) | rank={r.get('ranking')} | "
            f"{r.get('state')} {r.get('zipCode')} | tuition=${r.get('tuition')}"
        )
    return "\n".join(lines)
