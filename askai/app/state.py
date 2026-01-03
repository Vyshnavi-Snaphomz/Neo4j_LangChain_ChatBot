from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    messages: List[Any]
    extracted_entities: Dict[str, Any]
    generated_cypher: Optional[str]
    search_results: List[Dict[str, Any]]
    plan: Optional[str]
    intent: Optional[str]
    final_response: Optional[str]
    conversation_history: List[Dict[str, str]]
    previous_results: Optional[List[Dict[str, Any]]]  # Store last search results for reference

