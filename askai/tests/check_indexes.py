from dotenv import load_dotenv
load_dotenv()

from app.neo4j_client import neo4j_client

# Check if index exists
result = neo4j_client.query("SHOW INDEXES")
print("Current indexes:")
for r in result:
    name = r.get('name', 'N/A')
    index_type = r.get('type', 'N/A')
    print(f"  - {name}: {index_type}")
    
# Check specifically for vector index
vector_check = neo4j_client.query("SHOW INDEXES YIELD name WHERE name = 'property_embedding_index' RETURN name")
if vector_check:
    print("\n✓ Vector index 'property_embedding_index' EXISTS")
else:
    print("\n✗ Vector index 'property_embedding_index' DOES NOT EXIST")

neo4j_client.close()
