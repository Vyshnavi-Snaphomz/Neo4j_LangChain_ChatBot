from app.neo4j_client import neo4j_client

query = """
MATCH (p:Property)
WHERE p.hdpUrl IS NOT NULL
RETURN p.url AS url, p.hdpUrl AS hdpUrl
LIMIT 5
"""

results = neo4j_client.query(query)
print("URL Check:")
for r in results:
    print(f"URL: {r.get('url')}")
    print(f"HDP URL: {r.get('hdpUrl')}")
    print("-" * 20)
