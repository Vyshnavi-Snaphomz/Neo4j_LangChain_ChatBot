import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from typing import List, Dict, Any, Optional

# Load environment variables from .env file
load_dotenv()

class Neo4jClient:
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        username = os.getenv("NEO4J_USERNAME", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        # Add robust connection settings
        self.driver = GraphDatabase.driver(
            uri, 
            auth=(username, password),
            max_connection_lifetime=300,  # Refresh connections every 5 mins
            keep_alive=True
        )

    def close(self):
        self.driver.close()

    def query(self, cypher: str, params: Dict[str, Any] = {}) -> List[Dict[str, Any]]:
        with self.driver.session() as session:
            # Use execute_read for automatic retries of transient network errors
            try:
                return session.execute_read(
                    lambda tx: [record.data() for record in tx.run(cypher, params)]
                )
            except Exception as e:
                print(f"Neo4j Query Error: {e}")
                raise e

    def structured_search(self, cypher: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Enforce safety: Read transactions only could be better but run() is fine for now
        return self.query(cypher, params)

    def vector_search(self, embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        cypher = """
        CALL db.index.vector.queryNodes(
          'property_embedding_index',
          $topK,
          $embedding
        )
        YIELD node, score
        RETURN
          node.beds AS beds,
          node.baths AS baths,
          node.price AS price,
          node.streetAddress AS address,
          node.listingUrl AS listingUrl,
          node.lotAreaUnits AS lotAreaUnits,
          score
        ORDER BY score DESC
        """
        return self.query(cypher, {"embedding": embedding, "topK": top_k})

# Singleton instance
neo4j_client = Neo4jClient()
