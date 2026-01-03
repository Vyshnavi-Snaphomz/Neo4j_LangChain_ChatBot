from app.state import AgentState
from app.nodes.search import neo4j_search

# Mock state
state = {
    "extracted_entities": {
        "state": "CA",
        "keywords": ["modern"]
    }
}

print("Testing search priorities...")
result = neo4j_search(state)
results = result['search_results']

print(f"\nFound {len(results)} results")
for i, r in enumerate(results):
    has_desc = bool(r.get('description'))
    desc_len = len(r.get('description', ''))
    print(f"Prop {i+1}: Price=${r.get('price')}, HasDesc={has_desc} (len={desc_len})")
