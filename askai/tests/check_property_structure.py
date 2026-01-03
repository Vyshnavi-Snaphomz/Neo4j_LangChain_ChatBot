from dotenv import load_dotenv
load_dotenv()

from app.neo4j_client import neo4j_client

# Check what properties exist on Property nodes
print("Checking Property node structure...")
result = neo4j_client.query("MATCH (p:Property) RETURN keys(p) AS keys LIMIT 1")
if result:
    print(f"Available properties: {result[0]['keys']}")

# Check for state data
print("\nChecking state data...")
state_result = neo4j_client.query("MATCH (p:Property) WHERE p.state IS NOT NULL RETURN DISTINCT p.state AS state ORDER BY state LIMIT 20")
if state_result:
    print("States found:")
    for r in state_result:
        print(f"  - {r['state']}")
else:
    print("  No state data found")

# Check a sample property
print("\nSample property:")
sample = neo4j_client.query("MATCH (p:Property) RETURN p LIMIT 1")
if sample:
    prop = sample[0]['p']
    for key, value in prop.items():
        if key not in ['embedding', 'embedding_text']:
            print(f"  {key}: {value}")

neo4j_client.close()
