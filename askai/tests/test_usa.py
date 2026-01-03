from app.state import AgentState
from app.nodes.search import neo4j_search

# Test "USA" search (should behave as broad search)
# Extractor should have returned empty entities for "USA" input
state = {
    "extracted_entities": {} 
}

print("Testing broad search (simulating 'USA' input)...")
result = neo4j_search(state)
results = result['search_results']

print(f"\nFound {len(results)} results")
for i, r in enumerate(results[:3], 1):
    print(f"Prop {i}: {r.get('state')} - {r.get('price')}")
