from app.neo4j_client import neo4j_client

query = """
MATCH (p:Property)
WHERE p.description IS NOT NULL
RETURN p.state, p.city, substring(p.description, 0, 50) as desc_start, size(p.description) as len
LIMIT 5
"""

results = neo4j_client.query(query)
print(f"Found {len(results)} properties with description")
for r in results:
    print(r)
