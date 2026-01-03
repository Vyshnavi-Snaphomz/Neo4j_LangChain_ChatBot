import sys
import traceback
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

try:
    print("Testing entity extractor...")
    from app.nodes.extractor import entity_extractor
    from app.state import AgentState
    
    state = {
        "messages": [("user", "houses in CA")],
        "extracted_entities": {},
        "generated_cypher": None,
        "search_results": [],
        "plan": None,
        "intent": "search"
    }
    
    result = entity_extractor(state)
    print(f"✓ Entity Extractor Result: {result}")
    
    print("\nTesting search with vector search...")
    from app.nodes.search import neo4j_search
    
    search_state = {
        "messages": [("user", "houses in CA")],
        "extracted_entities": {"state": "California"},
        "generated_cypher": None,
        "search_results": [],
        "plan": None,
        "intent": "search"
    }
    
    search_result = neo4j_search(search_state)
    print(f"✓ Search Result Count: {len(search_result.get('search_results', []))}")
    
    if search_result.get('search_results'):
        print("Sample results:")
        for i, r in enumerate(search_result['search_results'][:3], 1):
            print(f"  {i}. Price: ${r.get('price')}, Score: {r.get('score', 'N/A')}")
    
    print("\n✓ All component tests passed!")
    
except Exception as e:
    print(f"\n✗ ERROR: {str(e)}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
