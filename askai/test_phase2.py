"""
Test script for Phase 2 Smart Routing Integration
"""

from app.agent_wrapper import AgentWrapper

def test_smart_routing():
    """Test smart routing with template responses"""
    
    print("=" * 60)
    print("PHASE 2: SMART ROUTING TEST")
    print("=" * 60)
    
    # Initialize agent
    agent = AgentWrapper(user_id="test_user")
    
    # Test 1: Template response (FREE)
    print("\n📝 Test 1: Template Response (FREE)")
    print("-" * 60)
    query1 = "What is PMI?"
    print(f"Query: {query1}")
    response1 = agent.chat(query1)
    print(f"\nResponse:\n{response1}\n")
    
    # Test 2: Another template (FREE)
    print("\n📝 Test 2: Another Template (FREE)")
    print("-" * 60)
    query2 = "What is HOA?"
    print(f"Query: {query2}")
    response2 = agent.chat(query2)
    print(f"\nResponse:\n{response2}\n")
    
    # Test 3: Regular query (LangGraph)
    print("\n🔍 Test 3: Regular Query (LangGraph)")
    print("-" * 60)
    query3 = "Find homes in Austin under 500k"
    print(f"Query: {query3}")
    response3 = agent.chat(query3)
    print(f"\nResponse:\n{response3[:200]}...\n")
    
    # Get cost stats
    print("\n💰 COST STATISTICS")
    print("=" * 60)
    stats = agent.cost_tracker.get_user_stats("test_user")
    print(f"Total Queries: {stats['total_queries']}")
    print(f"Total Cost: ${stats['total_cost']}")
    print(f"Avg Cost/Query: ${stats['avg_cost_per_query']}")
    print(f"Route Distribution: {stats['route_distribution']}")
    
    # Get insights
    print("\n🧠 USER INSIGHTS")
    print("=" * 60)
    insights = agent.insights.get_user_insights("test_user")
    if insights:
        print(f"Interaction Count: {insights['interaction_count']}")
        print(f"Location Interests: {insights['location_interests']}")
        print(f"Preferences: {insights['preferences']}")
    
    print("\n✅ PHASE 2 INTEGRATION TEST COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    test_smart_routing()
