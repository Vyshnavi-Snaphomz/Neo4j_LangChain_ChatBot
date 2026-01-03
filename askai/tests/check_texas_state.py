from dotenv import load_dotenv
load_dotenv()

from app.neo4j_client import neo4j_client

# Check what state values exist for Texas
print("Checking Texas state values in database...")

query = "MATCH (p:Property) WHERE p.state CONTAINS 'T' RETURN DISTINCT p.state AS state ORDER BY state LIMIT 20"
results = neo4j_client.query(query)

print("\nStates containing 'T':")
for r in results:
    print(f"  - {r['state']}")

# Check specifically for TX
tx_query = "MATCH (p:Property) WHERE p.state = 'TX' RETURN count(p) AS count"
tx_result = neo4j_client.query(tx_query)
print(f"\nProperties with state='TX': {tx_result[0]['count'] if tx_result else 0}")

# Check for Texas
texas_query = "MATCH (p:Property) WHERE p.state = 'Texas' RETURN count(p) AS count"
texas_result = neo4j_client.query(texas_query)
print(f"Properties with state='Texas': {texas_result[0]['count'] if texas_result else 0}")

neo4j_client.close()
