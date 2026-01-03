from app.neo4j_client import neo4j_client

# Debug query to find "Nevada" properties and check their description status
query = """
MATCH (p:Property)
WHERE (p.state = 'NV' OR p.state = 'Nevada')
RETURN p.price, p.state, p.description, p.embedding_text
LIMIT 10
"""

results = neo4j_client.query(query)

print(f"Found {len(results)} properties in Nevada.")
for i, r in enumerate(results, 1):
    desc = r.get('description')
    emb_text = r.get('embedding_text')
    print(f"\nProperty #{i}:")
    print(f"  Price: {r.get('price')}")
    print(f"  Description: {desc if desc else 'NONE'}")
    print(f"  Embedding Text (first 50): {str(emb_text)[:50] if emb_text else 'NONE'}")
    
    # Simulate softener logic
    final_desc = desc
    if not final_desc:
        final_desc = emb_text
    
    if final_desc and "for_sale" in final_desc and not desc:
         pass # Logic from softener
         
    print(f"  > Softener would show: {bool(final_desc)}")
