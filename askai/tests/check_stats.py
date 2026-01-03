from app.neo4j_client import neo4j_client

# Check count of properties with description
query_count = """
MATCH (p:Property)
RETURN count(p) as total, 
       count(p.description) as with_desc, 
       count(p.zpid) as with_zpid,
       count(p.embedding_text) as with_emb
"""

results = neo4j_client.query(query_count)
print("Content Stats:")
print(results)

# If description exists, show one
if results[0]['with_desc'] > 0:
    query_sample = """
    MATCH (p:Property)
    WHERE p.description IS NOT NULL
    RETURN p.description as desc, keys(p) as all_keys
    LIMIT 1
    """
    sample = neo4j_client.query(query_sample)
    print("\nSample with Description Keys:")
    print(sample[0]['all_keys'])
else:
    print("\nNO NODES FOUND WITH 'description' PROPERTY!")
