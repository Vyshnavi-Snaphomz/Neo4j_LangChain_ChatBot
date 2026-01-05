"""
Financial Analysis Handler

Provides comprehensive mortgage and affordability analysis including:
- Mortgage payment calculations
- Property tax and insurance estimates
- PMI calculations
- Scenario comparisons
- Financial recommendations
"""

from app.state import AgentState
from app.llm import get_llm
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import math
from app.nodes.search import neo4j_search

class FinancialParameters(BaseModel):
    """Financial parameters extracted from user query"""
    down_payment: Optional[float] = Field(None, description="Down payment amount in dollars")
    credit_tier: str = Field("good", description="Credit tier: excellent, good, fair, poor")
    loan_term_years: int = Field(30, description="Loan term in years")
    property_tax_rate: float = Field(0.012, description="Annual property tax rate (default 1.2%)")
    insurance_rate: float = Field(0.0035, description="Annual homeowner's insurance rate (default 0.35%)")
    interest_rate: Optional[float] = Field(None, description="Interest rate if specified")
    worst_case_rate_increase: float = Field(0.025, description="Worst-case rate increase (default 2.5%)")
    target_prices: Optional[List[float]] = Field(None, description="Target property prices to compare")
    monthly_income: Optional[float] = Field(None, description="Monthly household income")

class MortgageCalculation(BaseModel):
    """Complete mortgage calculation for a property"""
    property_price: float
    down_payment: float
    loan_amount: float
    ltv_ratio: float
    interest_rate: float
    monthly_pi: float  # Principal + Interest
    monthly_tax: float
    monthly_insurance: float
    monthly_pmi: float
    total_monthly: float
    total_annual: float
    
def extract_context_from_history(conversation_history: List[Dict], current_message: str) -> Dict[str, Any]:
    """
    Extract financial context from conversation history for follow-up questions.
    
    Returns dict with: target_prices, down_payment, credit_tier
    """
    import re
    
    context = {
        "target_prices": None,
        "down_payment": None,
        "credit_tier": None
    }
    
    # Look back through last 5 messages for context
    for msg in conversation_history[-5:]:
        if msg["role"] == "user":
            content = msg["content"].lower()
            
            # Extract prices (e.g., "900k vs 1.2M", "500k and 700k")
            price_patterns = [
                r'(\d+(?:\.\d+)?)\s*(k|m)\s*(?:vs|and|or)\s*(\d+(?:\.\d+)?)\s*(k|m)',
            ]
            
            for pattern in price_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    p1_str, unit1, p2_str, unit2 = match.groups()
                    p1 = float(p1_str)
                    p2 = float(p2_str)
                    
                    # Convert to actual values based on individual units
                    if unit1.lower() == 'k':
                        p1 *= 1000
                    elif unit1.lower() == 'm':
                        p1 *= 1000000
                    
                    if unit2.lower() == 'k':
                        p2 *= 1000
                    elif unit2.lower() == 'm':
                        p2 *= 1000000
                    
                    context["target_prices"] = [p1, p2]
                    break
            
            # Extract down payment
            down_patterns = [
                r'(\d+)\s*k\s+down',
                r'\$(\d+(?:,\d{3})*)\s+down',
            ]
            for pattern in down_patterns:
                match = re.search(pattern, content)
                if match:
                    down_str = match.group(1).replace(',', '')
                    down_val = float(down_str)
                    if 'k' in content:
                        down_val *= 1000
                    context["down_payment"] = down_val
                    break
            
            # Extract credit tier
            if 'excellent credit' in content:
                context["credit_tier"] = "excellent"
            elif 'good credit' in content:
                context["credit_tier"] = "good"
    
    return context

def extract_financial_parameters(state: AgentState) -> FinancialParameters:
    """
    Extract financial parameters from user query using LLM
    """
    llm = get_llm()
    last_message = state["messages"][-1][1]
    
    structured_llm = llm.with_structured_output(FinancialParameters)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Extract financial parameters from the user's query.

IMPORTANT EXTRACTIONS:
- Down payment: Look for "X down", "X downpayment", "putting X down"
- Credit: "strong credit" = excellent, "good credit" = good, "fair credit" = fair
- Loan term: Default to 30 years unless specified
- Property tax rate: Extract if mentioned (e.g., "1.2% tax"), otherwise use 1.2%
- Insurance rate: Extract if mentioned (e.g., "0.35% insurance"), otherwise use 0.35%
- Interest rate: Extract if mentioned, otherwise leave None
- Target prices: Extract all price points mentioned for comparison (e.g., "950k vs 1.15M" → [950000, 1150000])
- Monthly income: Extract if mentioned

