import os
from dotenv import load_dotenv
from app.graph import graph

load_dotenv()

def main():
    print("Real-Estate AI Agent Started (Type 'quit' to exit)")
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit"]:
            break
        
        initial_state = {
            "messages": [("user", user_input)],
            "extracted_entities": {},
            "generated_cypher": None,
            "search_results": [],
            "plan": None,
            "intent": None,
            "final_response": None,
            "conversation_history": [],
            "previous_results": None
        }
        
        # Stream the graph execution
        for event in graph.stream(initial_state):
            for key, value in event.items():
                print(f"Finished Node: {key}")
                # print(f"Output: {value}") # Debug only

if __name__ == "__main__":
    main()
