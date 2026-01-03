import sys
import traceback
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

try:
    from app.graph import graph
    
    # Test query: "houses in CA"
    test_query = "houses in CA"
    
    initial_state = {
        "messages": [("user", test_query)],
        "extracted_entities": {},
        "generated_cypher": None,
        "search_results": [],
        "plan": None,
        "intent": None
    }
    
    print(f"Testing query: '{test_query}'")
    print("=" * 60)
    
    # Stream the graph execution
    for event in graph.stream(initial_state):
        for key, value in event.items():
            print(f"\nNode: {key}")
            
            # Print relevant state information
            if key == "Entity_Extractor":
                print(f"Extracted Entities: {value.get('extracted_entities', {})}")
            elif key == "Neo4j_Search":
                results = value.get('search_results', [])
                print(f"Search Results Count: {len(results)}")
                if results:
                    print("Sample Results:")
                    for i, result in enumerate(results[:3], 1):
                        print(f"  {i}. Price: ${result.get('price')}, Score: {result.get('score', 'N/A')}")
            elif key == "Final_Response":
                messages = value.get('messages', [])
                if messages:
                    print(f"Final Response: {messages[-1][1]}")
    
    print("\n" + "=" * 60)
    print("Test completed successfully!")
    
except Exception as e:
    print(f"\nERROR: {str(e)}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
