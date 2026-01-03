from datetime import datetime
import uuid
from typing import List, Dict, Any
from app.neo4j_client import neo4j_client

class SessionManager:
    """
    Manages chat session persistence in Neo4j.
    Schema:
    (:User {userId: str}) -[:HAS_SESSION]-> (:Session {sessionId: str, createdAt: datetime}) 
    (:Session) -[:HAS_MESSAGE]-> (:Message {role: str, content: str, timestamp: datetime})
    """
    
    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        
    def create_session(self) -> str:
        """Create a new session node for the user."""
        session_id = str(uuid.uuid4())
        cypher = """
        MERGE (u:User {userId: $user_id})
        CREATE (s:Session {sessionId: $session_id, createdAt: datetime(), title: 'New Chat'})
        CREATE (u)-[:HAS_SESSION]->(s)
        RETURN s.sessionId
        """
        neo4j_client.write_query(cypher, {"user_id": self.user_id, "session_id": session_id})
        return session_id
        
    def save_message(self, session_id: str, role: str, content: str):
        """Save a message to the session."""
        cypher = """
        MATCH (s:Session {sessionId: $session_id})
        CREATE (m:Message {
            role: $role, 
            content: $content, 
            timestamp: datetime()
        })
        CREATE (s)-[:HAS_MESSAGE]->(m)
        """
        neo4j_client.write_query(cypher, {
            "session_id": session_id,
            "role": role,
            "content": content
        })
        
    def update_session_title(self, session_id: str, title: str):
        """Update the title of a session (e.g., using first user message)."""
        cypher = """
        MATCH (s:Session {sessionId: $session_id})
        SET s.title = $title
        """
        neo4j_client.write_query(cypher, {"session_id": session_id, "title": title})

    def get_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """Retrieve all messages for a session, ordered by time."""
        cypher = """
        MATCH (s:Session {sessionId: $session_id})-[:HAS_MESSAGE]->(m:Message)
        RETURN m.role as role, m.content as content
        ORDER BY m.timestamp ASC
        """
        return neo4j_client.query(cypher, {"session_id": session_id})

    def save_context(self, session_id: str, context_key: str, context_data: Any):
        """Save a context object (like search results) to the session."""
        import json
        cypher = """
        MATCH (s:Session {sessionId: $session_id})
        SET s.""" + context_key + """ = $data
        """
        neo4j_client.write_query(cypher, {
            "session_id": session_id,
            "data": json.dumps(context_data)
        })

    def get_context(self, session_id: str, context_key: str) -> Any:
        """Retrieve a context object from the session."""
        import json
        cypher = """
        MATCH (s:Session {sessionId: $session_id})
        RETURN s.""" + context_key + """ as data
        """
        results = neo4j_client.query(cypher, {"session_id": session_id})
        if results and results[0]["data"]:
            return json.loads(results[0]["data"])
        return None

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions for the user, ordered by newest first."""
        cypher = """
        MATCH (u:User {userId: $user_id})-[:HAS_SESSION]->(s:Session)
        RETURN s.sessionId as id, s.title as title, s.createdAt as createdAt
        ORDER BY s.createdAt DESC
        """
        return neo4j_client.query(cypher, {"user_id": self.user_id})

    def delete_session(self, session_id: str):
        """Delete a session and its messages."""
        cypher = """
        MATCH (s:Session {sessionId: $session_id})
        OPTIONAL MATCH (s)-[:HAS_MESSAGE]->(m)
        DETACH DELETE s, m
        """
        neo4j_client.write_query(cypher, {"session_id": session_id})