EXAMPLES:
- "I have 180k down" → down_payment: 180000
- "strong credit" → credit_tier: "excellent"
- "Compare 950k home vs $1.15M home" → target_prices: [950000, 1150000]
- "rate +2.5%" → worst_case_rate_increase: 0.025
- "property tax 1.2%" → property_tax_rate: 0.012
- "insurance 0.35%" → insurance_rate: 0.0035

Extract all relevant financial parameters."""),
        ("user", "{input}")
    ])
    
    chain = prompt | structured_llm
    params = chain.invoke({"input": last_message})
    
    return params

def calculate_monthly_payment(principal: float, annual_rate: float, years: int) -> float:
    """
    Calculate monthly mortgage payment using standard formula:
    M = P * [r(1+r)^n] / [(1+r)^n - 1]
    
    Args:
        principal: Loan amount
        annual_rate: Annual interest rate (as decimal, e.g., 0.065 for 6.5%)
        years: Loan term in years
    
    Returns:
        Monthly payment amount
    """
    if annual_rate == 0:
        return principal / (years * 12)
    
    monthly_rate = annual_rate / 12
    num_payments = years * 12
    
    payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / \
              ((1 + monthly_rate)**num_payments - 1)
    
    return payment

def calculate_pmi_rate(ltv_ratio: float) -> float:
    """
    Calculate PMI rate based on LTV ratio
    
    PMI is required when LTV > 80%
    Rates based on industry standards:
    - LTV 80-85%: 0.50% annually
    - LTV 85-90%: 0.75% annually
    - LTV 90-95%: 1.00% annually
    - LTV 95%+: 1.25% annually
    
    Args:
        ltv_ratio: Loan-to-value ratio (as decimal)
    
    Returns:
        Annual PMI rate (as decimal)
    """
    if ltv_ratio <= 0.80:
        return 0.0
    elif ltv_ratio <= 0.85:
        return 0.005  # 0.5%
    elif ltv_ratio <= 0.90:
        return 0.0075  # 0.75%
    elif ltv_ratio <= 0.95:
        return 0.01  # 1.0%
    else:
        return 0.0125  # 1.25%

def get_current_mortgage_rate() -> float:
    """
    Get current mortgage rate from FRED API
    
    Falls back to conservative estimate if API fails
    
    Returns:
        Current 30-year fixed mortgage rate (as decimal)
    """
    import os
    import requests
    
    # Get API key from environment
    fred_api_key = os.getenv("FRED_API_KEY")
    
    if not fred_api_key:
        print("[DEBUG] FRED_API_KEY not found, using default rate 7.0%")
        return 0.070  # 7.0% fallback
    
    try:
        # FRED API endpoint for 30-year mortgage rate
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "series_id": "MORTGAGE30US",  # 30-year fixed rate mortgage average
            "api_key": fred_api_key,
            "limit": 1,
            "sort_order": "desc",
            "file_type": "json"
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "observations" in data and len(data["observations"]) > 0:
                rate_str = data["observations"][0]["value"]
                rate = float(rate_str) / 100  # Convert percentage to decimal
                print(f"[DEBUG] Current mortgage rate from FRED: {rate:.2%}")
                return rate
            else:
                print("[DEBUG] No data from FRED API, using default 7.0%")
                return 0.070
        else:
            print(f"[DEBUG] FRED API error {response.status_code}, using default 7.0%")
            return 0.070
            
    except Exception as e:
        print(f"[DEBUG] Error fetching FRED data: {e}, using default 7.0%")
        return 0.070  # 7.0% fallback


def calculate_mortgage_scenario(
    property_price: float,
    down_payment: float,
    interest_rate: float,
    params: FinancialParameters
) -> MortgageCalculation:
    """
    Calculate complete mortgage scenario
    
    Args:
        property_price: Property purchase price
        down_payment: Down payment amount
        interest_rate: Annual interest rate
        params: Financial parameters
    
    Returns:
        Complete mortgage calculation
    """
    # Calculate loan amount and LTV
    loan_amount = property_price - down_payment
    ltv_ratio = loan_amount / property_price
    
    # Calculate monthly P&I
    monthly_pi = calculate_monthly_payment(
        loan_amount,
        interest_rate,
        params.loan_term_years
    )
    
    # Calculate monthly property tax
    annual_tax = property_price * params.property_tax_rate
    monthly_tax = annual_tax / 12
    
    # Calculate monthly insurance
    annual_insurance = property_price * params.insurance_rate
    monthly_insurance = annual_insurance / 12
    
    # Calculate monthly PMI
    pmi_rate = calculate_pmi_rate(ltv_ratio)
    annual_pmi = loan_amount * pmi_rate
    monthly_pmi = annual_pmi / 12
    
    # Calculate total monthly payment
    total_monthly = monthly_pi + monthly_tax + monthly_insurance + monthly_pmi
    total_annual = total_monthly * 12
    
    return MortgageCalculation(
        property_price=property_price,
        down_payment=down_payment,
        loan_amount=loan_amount,
        ltv_ratio=ltv_ratio,
        interest_rate=interest_rate,
        monthly_pi=monthly_pi,
        monthly_tax=monthly_tax,
        monthly_insurance=monthly_insurance,
        monthly_pmi=monthly_pmi,
        total_monthly=total_monthly,
        total_annual=total_annual
    )

def select_properties_by_price(
    previous_results: List[Dict],
    target_price: float,
    tolerance: float = 0.10
) -> List[Dict]:
    """
    Select up to 3 properties near target price
    
    Args:
        previous_results: List of properties from search
        target_price: Target price
        tolerance: Price tolerance (default 10%)
    
    Returns:
        List of up to 3 properties near target price
    """
    min_price = target_price * (1 - tolerance)
    max_price = target_price * (1 + tolerance)
    
    # Filter properties in range
    filtered = [
        p for p in previous_results
        if min_price <= p.get("price", 0) <= max_price
    ]
    
    # Sort by proximity to target
    filtered.sort(key=lambda p: abs(p.get("price", 0) - target_price))
    
    # Return top 3
    return filtered[:3]

def fetch_properties_for_price_band(
    state: AgentState,
    target_price: float,
    location_entities: Dict[str, Any],
    tolerance: float = 0.10
) -> List[Dict]:
    """
    Fetch real properties from Neo4j for a specific price band
    
    Args:
        state: Current agent state
        target_price: Target price point
        location_entities: Location filters (city, state, etc.)
        tolerance: Price tolerance (default 10%)
    
    Returns:
        List of up to 3 properties near target price
    """
    min_price = target_price * (1 - tolerance)
    max_price = target_price * (1 + tolerance)
    
    # Build search entities for this price band
    search_entities = {
        **location_entities,
        "min_price": min_price,
        "max_price": max_price
    }
    
    # Create temporary state for search
    search_state = {
        **state,
        "extracted_entities": search_entities
    }
    
    # Execute Neo4j search
    result = neo4j_search(search_state)
    properties = result.get("search_results", [])
    
    # FILTER: Remove extreme outliers and ensure realistic comparables
    filtered = []
    seen_prices = set()
    
    for prop in properties:
        # Skip if missing critical data
        if not prop.get("price"):
            continue
        
        # Skip extreme bed/bath outliers (likely commercial or data errors)
        beds = prop.get("beds", 0)
        baths = prop.get("baths", 0)
        if beds and beds > 7:
            continue
        if baths and baths > 7:
            continue
        
        # Skip near-duplicate prices (within $1000)
        price = prop.get("price")
        if any(abs(price - seen) < 1000 for seen in seen_prices):
            continue
        
        seen_prices.add(price)
        filtered.append(prop)
    
    # Prefer single-family homes if available
    single_family = [p for p in filtered if p.get("homeType") in ["SINGLE_FAMILY", "single_family", "Single Family"]]
    if len(single_family) >= 3:
        filtered = single_family
    
    # Return top 3
    return filtered[:3]

def detect_mixed_intent(last_message: str, params: FinancialParameters) -> Dict[str, Any]:
    """
    Detect if user wants both financial analysis AND property listings
    
    Returns location entities if mixed intent detected, None otherwise
    """
    from app.llm import get_llm
    from langchain_core.prompts import ChatPromptTemplate
    from pydantic import BaseModel, Field
    from typing import Optional, List
    
    class MixedIntentDetection(BaseModel):
        has_location: bool = Field(description="True if user mentions a location (city, state, metro area)")
        wants_listings: bool = Field(description="True if user asks to 'show options', 'compare homes', 'find properties', etc.")
        city: Optional[str] = Field(None, description="City name if mentioned")
        cities: Optional[List[str]] = Field(None, description="List of cities for metro areas (e.g., DFW)")
        state: Optional[str] = Field(None, description="State name if mentioned")
    
    llm = get_llm()
    structured_llm = llm.with_structured_output(MixedIntentDetection)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Analyze if the user wants BOTH financial analysis AND real property listings.

LOCATION DETECTION:
- Look for city names: "Dallas", "Austin", "San Francisco", etc.
- Look for state names: "Texas", "California", "TX", "CA", etc.
- Look for metro areas: "DFW" (Dallas-Fort Worth), "Bay Area", etc.

METRO AREA MAPPINGS:
- "DFW" or "Dallas-Fort Worth" → cities: ["Dallas", "Fort Worth", "Arlington", "Plano", "Irving"]
- "Bay Area" → cities: ["San Francisco", "Oakland", "San Jose"]

LISTING REQUEST DETECTION:
- "show options", "show me homes", "find properties"
- "compare homes", "compare properties"
- "show 3 options", "give me examples"
- Any request to see actual listings

Set has_location=True if location mentioned.
Set wants_listings=True if user asks to see properties.

Examples:
- "I have 180k down. Should I buy 950k or 1.15M home in DFW? Show 3 options each" 
  → has_location=True, wants_listings=True, cities=["Dallas", "Fort Worth", "Arlington", "Plano", "Irving"], state="Texas"
  
- "Compare 950k vs 1.15M home with 180k down"
  → has_location=False, wants_listings=False
  
- "Show me homes in Austin under 500k"
  → has_location=True, wants_listings=True, city="Austin", state="Texas"
"""),
        ("user", "{input}")
    ])
    
    chain = prompt | structured_llm
    result = chain.invoke({"input": last_message})
    
    if result.has_location and result.wants_listings:
        entities = {}
        if result.city:
            entities["city"] = result.city
        if result.cities:
            entities["cities"] = result.cities
        if result.state:
            entities["state"] = result.state
        return entities
    
    return None

