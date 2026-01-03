from app.neo4j_client import neo4j_client
import json

# Query to get ALL keys from the first 5 Property nodes
query = """
MATCH (p:Property)
RETURN keys(p) as property_keys, p.description as desc_val, p.embedding_text as emb_text_val
LIMIT 5
"""

results = neo4j_client.query(query)

print(f"Found {len(results)} properties. analyzing keys...")

all_keys = set()
for i, r in enumerate(results):
    keys = r.get('property_keys', [])
    all_keys.update(keys)
    print(f"\n--- Property {i+1} ---")
    print(f"Keys: {keys}")
    print(f"Description present: {'description' in keys}")
    print(f"Description value (first 50 chars): {str(r.get('desc_val', ''))[:50]}")
    # Check for case sensitivity
    for k in keys:
        if k.lower() == 'description':
            print(f"Found description-like key: '{k}'")

print("\n\n=== UNIQUE KEYS FOUND ACROSS SAMPLES ===")
print(sorted(list(all_keys)))
