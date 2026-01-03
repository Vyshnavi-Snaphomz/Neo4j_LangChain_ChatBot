from dotenv import load_dotenv
load_dotenv()

from app.neo4j_client import neo4j_client

# Get all property keys from a sample
print("Checking ALL properties on Property nodes...")
result = neo4j_client.query("MATCH (p:Property) WITH p LIMIT 1 UNWIND keys(p) AS key RETURN DISTINCT key ORDER BY key")
print("\nAll available properties:")
for r in result:
    print(f"  - {r['key']}")

# Get a full sample property
print("\n\nSample Property (full details):")
sample = neo4j_client.query("MATCH (p:Property) RETURN p LIMIT 1")
if sample:
    prop = sample[0]['p']
    for key, value in sorted(prop.items()):
        if key not in ['embedding']:
            value_str = str(value)[:100] if value else 'None'
            print(f"  {key}: {value_str}")

neo4j_client.close()
