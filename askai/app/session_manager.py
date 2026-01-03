import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

class SessionManager:
    """
    Manages session persistence using browser localStorage via Streamlit.
    Handles serialization and deserialization of session data.
    """
    
    @staticmethod
    def create_session_data(
        conversation_history: list,
        previous_results: list,
        selected_properties: list = None,
        filters: dict = None
    ) -> Dict[str, Any]:
        """Create a serializable session data structure."""
        return {
            "session_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "conversation_history": conversation_history,
            "previous_results": previous_results,
            "selected_properties": selected_properties or [],
            "filters": filters or {
                "price_min": 0,
                "price_max": 2000000,
                "beds": None,
                "baths": None,
                "sort_by": "price_asc"
            }
        }
    
    @staticmethod
    def serialize_session(data: Dict[str, Any]) -> str:
        """Serialize session data to JSON string."""
        return json.dumps(data, default=str)
    
    @staticmethod
    def deserialize_session(json_str: str) -> Optional[Dict[str, Any]]:
        """Deserialize JSON string to session data."""
        try:
            return json.loads(json_str)
        except (json.JSONDecodeError, TypeError):
            return None
    
    @staticmethod
    def get_localStorage_save_script(data: Dict[str, Any]) -> str:
        """Generate JavaScript to save data to localStorage."""
        json_data = SessionManager.serialize_session(data)
        return f"""
        <script>
        try {{
            localStorage.setItem('agent_session', '{json_data}');
            console.log('Session saved to localStorage');
        }} catch(e) {{
            console.error('Error saving session:', e);
        }}
        </script>
        """
    
    @staticmethod
    def get_localStorage_load_script() -> str:
        """Generate JavaScript to load data from localStorage."""
        return """
        <script>
        try {
            const session = localStorage.getItem('agent_session');
            if (session) {
                // Send session data to Streamlit
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    data: session
                }, '*');
                console.log('Session loaded from localStorage');
            }
        } catch(e) {
            console.error('Error loading session:', e);
        }
        </script>
        """
