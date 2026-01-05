"""
Cost Tracking and Observability for Snaphomz
Tracks token usage, API costs, and routing decisions
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import os


class CostTracker:
    """
    Tracks costs and provides observability into system usage
    """
    
    def __init__(self, log_file: str = "./data/cost_log.jsonl"):
        self.log_file = log_file
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Pricing (as of 2024, adjust as needed)
        self.pricing = {
            "gpt-4": {
                "input": 0.03 / 1000,   # $0.03 per 1K input tokens
                "output": 0.06 / 1000   # $0.06 per 1K output tokens
            },
            "gpt-3.5-turbo": {
                "input": 0.0015 / 1000,
                "output": 0.002 / 1000
            },
            "gemini-pro": {
                "input": 0.00025 / 1000,  # Approximate
                "output": 0.0005 / 1000
            },
            "embeddings": {
                "cost_per_1k": 0.0001
            }
        }
    
    def log_interaction(
        self,
        user_id: str,
        query: str,
        route: str,
        response_type: str,
        tokens_used: Optional[Dict[str, int]] = None,
        cost: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an interaction
        
        Args:
            user_id: User identifier
            query: User query
            route: Routing decision (template/tool/langgraph/gpt_reasoning)
            response_type: Type of response
            tokens_used: Token counts {input, output, total}
            cost: Calculated cost
            metadata: Additional metadata
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "query": query[:200],  # Truncate for privacy
            "route": route,
            "response_type": response_type,
            "tokens_used": tokens_used or {},
            "cost": cost,
            "metadata": metadata or {}
        }
        
        # Append to log file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Calculate cost for a model call
        
        Args:
            model: Model name
            input_tokens: Input token count
            output_tokens: Output token count
            
        Returns:
            Total cost in USD
        """
        if model not in self.pricing:
            return 0.0
        
        pricing = self.pricing[model]
        input_cost = input_tokens * pricing["input"]
        output_cost = output_tokens * pricing["output"]
        
        return input_cost + output_cost
    
    def get_user_stats(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get usage statistics for a user
        
        Args:
            user_id: User identifier
            days: Number of days to look back
            
        Returns:
            Usage statistics
        """
        if not os.path.exists(self.log_file):
            return {"total_queries": 0, "total_cost": 0.0}
        
        total_queries = 0
        total_cost = 0.0
        route_counts = {}
        total_tokens = 0
        
        with open(self.log_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry["user_id"] == user_id:
                        total_queries += 1
                        total_cost += entry.get("cost", 0.0)
                        
                        route = entry.get("route", "unknown")
                        route_counts[route] = route_counts.get(route, 0) + 1
                        
                        tokens = entry.get("tokens_used", {})
                        total_tokens += tokens.get("total", 0)
                except:
                    continue
        
        return {
            "total_queries": total_queries,
            "total_cost": round(total_cost, 4),
            "total_tokens": total_tokens,
            "route_distribution": route_counts,
            "avg_cost_per_query": round(total_cost / total_queries, 4) if total_queries > 0 else 0
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get overall system statistics
        
        Returns:
            System-wide statistics
        """
        if not os.path.exists(self.log_file):
            return {"total_queries": 0, "total_cost": 0.0}
        
        total_queries = 0
        total_cost = 0.0
        unique_users = set()
        route_counts = {}
        
        with open(self.log_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    total_queries += 1
                    total_cost += entry.get("cost", 0.0)
                    unique_users.add(entry["user_id"])
                    
                    route = entry.get("route", "unknown")
                    route_counts[route] = route_counts.get(route, 0) + 1
                except:
                    continue
        
        # Calculate cost savings from routing
        template_queries = route_counts.get("template", 0)
        tool_queries = route_counts.get("tool", 0)
        saved_queries = template_queries + tool_queries
        estimated_savings = saved_queries * 0.02  # Assume $0.02 saved per template/tool query
        
        return {
            "total_queries": total_queries,
            "total_cost": round(total_cost, 4),
            "unique_users": len(unique_users),
            "route_distribution": route_counts,
            "cost_savings": {
                "queries_optimized": saved_queries,
                "estimated_savings_usd": round(estimated_savings, 4),
                "optimization_rate": round(saved_queries / total_queries * 100, 2) if total_queries > 0 else 0
            }
        }


class InsightsEngine:
    """
    Extracts and stores user insights for personalization
    """
    
    def __init__(self, storage_file: str = "./data/user_insights.json"):
        self.storage_file = storage_file
        os.makedirs(os.path.dirname(storage_file), exist_ok=True)
        self.insights = self._load_insights()
    
    def _load_insights(self) -> Dict[str, Any]:
        """Load insights from storage"""
        if os.path.exists(self.storage_file):
            with open(self.storage_file, "r") as f:
                return json.load(f)
        return {}
    
    def _save_insights(self) -> None:
        """Save insights to storage"""
        with open(self.storage_file, "w") as f:
            json.dump(self.insights, f, indent=2)
    
    def extract_signals(
        self,
        user_id: str,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Extract useful signals from user interaction
        
        Args:
            user_id: User identifier
            query: User query
            context: Additional context
        """
        if user_id not in self.insights:
            self.insights[user_id] = {
                "budget_signals": [],
                "location_interests": [],
                "preferences": {},
                "interaction_count": 0,
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat()
            }
        
        user_data = self.insights[user_id]
        user_data["interaction_count"] += 1
        user_data["last_seen"] = datetime.now().isoformat()
        
        # Extract budget signals
        import re
        budget_match = re.search(r'\$?(\d{1,3}(?:,?\d{3})*(?:k|K)?)', query)
        if budget_match:
            budget_str = budget_match.group(1)
            # Convert to number
            if 'k' in budget_str.lower():
                budget = int(budget_str.replace('k', '').replace('K', '').replace(',', '')) * 1000
            else:
                budget = int(budget_str.replace(',', ''))
            
            if budget > 50000:  # Likely a home price
                user_data["budget_signals"].append({
                    "amount": budget,
                    "timestamp": datetime.now().isoformat()
                })
                # Keep only last 5 signals
                user_data["budget_signals"] = user_data["budget_signals"][-5:]
        
        # Extract location interests
        location_keywords = ["austin", "dallas", "houston", "san antonio", "dfw", "texas"]
        for location in location_keywords:
            if location in query.lower():
                if location not in user_data["location_interests"]:
                    user_data["location_interests"].append(location)
        
        # Extract preferences
        if "school" in query.lower():
            user_data["preferences"]["cares_about_schools"] = True
        if "pool" in query.lower():
            user_data["preferences"]["wants_pool"] = True
        if "garage" in query.lower():
            user_data["preferences"]["wants_garage"] = True
        
        self._save_insights()
    
    def get_user_insights(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get insights for a user"""
        return self.insights.get(user_id)
    
    def get_personalization_hints(self, user_id: str) -> Dict[str, Any]:
        """
        Get personalization hints for routing
        
        Args:
            user_id: User identifier
            
        Returns:
            Personalization hints
        """
        insights = self.get_user_insights(user_id)
        if not insights:
            return {"is_new_user": True}
        
        # Calculate average budget
        budget_signals = insights.get("budget_signals", [])
        avg_budget = sum(s["amount"] for s in budget_signals) / len(budget_signals) if budget_signals else None
        
        return {
            "is_new_user": insights["interaction_count"] < 3,
            "is_returning": insights["interaction_count"] >= 3,
            "avg_budget": avg_budget,
            "preferred_locations": insights.get("location_interests", []),
            "preferences": insights.get("preferences", {}),
            "interaction_count": insights["interaction_count"]
        }
