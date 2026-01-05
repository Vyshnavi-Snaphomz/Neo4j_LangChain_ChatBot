"""
Smart Routing System for Snaphomz
Determines whether to use template/tool responses (cheap) or GPT reasoning (expensive)
"""

from typing import Dict, Any, Optional
import re


class SmartRouter:
    """
    Routes queries to appropriate handler based on complexity and cost
    """
    
    def __init__(self):
        # Template responses for common questions
        self.templates = {
            "what_is_pmi": {
                "pattern": r"what is (pmi|private mortgage insurance)",
                "response": """**PMI (Private Mortgage Insurance)** is insurance that protects the lender if you default on your loan.

**When it's required:**
• Down payment < 20% of home price
• Conventional loans only (not FHA/VA)

**Cost:**
• Typically 0.5% - 1.5% of loan amount annually
• Example: $300k loan = $1,500-$4,500/year ($125-$375/month)

**How to remove it:**
• Once you reach 20% equity (80% LTV)
• Request removal when you hit 20%
• Automatically removed at 78% LTV

**Actionable:** Aim for 20% down payment to avoid PMI, or plan to refinance/request removal once you reach 20% equity.""",
                "cost": 0
            },
            "what_is_hoa": {
                "pattern": r"what is (hoa|homeowners association)",
                "response": """**HOA (Homeowners Association)** is an organization that makes and enforces rules for a subdivision, planned community, or condo.

**What it covers:**
• Common area maintenance (landscaping, pools, gyms)
• Exterior building maintenance (condos)
• Trash collection, snow removal
• Community amenities

**Cost:**
• Typical range: $200-$600/month
• Luxury communities: $1,000+/month
• Affects your buying power (included in DTI)

**Pros:**
• Maintained common areas
• Amenities (pool, gym, clubhouse)
• Property value protection

**Cons:**
• Monthly fees (forever)
• Rules and restrictions
• Special assessments possible

**Actionable:** Factor HOA fees into your monthly budget. Ask for HOA financial statements and meeting minutes before buying.""",
                "cost": 0
            },
            "closing_cost_range": {
                "pattern": r"how much (are|is) closing costs?|what (are|is) typical closing costs?",
                "response": """**Typical Closing Costs: 2-5% of purchase price**

**Breakdown:**

**Lender Fees (1-2%):**
• Origination fee: 0.5-1% of loan
• Underwriting: $300-$900
• Credit report: $25-$50

**Title & Escrow (1-2%):**
• Title insurance: $1,000-$4,000
• Title search: $200-$400
• Escrow fee: $500-$2,000

**Government Fees (0.5-1%):**
• Recording fees: $100-$250
• Transfer taxes: 0.5-2% (varies by state)

**Other:**
• Appraisal: $300-$600
• Home inspection: $300-$500
• Attorney fees: $500-$1,500 (if required)

**Example: $500k home**
• Low end (2%): $10,000
• High end (5%): $25,000

**Actionable:** Budget 3% for closing costs. Use [snapaudit.snaphomz.com](https://snapaudit.snaphomz.com) to review your Closing Disclosure.""",
                "cost": 0
            },
            "down_payment_requirement": {
                "pattern": r"how much (do i need|is required) for (a )?down payment",
                "response": """**Down Payment Requirements by Loan Type:**

**Conventional Loans:**
• Minimum: 3% (first-time buyers)
• Standard: 5-20%
• No PMI: 20%+

**FHA Loans:**
• Minimum: 3.5%
• Credit score 580+
• PMI required (for life of loan)

**VA Loans (Veterans):**
• Minimum: 0%
• No PMI
• Funding fee: 2.3% (can be rolled into loan)

**USDA Loans (Rural):**
• Minimum: 0%
• Income limits apply
• Must be in eligible rural area

**Jumbo Loans:**
• Minimum: 10-20%
• Higher for luxury properties

**Example: $400k home**
• 3% down: $12,000
• 5% down: $20,000
• 20% down: $80,000

**Actionable:** Use [preapproval.snaphomz.com](https://preapproval.snaphomz.com) to see what you qualify for with your down payment.""",
                "cost": 0
            }
        }
        
        # Simple calculation patterns
        self.calculation_patterns = {
            "monthly_payment": r"(monthly payment|what will i pay per month)",
            "affordability": r"(how much can i afford|what can i buy)",
            "total_cost": r"(total cost|how much will it cost)"
        }
    
    def classify_complexity(self, query: str) -> Dict[str, Any]:
        """
        Classify query complexity
        
        Args:
            query: User query
            
        Returns:
            Classification result with routing decision
        """
        query_lower = query.lower().strip()
        
        # Check for template matches
        for template_id, template in self.templates.items():
            if re.search(template["pattern"], query_lower):
                return {
                    "complexity": "simple",
                    "route": "template",
                    "template_id": template_id,
                    "estimated_cost": 0,
                    "reason": "Exact template match"
                }
        
        # Check for simple calculations
        for calc_type, pattern in self.calculation_patterns.items():
            if re.search(pattern, query_lower):
                # Check if has enough context for deterministic calculation
                has_price = bool(re.search(r'\$?\d{1,3}(,?\d{3})*k?', query_lower))
                has_down = bool(re.search(r'down|deposit', query_lower))
                
                if has_price or has_down:
                    return {
                        "complexity": "simple",
                        "route": "tool",
                        "tool_type": calc_type,
                        "estimated_cost": 0,
                        "reason": "Deterministic calculation possible"
                    }
        
        # Check for complex reasoning needs
        complex_indicators = [
            "should i", "is it worth", "compare", "which is better",
            "what if", "help me decide", "recommend", "advice"
        ]
        
        is_complex = any(indicator in query_lower for indicator in complex_indicators)
        
        if is_complex:
            return {
                "complexity": "complex",
                "route": "gpt_reasoning",
                "estimated_cost": 0.05,  # Estimated GPT-4 cost
                "reason": "Requires reasoning and judgment"
            }
        
        # Default: moderate complexity, use existing LangGraph flow
        return {
            "complexity": "moderate",
            "route": "langgraph",
            "estimated_cost": 0.02,
            "reason": "Standard query processing"
        }
    
    def get_template_response(self, template_id: str) -> Optional[str]:
        """
        Get template response
        
        Args:
            template_id: Template identifier
            
        Returns:
            Template response or None
        """
        template = self.templates.get(template_id)
        return template["response"] if template else None
    
    def route_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main routing function
        
        Args:
            query: User query
            context: Optional context (previous results, user history, etc.)
            
        Returns:
            Routing decision with response or next action
        """
        classification = self.classify_complexity(query)
        
        # If template route, return response immediately
        if classification["route"] == "template":
            response = self.get_template_response(classification["template_id"])
            return {
                "route": "template",
                "response": response,
                "cost": 0,
                "tokens_used": 0
            }
        
        # If tool route, return tool type for execution
        if classification["route"] == "tool":
            return {
                "route": "tool",
                "tool_type": classification["tool_type"],
                "cost": 0,
                "tokens_used": 0,
                "requires_execution": True
            }
        
        # Otherwise, route to GPT/LangGraph
        return {
            "route": classification["route"],
            "estimated_cost": classification["estimated_cost"],
            "reason": classification["reason"],
            "requires_execution": True
        }
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics"""
        return {
            "template_count": len(self.templates),
            "calculation_types": len(self.calculation_patterns),
            "total_routes": 4  # template, tool, langgraph, gpt_reasoning
        }
