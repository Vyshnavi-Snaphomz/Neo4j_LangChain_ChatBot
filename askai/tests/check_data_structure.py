from dotenv import load_dotenv
load_dotenv()

from app.neo4j_client import neo4j_client

# Check what labels exist
print("Checking node labels...")
result = neo4j_client.query("MATCH (n) RETURN DISTINCT labels(n) AS labels LIMIT 10")
for r in result:
    print(f"  Labels: {r['labels']}")

# Check if Property nodes exist
print("\nChecking for Property nodes...")
prop_count = neo4j_client.query("MATCH (p:Property) RETURN count(p) AS count")
if prop_count:
    print(f"  Property nodes: {prop_count[0]['count']}")
    
    # Check if they have embedding field
    embedding_check = neo4j_client.query("MATCH (p:Property) WHERE p.embedding IS NOT NULL RETURN count(p) AS count")
    if embedding_check:
        print(f"  Properties with embedding: {embedding_check[0]['count']}")

neo4j_client.close()
