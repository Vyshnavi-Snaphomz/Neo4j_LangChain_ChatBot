from app.neo4j_client import neo4j_client

# Check distinct state values to see if they are codes (TX) or names (Texas)
query = """
MATCH (p:Property)
RETURN distinct p.state as state
LIMIT 50
"""

results = neo4j_client.query(query)
print("Distinct States in DB:")
states = [r['state'] for r in results]
print(states)

# Check specifically for Texas and New York
query_specific = """
MATCH (p:Property)
WHERE p.state IN ['TX', 'Texas', 'NY', 'New York', 'FL', 'Florida', 'NJ', 'New Jersey']
RETURN distinct p.state as state, count(p) as count
"""
results_specific = neo4j_client.query(query_specific)
print("\nSpecific State Counts:")
for r in results_specific:
    print(f"{r['state']}: {r['count']}")
