from app.state import AgentState
from app.nodes.search import neo4j_search

# Test state for Nevada search
state = {
    "extracted_entities": {
        "state": "NV"
    }
}

print("Testing search with strict filters...")
result = neo4j_search(state)
results = result['search_results']

print(f"\nFound {len(results)} results")
for i, r in enumerate(results, 1):
    desc = r.get('description')
    emb = r.get('embedding_text')
    
    print(f"\nProperty #{i}:")
    print(f"  Price: {r.get('price')}")
    print(f"  Description present: {bool(desc)}")
    print(f"  Embedding Text present: {bool(emb)}")
    
    # Verification check
    if not desc and (not emb or len(emb) <= 20):
        print("  FAIL: This node should have been filtered out!")
    else:
        print("  PASS: Node has valid description content.")
