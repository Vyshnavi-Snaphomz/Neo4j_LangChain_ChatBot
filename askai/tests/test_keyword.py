from app.state import AgentState
from app.nodes.search import neo4j_search

# Test "hill top" keyword search
state = {
    "extracted_entities": {
        "keywords": ["hill top"]
    }
}

print("Testing 'hill top' keyword search...")
result = neo4j_search(state)
results = result['search_results']

print(f"\nFound {len(results)} results")
for i, r in enumerate(results, 1):
    desc = r.get('description', '')
    emb = r.get('embedding_text', '')
    print(f"Prop {i}: Found keyword in desc? {'hill top' in desc.lower()} | Found in embedding? {'hill top' in emb.lower()}")
