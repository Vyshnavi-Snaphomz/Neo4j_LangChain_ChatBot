from dotenv import load_dotenv
load_dotenv()

from app.neo4j_client import neo4j_client

# Test the exact query that should work
print("Testing direct Cypher query for Texas under 500k...")

query = """
MATCH (p:Property)
WHERE (p.state = $state OR p.state = $state_abbrev) AND p.price <= $max_price
RETURN p.price AS price, p.state AS state, p.embedding_text AS details
LIMIT 20
"""

params = {
    "state": "Texas",
    "state_abbrev": "TX",
    "max_price": 500000
}

results = neo4j_client.query(query, params)

print(f"\nResults found: {len(results)}")

if results:
    print("\nSample results:")
    for i, r in enumerate(results[:5], 1):
        print(f"\n{i}. Price: ${r.get('price')}")
        print(f"   State: {r.get('state')}")
        print(f"   Details: {r.get('details', '')[:100]}...")
else:
    print("\nNo results - checking what's wrong...")
    
    # Check if Texas properties exist
    check_query = "MATCH (p:Property) WHERE p.state = 'Texas' OR p.state = 'TX' RETURN count(p) AS count"
    count_result = neo4j_client.query(check_query)
    print(f"Texas properties in database: {count_result[0]['count'] if count_result else 0}")
    
    # Check price range
    price_check = "MATCH (p:Property) WHERE p.price <= 500000 RETURN count(p) AS count"
    price_result = neo4j_client.query(price_check)
    print(f"Properties under 500k: {price_result[0]['count'] if price_result else 0}")

neo4j_client.close()
