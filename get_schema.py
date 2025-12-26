import toml
from langchain_neo4j import Neo4jGraph

def get_schema():
    """
    Get the schema of the graph.
    """
    # Load secrets from secrets.toml
    secrets = toml.load(".streamlit/secrets.toml")

    # Get Neo4j connection details
    url = secrets.get("NEO4J_URI")
    username = secrets.get("NEO4J_USERNAME")
    password = secrets.get("NEO4J_PASSWORD")
    database = secrets.get("NEO4J_DATABASE", "neo4j")

    if not all([url, username, password]):
        raise ValueError("NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD must be set in .streamlit/secrets.toml")

    # Create Neo4jGraph object
    graph = Neo4jGraph(
        url=url,
        username=username,
        password=password,
        database=database,
    )

    schema = graph.schema
    print(schema)

if __name__ == "__main__":
    get_schema()