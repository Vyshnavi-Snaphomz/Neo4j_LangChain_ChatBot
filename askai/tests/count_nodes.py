from app.neo4j_client import neo4j_client

query = """
MATCH (p:Property)
RETURN count(p) as total_nodes, 
       count(p.description) as nodes_with_description,
       count(p.embedding_text) as nodes_with_embedding_text
"""

results = neo4j_client.query(query)
print("Database Statistics:")
print(f"Total Property Nodes: {results[0]['total_nodes']:,}")
print(f"Nodes with Description: {results[0]['nodes_with_description']:,}")
print(f"Nodes with Embedding Text: {results[0]['nodes_with_embedding_text']:,}")
