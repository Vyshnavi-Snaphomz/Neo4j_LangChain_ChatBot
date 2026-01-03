from dotenv import load_dotenv
load_dotenv()

import sys
import traceback

try:
    print("Testing updated search with 'houses in Texas with 3 beds'...")
    from app.nodes.search import neo4j_search
    
    search_state = {
        "messages": [("user", "houses in Texas with 3 beds")],
        "extracted_entities": {"state": "Texas", "beds": 3},
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
            price = r.get('price', 'N/A')
            state = r.get('state', 'N/A')
            details = r.get('details', 'N/A')
            print(f"\n{i}. Price: ${price}")
            print(f"   State: {state}")
            print(f"   Details: {details[:100]}...")
    else:
        print("\n✗ No results found")
    
    print("\n✓ Test completed successfully!")
    
except Exception as e:
    print(f"\n✗ ERROR: {str(e)}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
