from dotenv import load_dotenv
load_dotenv()

import sys
import traceback

try:
    print("Testing Cypher-only search with 'houses in CA'...")
    from app.nodes.search import neo4j_search
    
    search_state = {
        "messages": [("user", "houses in CA")],
        "extracted_entities": {"state": "California"},
        "generated_cypher": None,
        "search_results": [],
        "plan": None,
        "intent": "search"
    }
    
    result = neo4j_search(search_state)
    results = result.get('search_results', [])
    
    print(f"\n✓ Search completed!")
    print(f"  Results found: {len(results)}")
    
    if results:
        print("\nSample results:")
        for i, r in enumerate(results[:5], 1):
            state = r.get('state', 'N/A')
            city = r.get('city', 'N/A')
            price = r.get('price', 'N/A')
            beds = r.get('beds', 'N/A')
            baths = r.get('baths', 'N/A')
            print(f"  {i}. {state}, {city} - ${price} - {beds}bed/{baths}bath")
    else:
        print("\n✗ No results found")
    
    print("\n✓ Test completed successfully!")
    
except Exception as e:
    print(f"\n✗ ERROR: {str(e)}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