def format_property_listing(prop: Dict, index: int) -> str:
    """Format a single property for display"""
    output = f"\n**Option {index}:**\n"
    
    if prop.get("price"):
        output += f"- **Price:** ${prop['price']:,.0f}\n"
    
    location_parts = [prop.get("streetAddress"), prop.get("city"), prop.get("state")]
    location_str = ", ".join([str(p) for p in location_parts if p])
    if location_str:
        output += f"- **Location:** {location_str}\n"
    
    # Show all available specs (beds, baths, sqft)
    specs = []
    beds = prop.get("beds")
    baths = prop.get("baths")
    living_area = prop.get("livingArea")
    
    if beds is not None:
        specs.append(f"{int(beds)} bed")
    if baths is not None:
        specs.append(f"{baths} bath")
    if living_area:
        specs.append(f"{living_area:,.0f} sqft")
    
    if specs:
        output += f"- **Specs:** {' | '.join(specs)}\n"
    
    if prop.get("yearBuilt"):
        output += f"- **Built:** {prop['yearBuilt']}\n"
    
    if prop.get("url"):
        output += f"- **Listing:** {prop['url']}\n"
    elif prop.get("hdpUrl"):
        output += f"- **Listing:** https://www.zillow.com{prop['hdpUrl']}\n"
    
    return output

