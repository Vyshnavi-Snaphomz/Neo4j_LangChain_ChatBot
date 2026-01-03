from app.neo4j_client import neo4j_client
import json

# Get sample properties
result = neo4j_client.query('MATCH (p:Property) RETURN p.embedding_text AS text, p.price AS price LIMIT 5')
print("Sample Properties:")
for i, r in enumerate(result, 1):
    print(f"\n{i}. Price: ${r['price']}")
    print(f"   Text: {r['text']}")

neo4j_client.close()
