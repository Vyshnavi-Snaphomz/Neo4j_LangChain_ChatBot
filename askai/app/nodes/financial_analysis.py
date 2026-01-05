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
    mortgage comparisons with recommendations
    """
    print("[DEBUG] Financial analysis handler invoked")
    
    # Extract financial parameters
    params = extract_financial_parameters(state)
    print(f"[DEBUG] Extracted parameters: down_payment={params.down_payment}, target_prices={params.target_prices}")
    
    # Get current mortgage rate
    if params.interest_rate is None:
        current_rate = get_current_mortgage_rate()
    else:
        current_rate = params.interest_rate
    
    worst_case_rate = current_rate + params.worst_case_rate_increase
    
    print(f"[DEBUG] Rates: current={current_rate:.2%}, worst-case={worst_case_rate:.2%}")
    
    # Get previous search results
    previous_results = state.get("previous_results", [])
    
    # Build scenarios
    scenarios_current = []
    scenarios_worst = []
    scenario_names = []
    
    if params.target_prices:
        # User specified target prices
        for i, target_price in enumerate(params.target_prices, 1):
            # Try to find properties near target price
            if previous_results:
                matching_props = select_properties_by_price(previous_results, target_price)
                if matching_props:
                    # Use average price of matching properties
                    avg_price = sum(p.get("price", 0) for p in matching_props) / len(matching_props)
                    target_price = avg_price
            
            # Calculate scenarios
            scenario_current = calculate_mortgage_scenario(
                target_price,
                params.down_payment,
                current_rate,
                params
            )
            scenario_worst = calculate_mortgage_scenario(
                target_price,
                params.down_payment,
                worst_case_rate,
                params
            )
            
            scenarios_current.append(scenario_current)
            scenarios_worst.append(scenario_worst)
            scenario_names.append(f"${target_price/1000:.0f}k Home")
    
    # Generate response
    response = "\n# 🏠 Financial Analysis\n\n"
    
    # Current rate scenarios
    response += f"## Current Rate Scenario ({current_rate:.2%})\n"
    response += generate_comparison_table(scenarios_current, scenario_names)
    
    # Worst-case scenarios
    response += f"\n## Worst-Case Scenario ({worst_case_rate:.2%})\n"
    response += generate_comparison_table(scenarios_worst, scenario_names)
    
    # Recommendation
    response += generate_recommendation(scenarios_current, params)
    
    # Chain of thought
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
    response += f"- Credit tier: {params.credit_tier}\n"
    
    return {"final_response": response}