def generate_comparison_table(
    scenarios: List[MortgageCalculation],
    scenario_names: List[str]
) -> str:
    """
    Generate markdown comparison table
    
    Args:
        scenarios: List of mortgage calculations
        scenario_names: Names for each scenario
    
    Returns:
        Formatted markdown table
    """
    output = "\n## 💰 Financial Comparison\n\n"
    
    # Build header
    header = "| Metric |"
    separator = "|--------|"
    for name in scenario_names:
        header += f" {name} |"
        separator += "--------|"
    output += header + "\n" + separator + "\n"
    
    # Add rows
    rows = [
        ("**Purchase Price**", [f"${s.property_price:,.0f}" for s in scenarios]),
        ("Down Payment", [f"${s.down_payment:,.0f}" for s in scenarios]),
        ("Loan Amount", [f"${s.loan_amount:,.0f}" for s in scenarios]),
        ("LTV Ratio", [f"{s.ltv_ratio:.1%}" for s in scenarios]),
        ("Interest Rate", [f"{s.interest_rate:.2%}" for s in scenarios]),
        ("**Monthly P&I**", [f"${s.monthly_pi:,.0f}" for s in scenarios]),
        ("Monthly Tax", [f"${s.monthly_tax:,.0f}" for s in scenarios]),
        ("Monthly Insurance", [f"${s.monthly_insurance:,.0f}" for s in scenarios]),
        ("Monthly PMI", [f"${s.monthly_pmi:,.0f}" for s in scenarios]),
        ("**TOTAL MONTHLY**", [f"**${s.total_monthly:,.0f}**" for s in scenarios]),
        ("**TOTAL ANNUAL**", [f"**${s.total_annual:,.0f}**" for s in scenarios]),
    ]
    
    for metric, values in rows:
        row = f"| {metric} |"
        for value in values:
            row += f" {value} |"
        output += row + "\n"
    
    return output

