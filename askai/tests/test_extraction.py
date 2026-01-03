from app.state import AgentState
from app.nodes.extractor import entity_extractor

# Test cases
queries = [
    "hill top houses in the usa",
    "houses i ca",  # Typos
    "houses in ca", # Clean
    "usa"
]

print("Testing Entity Extractor...")
for q in queries:
    state = {
        "messages": [("user", q)],
        "conversation_history": []
    }
    try:
        result = entity_extractor(state)
        print(f"\nQuery: '{q}'")
        print(f"Extracted: {result['extracted_entities']}")
    except Exception as e:
        print(f"\nQuery: '{q}' -> ERROR: {e}")
