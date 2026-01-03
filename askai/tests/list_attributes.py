from app.neo4j_client import neo4j_client

# Sample 1000 nodes to catch sparse properties
query = """
MATCH (p:Property)
UNWIND keys(p) as key
RETURN distinct key
ORDER BY key
"""

results = neo4j_client.query(query)
with open("attributes.txt", "w") as f:
    f.write("Dataset Attributes (Columns):\n")
    for r in results:
        f.write(f"- {r['key']}\n")
