"""
Telemetry Viewer for Snaphomz
View cost logs, user insights, and system statistics
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List

def view_cost_logs(limit: int = 20) -> None:
    """View recent cost logs"""
    log_file = "./data/cost_log.jsonl"
    
    if not os.path.exists(log_file):
        print("❌ No cost logs found yet.")
        print("💡 Make some queries first to generate telemetry data.")
        return
    
    print("\n" + "=" * 80)
    print("📊 COST TELEMETRY LOGS")
    print("=" * 80)
    
    logs = []
    with open(log_file, "r") as f:
        for line in f:
            try:
                logs.append(json.loads(line))
            except:
                continue
    
    # Show last N logs
    recent_logs = logs[-limit:]
    
    for i, log in enumerate(recent_logs, 1):
        print(f"\n[{i}] {log.get('timestamp', 'N/A')}")
        print(f"    User: {log.get('user_id', 'N/A')}")
        print(f"    Query: {log.get('query', 'N/A')[:60]}...")
        print(f"    Route: {log.get('route', 'N/A')}")
        print(f"    Cost: ${log.get('cost', 0):.4f}")
        print(f"    Tokens: {log.get('tokens_used', {})}")
    
    print("\n" + "-" * 80)
    print(f"Total logs: {len(logs)}")

def view_user_insights() -> None:
    """View user insights"""
    insights_file = "./data/user_insights.json"
    
    if not os.path.exists(insights_file):
        print("❌ No user insights found yet.")
        return
    
    print("\n" + "=" * 80)
    print("🧠 USER INSIGHTS")
    print("=" * 80)
    
    with open(insights_file, "r") as f:
        insights = json.load(f)
    
    for user_id, data in insights.items():
        print(f"\n👤 User: {user_id}")
        print(f"   Interactions: {data.get('interaction_count', 0)}")
        print(f"   First seen: {data.get('first_seen', 'N/A')}")
        print(f"   Last seen: {data.get('last_seen', 'N/A')}")
        
        budget_signals = data.get('budget_signals', [])
        if budget_signals:
            avg_budget = sum(s['amount'] for s in budget_signals) / len(budget_signals)
            print(f"   Avg Budget: ${avg_budget:,.0f}")
        
        locations = data.get('location_interests', [])
        if locations:
            print(f"   Locations: {', '.join(locations)}")
        
        prefs = data.get('preferences', {})
        if prefs:
            print(f"   Preferences: {prefs}")

def view_system_stats() -> None:
    """View system-wide statistics"""
    log_file = "./data/cost_log.jsonl"
    
    if not os.path.exists(log_file):
        print("❌ No statistics available yet.")
        return
    
    print("\n" + "=" * 80)
    print("📈 SYSTEM STATISTICS")
    print("=" * 80)
    
    total_queries = 0
    total_cost = 0.0
    route_counts = {}
    users = set()
    
    with open(log_file, "r") as f:
        for line in f:
            try:
                log = json.loads(line)
                total_queries += 1
                total_cost += log.get('cost', 0)
                route = log.get('route', 'unknown')
                route_counts[route] = route_counts.get(route, 0) + 1
                users.add(log.get('user_id', 'unknown'))
            except:
                continue
    
    print(f"\n📊 Overview:")
    print(f"   Total Queries: {total_queries}")
    print(f"   Unique Users: {len(users)}")
    print(f"   Total Cost: ${total_cost:.4f}")
    print(f"   Avg Cost/Query: ${total_cost/total_queries:.4f}" if total_queries > 0 else "   Avg Cost/Query: $0.0000")
    
    print(f"\n🔀 Route Distribution:")
    for route, count in sorted(route_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_queries * 100) if total_queries > 0 else 0
        print(f"   {route}: {count} ({percentage:.1f}%)")
    
    # Calculate savings
    template_queries = route_counts.get('template', 0)
    tool_queries = route_counts.get('tool', 0)
    optimized_queries = template_queries + tool_queries
    estimated_savings = optimized_queries * 0.02  # Assume $0.02 saved per optimized query
    
    print(f"\n💰 Cost Optimization:")
    print(f"   Optimized Queries: {optimized_queries}")
    print(f"   Estimated Savings: ${estimated_savings:.4f}")
    print(f"   Optimization Rate: {(optimized_queries/total_queries*100):.1f}%" if total_queries > 0 else "   Optimization Rate: 0.0%")

def main():
    """Main telemetry viewer"""
    print("\n" + "=" * 80)
    print("🔍 SNAPHOMZ TELEMETRY VIEWER")
    print("=" * 80)
    
    # Check if data directory exists
    if not os.path.exists("./data"):
        print("\n❌ Data directory not found.")
        print("💡 The telemetry system will create it automatically when you make queries.")
        return
    
    # View all telemetry
    view_system_stats()
    view_cost_logs(limit=10)
    view_user_insights()
    
    print("\n" + "=" * 80)
    print("✅ Telemetry view complete!")
    print("=" * 80)
    print("\n💡 Tip: Make queries in the Streamlit app to see telemetry data populate.")
    print("   Try: 'What is PMI?' (template - FREE)")
    print("   Try: 'Find homes in Austin' (LangGraph - $0.02)")

if __name__ == "__main__":
    main()
