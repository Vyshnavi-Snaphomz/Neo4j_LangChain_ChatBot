from app.state import AgentState
from app.nodes.search import neo4j_search

# Test cases for state matching
queries = [
    {"state": "Texas", "keywords": []}, 
    {"state": "New York", "keywords": []} 
]

print("Testing State Search Fix...")
for entities in queries:
    state = {"extracted_entities": entities}
    print(f"\nSearching for entities: {entities}")
    
    result = neo4j_search(state)
    results = result['search_results']
    
    print(f"Found {len(results)} results")
    if results:
        print(f"First result State: {results[0].get('state')}")
    else:
        print("FAIL: No results found.")