def generate_recommendation(
    scenarios: List[MortgageCalculation],
    params: FinancialParameters
) -> str:
    """
    Generate financial recommendation
    
    Args:
        scenarios: List of mortgage calculations
        params: Financial parameters
    
    Returns:
        Recommendation text with reasoning
    """
    output = "\n## 🎯 Financial Recommendation\n\n"
    
    # Affordability analysis (28% rule)
    if params.monthly_income:
        output += "### Affordability Analysis (28% Rule)\n\n"
        max_affordable = params.monthly_income * 0.28
        
        for i, scenario in enumerate(scenarios, 1):
            ratio = scenario.total_monthly / params.monthly_income
            status = "✅ Affordable" if ratio <= 0.28 else "⚠️ Tight" if ratio <= 0.35 else "❌ Risky"
            output += f"- **Scenario {i}**: {ratio:.1%} of income ({status})\n"
        
        output += f"\nRecommended max: ${max_affordable:,.0f}/month\n\n"
    
    # Compare scenarios
    if len(scenarios) >= 2:
        diff = scenarios[1].total_monthly - scenarios[0].total_monthly
        diff_pct = (diff / scenarios[0].total_monthly) * 100
        
        output += f"### Monthly Payment Difference\n\n"
        output += f"Scenario 2 costs **${diff:,.0f} more per month** ({diff_pct:.1f}% increase)\n\n"
        
        # PMI analysis
        has_pmi = [s.monthly_pmi > 0 for s in scenarios]
        
        output += "### Recommendation\n\n"
        
        # Decision logic
        if has_pmi[0] and not has_pmi[1]:
            output += "✅ **Recommended: Scenario 2**\n\n"
            output += "**Reasons**:\n"
            output += "- No PMI required (saves money long-term)\n"
            output += "- Better loan-to-value ratio\n"
        elif not has_pmi[0] and has_pmi[1]:
            output += "✅ **Recommended: Scenario 1**\n\n"
            output += "**Reasons**:\n"
            output += "- No PMI required (LTV ≤ 80%)\n"
            output += f"- Lower monthly payment (${diff:,.0f} less)\n"
            output += "- More financial cushion for emergencies\n"
        elif diff_pct > 20:
            output += "✅ **Recommended: Scenario 1 (Lower Price)**\n\n"
            output += "**Reasons**:\n"
            output += f"- Significantly lower monthly payment ({diff_pct:.1f}% less)\n"
            output += "- Better debt-to-income ratio\n"
            output += "- More flexibility for savings/investments\n"
        else:
            output += "⚖️ **Both Options Are Viable**\n\n"
            output += "**Considerations**:\n"
            output += f"- Monthly difference is manageable (${diff:,.0f})\n"
            output += "- Choose based on property features and location\n"
            output += "- Ensure emergency fund covers 6 months of payments\n"
        
        # Additional insights
        output += "\n### Key Insights\n\n"
        
        for i, scenario in enumerate(scenarios, 1):
            pmi_cost = scenario.monthly_pmi * 12
            if pmi_cost > 0:
                output += f"- **Scenario {i}**: Paying ${pmi_cost:,.0f}/year in PMI until LTV reaches 80%\n"
        
        # Calculate break-even for PMI
        if has_pmi[0] and not has_pmi[1]:
            pmi_annual = scenarios[0].monthly_pmi * 12
            price_diff = scenarios[1].property_price - scenarios[0].property_price
            years_to_breakeven = price_diff / pmi_annual
            output += f"- PMI break-even: ~{years_to_breakeven:.1f} years\n"
    
    return output

