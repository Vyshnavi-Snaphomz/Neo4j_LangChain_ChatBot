from app.neo4j_client import neo4j_client

def setup_constraints():
    # Enforce uniqueness for property ZPID or similar if needed
    # Ignoring for now as per minimal schema instructions, but good practice.
    pass

def setup_vector_index():
    # Create vector index for property descriptions or combined text
    # The prompt expects 'property_embedding_index'
    
    # We need to drop if exists to be safe or create if not exists
    # Neo4j 5.x syntax
    cypher_check = "SHOW INDEXES YIELD name WHERE name = 'property_embedding_index' RETURN name"
    if neo4j_client.query(cypher_check):
        print("Index 'property_embedding_index' already exists.")
        return

    # Assuming 'Property' nodes have an 'embedding' property
    # Dimensions: OpenAI text-embedding-3-small is 1536
    cypher_create = """
    CREATE VECTOR INDEX property_embedding_index IF NOT EXISTS
    FOR (p:Property)
    ON (p.embedding)
    OPTIONS {indexConfig: {
      `vector.dimensions`: 1536,
      `vector.similarity_function`: 'cosine'
    }}
    """
    try:
        neo4j_client.query(cypher_create)
        print("Created vector index 'property_embedding_index'.")
    except Exception as e:
        print(f"Error creating index: {e}")

if __name__ == "__main__":
    setup_vector_index()
    neo4j_client.close()
