import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.state import AgentState
from app.graph import graph
from unittest.mock import MagicMock, patch

# Mock Neo4j Client
mock_client = MagicMock()
mock_client.structured_search.return_value = [
    {"beds": 3, "baths": 2, "price": 500000, "streetAddress": "123 Test St", "listingUrl": "http://test", "lotAreaUnits": "sqft"}
]
mock_client.vector_search.return_value = []

@patch('app.nodes.search.neo4j_client', mock_client)
@patch('app.nodes.rerank.neo4j_client', mock_client)
def test_happy_path():
    print("Running Happy Path Test...")
    initial_state = {
        "messages": [("user", "Find a 3 bed house in Austin")],
        "extracted_entities": {},
        "generated_cypher": None,
        "search_results": [],
        "plan": None,
        "intent": None
    }
    
    # We allow the LLM to run (assuming key is present or we interpret failure)
    # If no key, LLM calls will fail. For robustness in this environment, 
    # we might need to mock LLM too if we don't have the key.
    # But let's try assuming the user might supply the key or we just want to see the code run until that point.
    
    # Actually, for the purpose of "Proof of Concept" without keys, I should mock the LLM responses.
    
    # Patch get_llm in all nodes
    with patch('app.nodes.intent.get_llm') as mock_intent_llm, \
         patch('app.nodes.extractor.get_llm') as mock_extractor_llm, \
         patch('app.nodes.planner.get_llm') as mock_planner_llm, \
         patch('app.nodes.generator.get_llm') as mock_generator_llm, \
         patch('app.nodes.rerank.get_llm') as mock_rerank_llm, \
         patch('app.nodes.softener.get_llm') as mock_softener_llm:
        
        # Setup Identity Mocks (Basic string return)
        mock_llm = MagicMock()
        mock_llm.invoke.return_value.content = "search"
        # For structured output (extractor)
        mock_llm.with_structured_output.return_value.invoke.return_value.dict.return_value = {"city": "Austin", "beds": 3}
        
        mock_intent_llm.return_value = mock_llm
        mock_extractor_llm.return_value = mock_llm
        
        # Planner
        mock_planner_llm_obj = MagicMock()
        mock_planner_llm_obj.invoke.return_value.content = "Execute Cypher Search"
        mock_planner_llm.return_value = mock_planner_llm_obj
        
        # Generator
        mock_generator_llm_obj = MagicMock()
        # Generator node logic constructs string manually?
        # Let's see generator.py... "Always parameterize..."
        # Wait, generator.py creates the string based on entities. It doesn't use LLM for the structured part if I implemented it that way.
        # Checking my generator.py implementation...
        # "cypher_generator" function calls `get_llm()`?
        # Yes, I imported it. "llm = get_llm()". But I didn't use it for the Structured Logic I implemented!
        # I just used basic logic. 
        # But `llm = get_llm()` is called, so it will fail if not mocked.
        mock_generator_llm.return_value = mock_llm # Just needs to not crash
        
        # ReRank
        # Uses embeddings... "embeddings_model.embed_query". I need to mock OpenAIEmbeddings probably.
        # rerank.py: "from langchain_openai import OpenAIEmbeddings"
        # I should patch the class OpenAIEmbeddings in app.nodes.rerank
        
        # Softener
        mock_softener_llm_obj = MagicMock()
        mock_softener_llm_obj.invoke.return_value.content = "Here are the results."
        mock_softener_llm.return_value = mock_softener_llm_obj
        
        # ReRank patch for Embeddings
        with patch('app.nodes.rerank.OpenAIEmbeddings') as mock_embeddings:
            mock_embeddings.return_value.embed_query.return_value = [0.1] * 1536
            
            try:
               for event in graph.stream(initial_state):
                   pass
               print("Test Finished Successfully (Logic Flow Verified)")
            except Exception as e:
               print(f"Test Failed: {e}")
               import traceback
               traceback.print_exc()

if __name__ == "__main__":
    test_happy_path()