def financial_analysis_handler(state: AgentState) -> Dict[str, Any]:
    """
    Main financial analysis handler
    
    Processes financial analysis queries and generates comprehensive
    mortgage comparisons with recommendations.
    
    Supports MIXED INTENT: Financial reasoning + real property listings
    """
    print("[DEBUG] Financial analysis handler invoked")
    
    last_message = state["messages"][-1][1]
    conversation_history = state.get("conversation_history", [])
    
    # Extract financial parameters
    params = extract_financial_parameters(state)
    print(f"[DEBUG] Extracted parameters: down_payment={params.down_payment}, target_prices={params.target_prices}")
    
    # If missing critical params, try to extract from conversation history
    if not params.target_prices or not params.down_payment:
        context = extract_context_from_history(conversation_history, last_message)
        print(f"[DEBUG] Extracted context from history: {context}")
        
        if not params.target_prices and context["target_prices"]:
            params.target_prices = context["target_prices"]
            print(f"[DEBUG] Using target_prices from context: {params.target_prices}")
        
        if not params.down_payment and context["down_payment"]:
            params.down_payment = context["down_payment"]
            print(f"[DEBUG] Using down_payment from context: {params.down_payment}")
        
        if not params.credit_tier and context["credit_tier"]:
            params.credit_tier = context["credit_tier"]
    
    # DEFAULT HANDLING: If no down payment specified, use 20% of lowest price tier
    if params.down_payment is None:
        if params.target_prices:
            default_down_payment = params.target_prices[0] * 0.20  # 20% down
        else:
            default_down_payment = 100000  # Fallback: $100k
        params.down_payment = default_down_payment
        print(f"[DEBUG] No down payment specified, using default: ${default_down_payment:,.0f}")
    
    # DEFAULT HANDLING: If no target prices, cannot proceed
    if not params.target_prices:
        return {
            "final_response": "I need price points to compare. Please specify target prices (e.g., 'Compare 500k vs 700k homes in [location]')."
        }
    
    # Detect mixed intent (financial + property search)
    location_entities = detect_mixed_intent(last_message, params)
    is_mixed_intent = location_entities is not None
    
    print(f"[DEBUG] Mixed intent: {is_mixed_intent}, location: {location_entities}")
    
    # Get current mortgage rate
    if params.interest_rate is None:
        current_rate = get_current_mortgage_rate()
    else:
        current_rate = params.interest_rate
    
    worst_case_rate = current_rate + params.worst_case_rate_increase
    
    print(f"[DEBUG] Rates: current={current_rate:.2%}, worst-case={worst_case_rate:.2%}")
    
    # Build scenarios
    scenarios_worst = []
    scenario_names = []
    properties_by_tier = {}  # Store properties for each price tier
    
    if params.target_prices:
        # User specified target prices
        for i, target_price in enumerate(params.target_prices, 1):
            # If mixed intent, fetch real properties for this price tier
            if is_mixed_intent:
                print(f"[DEBUG] Fetching properties for ${target_price:,.0f} tier")
                properties = fetch_properties_for_price_band(
                    state,
                    target_price,
                    location_entities,
                    tolerance=0.10
                )
                properties_by_tier[i] = properties
                print(f"[DEBUG] Found {len(properties)} properties for tier {i}")
            
            # Calculate worst-case scenario
            scenario_worst = calculate_mortgage_scenario(
                target_price,
                params.down_payment,
                worst_case_rate,
                params
            )
            
            scenarios_worst.append(scenario_worst)
            scenario_names.append(f"${target_price/1000:.0f}k Home")
    
    # Generate response
    response = "\n# 🏠 Financial Analysis\n\n"
    
    # Worst-case scenarios (primary focus)
    response += f"## Worst-Case Scenario ({worst_case_rate:.2%})\n"
    response += generate_comparison_table(scenarios_worst, scenario_names)
    
    # If mixed intent, show property listings
    if is_mixed_intent and properties_by_tier:
        response += "\n## 🏡 Property Options\n\n"
        
        global_index = 1  # Track global property number across all tiers
        
        for tier_idx, properties in properties_by_tier.items():
            tier_price = params.target_prices[tier_idx - 1]
            response += f"\n### ${tier_price/1000:.0f}k Tier Options\n"
            
            if properties:
                for local_idx, prop in enumerate(properties, 1):
                    # Show both tier-local and global numbering
                    response += f"\n**Option {local_idx} (Property #{global_index} overall):**\n"
                    
                    # Format property details
                    if prop.get("price"):
                        response += f"- **Price:** ${prop['price']:,.0f}\n"
                    
                    location_parts = [prop.get("streetAddress"), prop.get("city"), prop.get("state")]
                    location_str = ", ".join([str(p) for p in location_parts if p])
                    if location_str:
                        response += f"- **Location:** {location_str}\n"
                    
                    specs = []
                    if prop.get("beds") is not None:
                        specs.append(f"{int(prop['beds'])} bed")
                    if prop.get("baths") is not None:
                        specs.append(f"{prop['baths']} bath")
                    if prop.get("livingArea"):
                        specs.append(f"{prop['livingArea']:,.0f} sqft")
                    
                    if specs:
                        response += f"- **Specs:** {' | '.join(specs)}\n"
                    
                    if prop.get("yearBuilt"):
                        response += f"- **Built:** {prop['yearBuilt']}\n"
                    
                    if prop.get("url"):
                        response += f"- **Listing:** {prop['url']}\n"
                    elif prop.get("hdpUrl"):
                        response += f"- **Listing:** https://www.zillow.com{prop['hdpUrl']}\n"
                    
                    global_index += 1
            else:
                response += f"\n*No properties found in the ${tier_price*0.9:,.0f} - ${tier_price*1.1:,.0f} range.*\n"
        
        # Add lifestyle tradeoff analysis
        if len(params.target_prices) >= 2:
            diff = scenarios_worst[1].total_monthly - scenarios_worst[0].total_monthly
            response += "\n## 💡 Lifestyle Tradeoffs\n\n"
            response += f"**Monthly Payment Difference:** ${diff:,.0f}\n\n"
            response += "**What the extra payment gets you:**\n"
            response += f"- Higher price tier (${params.target_prices[1]/1000:.0f}k vs ${params.target_prices[0]/1000:.0f}k)\n"
            response += "- Potentially larger home, better location, or newer construction\n"
            response += "- Review the property options above to assess value\n\n"
            response += "**Consider:**\n"
            response += "- Is the extra monthly payment sustainable?\n"
            response += "- Do the higher-tier properties justify the cost?\n"
            response += "- Will you have 6 months emergency fund after purchase?\n"
    
    # Recommendation
    response += generate_recommendation(scenarios_worst, params)
    
    # Methodology
    response += "\n---\n\n"
    response += "### 🧠 Analysis Methodology\n\n"
    response += "**Calculations Include**:\n"
    response += "- Principal & Interest (standard mortgage formula)\n"
    response += f"- Property Tax ({params.property_tax_rate:.1%} annually)\n"
    response += f"- Homeowner's Insurance ({params.insurance_rate:.2%} annually)\n"
    response += "- PMI (if LTV > 80%, rates: 0.5%-1.25% based on LTV)\n\n"
    response += "**Assumptions**:\n"
    response += f"- Loan term: {params.loan_term_years} years\n"
    response += f"- Down payment: ${params.down_payment:,.0f}\n"
    response += f"- Credit tier: {params.credit_tier or 'good (assumed)'}\n"
    
    if is_mixed_intent:
        response += f"- Property search: {location_entities}\n"
        response += "- Price tolerance: ±10% per tier\n"
    
    # Update previous_results if we fetched properties
    state_updates = {"final_response": response}
    if is_mixed_intent and properties_by_tier:
        # Flatten all properties from all tiers for reference
        all_properties = []
        for tier_properties in properties_by_tier.values():
            all_properties.extend(tier_properties)
        state_updates["previous_results"] = all_properties
        print(f"[DEBUG] Saved {len(all_properties)} properties to previous_results")
    
    return state_updates
