from app.neo4j_client import neo4j_client
import json

query = """
MATCH (p:Property)
WHERE p.description IS NOT NULL
RETURN properties(p) as props
LIMIT 1
"""

results = neo4j_client.query(query)

if results:
    props = results[0]['props']
    # Remove embedding for readability
    if 'embedding' in props:
        props['embedding'] = "(vector hidden)"
    print(json.dumps(props, indent=2, default=str))
else:
    print("No rich nodes found.")
